"""Footage Finder — search for real stock footage to match each scene in the script.

Uses web search to find actual footage on free and paid platforms for every
major scene. Returns direct search links + specific clip URLs where found.
"""

import json
import re
from .client import get_client, MODEL, MAX_TOKENS
from .projects import load_stage, save_stage
from .elevenlabs_export import _strip_script

SYSTEM = """You are a video producer and stock footage researcher.
Your job is to find real footage that matches scenes in a YouTube script.

You know the major stock footage platforms:
FREE:
  - Pexels Videos: pexels.com/videos — search URL: pexels.com/search/videos/{query}/
  - Pixabay: pixabay.com/videos — search URL: pixabay.com/videos/search/{query}/
  - Coverr: coverr.co — search URL: coverr.co/search?q={query}
  - Mixkit: mixkit.co/free-stock-video/{query}/
  - Videvo: videvo.net — search URL: videvo.net/stock-video-footage/{query}/

PAID (higher quality):
  - Storyblocks: storyblocks.com/video/search?term={query}
  - Shutterstock: shutterstock.com/search/{query}?videotype=footage
  - Pond5: pond5.com/stock-footage/clip/{query}
  - Getty: gettyimages.com/videos/{query}

For each scene you:
1. Identify the most specific search query that will find real footage
2. Provide a direct search URL on the best-fit free platform
3. Suggest 2-3 alternative search queries if the first is too specific
4. Note whether real footage is likely available or if AI generation is better"""


def _extract_scene_needs(script_text: str, spoken_text: str) -> str:
    """Extract visual moments from the script that need footage."""
    # Pull B-ROLL and VISUAL tags from the full script
    broll = re.findall(r'\[B-ROLL:\s*([^\]]+)\]', script_text, re.IGNORECASE)
    visuals = re.findall(r'\[VISUAL:\s*([^\]]+)\]', script_text, re.IGNORECASE)
    return "\n".join(
        [f"B-ROLL: {b}" for b in broll[:15]] +
        [f"VISUAL: {v}" for v in visuals[:15]]
    )


def find_footage(topic: str, script_text: str = "") -> str:
    """Search for real stock footage for every major scene in the script."""
    client = get_client()

    if not script_text:
        script_text = load_stage(topic, "script") or ""
    if not script_text:
        print(f"\nNo script found for: {topic}")
        print(f"Run first:  python main.py script \"{topic}\"\n")
        return ""

    spoken = _strip_script(script_text)
    scene_needs = _extract_scene_needs(script_text, spoken)
    script_excerpt = spoken[:1200]

    print("\n" + "=" * 60)
    print("FOOTAGE FINDER")
    print("Searching for real stock footage for your scenes...")
    print("=" * 60 + "\n")

    tools = [{"type": "web_search_20260209", "name": "web_search"}]

    user_msg = f"""YouTube video topic: "{topic}"

Script excerpt:
{script_excerpt}

Visual moments flagged in the script:
{scene_needs or "(No explicit B-ROLL tags found — analyze the script content for footage needs)"}

Your tasks:
1. Identify the 8-12 most important moments in this video that need real footage
2. For each, web-search to find actual available clips on Pexels, Pixabay, or Coverr
3. Return a JSON array with one object per scene:

{{
  "scene_number": integer,
  "scene_description": "what this moment is about",
  "primary_search_query": "the best search term to find this footage",
  "platform": "Pexels | Pixabay | Coverr | Mixkit | Storyblocks",
  "search_url": "direct URL to search results for this query",
  "found_clips": [
    {{
      "title": "clip name or description",
      "url": "direct URL to the specific clip if found",
      "duration": "clip duration if known",
      "free": true/false
    }}
  ],
  "alternative_queries": ["query 2", "query 3"],
  "footage_available": "high | medium | low",
  "note": "any useful note — e.g. 'AI generation recommended if no results'"
}}

Search the web to find actual clips — don't just guess URLs.
Return ONLY a valid JSON array. No markdown fences."""

    messages = [{"role": "user", "content": user_msg}]
    result = ""

    while True:
        tool_calls = []
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=SYSTEM,
            tools=tools,
            messages=messages,
        ) as stream:
            current_tool_id = ""
            current_tool_input = []
            showing_response = False

            for event in stream:
                if event.type == "content_block_start":
                    blk = event.content_block
                    if blk.type == "thinking":
                        print("[Identifying scenes and searching for footage...]")
                    elif blk.type == "text":
                        showing_response = True
                    elif blk.type == "tool_use":
                        showing_response = False
                        current_tool_id = blk.id
                        current_tool_input = []

                elif event.type == "content_block_delta":
                    d = event.delta
                    if d.type == "text_delta" and showing_response:
                        result += d.text
                    elif d.type == "input_json_delta":
                        current_tool_input.append(d.partial_json)

                elif event.type == "content_block_stop":
                    if current_tool_id:
                        raw = "".join(current_tool_input)
                        try:
                            inp = json.loads(raw) if raw else {}
                        except json.JSONDecodeError:
                            inp = {}
                        q = inp.get("query", "")
                        if q:
                            print(f"  [Searching: {q}]")
                        tool_calls.append({"id": current_tool_id, "input": inp})
                        current_tool_id = ""
                        current_tool_input = []

            final = stream.get_final_message()

        if final.stop_reason != "tool_use" or not tool_calls:
            break

        messages.append({"role": "assistant", "content": final.content})
        tool_results = [
            {
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": "Search results received.",
            }
            for tc in tool_calls
        ]
        messages.append({"role": "user", "content": tool_results})

    # Parse and format
    try:
        clean = re.sub(r'^```json\s*|```\s*$', '', result.strip(), flags=re.MULTILINE)
        scenes = json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', result, re.DOTALL)
        scenes = json.loads(match.group()) if match else []

    output = _format_footage_sheet(scenes, topic)
    print(output)
    save_stage(topic, "footage", output)
    print(f"\n✓ Footage finder saved to project.")
    return output


def _format_footage_sheet(scenes: list, topic: str) -> str:
    lines = [
        "=" * 70,
        f"FOOTAGE FINDER: {topic}",
        "=" * 70,
        "",
        "FREE PLATFORMS:",
        "  Pexels    → pexels.com/videos",
        "  Pixabay   → pixabay.com/videos",
        "  Coverr    → coverr.co",
        "  Mixkit    → mixkit.co/free-stock-video",
        "  Videvo    → videvo.net",
        "",
        "PAID (higher quality):",
        "  Storyblocks → storyblocks.com",
        "  Shutterstock → shutterstock.com",
        "  Pond5       → pond5.com",
        "",
        "=" * 70,
        "",
    ]

    for s in scenes:
        avail = s.get("footage_available", "?")
        avail_icon = {"high": "●", "medium": "◑", "low": "○"}.get(avail, "?")
        lines += [
            f"── SCENE {s.get('scene_number', '?')}  {avail_icon} Footage availability: {avail.upper()} ──",
            f"   {s.get('scene_description', '')}",
            "",
            f"   PRIMARY SEARCH: \"{s.get('primary_search_query', '')}\"",
            f"   PLATFORM: {s.get('platform', '')}",
            f"   SEARCH URL: {s.get('search_url', '')}",
            "",
        ]

        clips = s.get("found_clips", [])
        if clips:
            lines.append("   CLIPS FOUND:")
            for clip in clips:
                free_tag = "[FREE]" if clip.get("free") else "[PAID]"
                dur = f"  ({clip.get('duration', '')})" if clip.get("duration") else ""
                lines.append(f"   {free_tag} {clip.get('title', '')}{dur}")
                if clip.get("url"):
                    lines.append(f"         {clip['url']}")
            lines.append("")

        alts = s.get("alternative_queries", [])
        if alts:
            lines.append("   ALTERNATIVE SEARCHES:")
            for a in alts:
                lines.append(f"   → \"{a}\"")
            lines.append("")

        if s.get("note"):
            lines.append(f"   NOTE: {s['note']}")
            lines.append("")

    return "\n".join(lines)
