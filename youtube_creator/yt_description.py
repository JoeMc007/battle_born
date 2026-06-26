"""YouTube Description Generator — SEO-optimized, copy-paste ready description.

Produces the exact text to paste into YouTube's description field:
  - Hook line (visible before "Show more")
  - Keyword-rich body copy
  - What's covered in this video
  - Formatted chapter timestamps (YouTube-native format)
  - Resource/links placeholder
  - About the channel
  - Hashtags (#tag format)
  - Keyword list (for buried SEO)
"""

import re
import json
from .client import get_client, MODEL, MAX_TOKENS
from .projects import load_stage, save_stage
from .channel_dna import load_dna

SYSTEM = """You are an expert YouTube SEO copywriter. You write descriptions that:
1. Hook viewers in the first 2 lines (visible before "Show more")
2. Naturally weave in high-value search keywords without keyword stuffing
3. Tell YouTube's algorithm exactly what the video is about
4. Drive action: comments, subscriptions, related video views
5. Are formatted exactly the way YouTube expects them

You know these YouTube description rules:
- First 100-150 characters appear as search snippet preview — make them count
- Chapters must be in exact format: 0:00 Title (timestamps must be ascending)
- Hashtags at the bottom get displayed above the title on mobile
- Keyword density sweet spot: 2-3% (not stuffed, not absent)
- Line breaks and spacing affect readability significantly"""


def generate_yt_description(
    topic: str,
    script_text: str = "",
    seo_data: str = "",
) -> str:
    """Generate a complete, copy-paste ready YouTube description."""
    client = get_client()
    dna = load_dna()

    if not script_text:
        script_text = load_stage(topic, "script") or ""
    if not seo_data:
        seo_data = load_stage(topic, "seo") or ""

    if not script_text:
        print(f"\nNo script found for: {topic}")
        print(f"Run first:  python main.py script \"{topic}\"\n")
        return ""

    channel_info = ""
    if not dna.is_empty():
        channel_info = (
            f"Channel name: {dna.channel_name}\n"
            f"Niche: {dna.niche}\n"
            f"One-liner: \"{dna.one_liner}\"\n"
            f"Audience: {dna.audience}\n"
            f"Tone: {dna.tone}\n"
        )

    seo_context = f"\nSEO data already generated:\n{seo_data[:1000]}" if seo_data else ""

    # Extract script sections to build chapters
    chapter_markers = re.findall(
        r'\[(\d+:\d+)\s*[-—]\s*([^\]]+)\]', script_text
    )

    # Estimate timestamps from word count if no explicit markers
    if not chapter_markers:
        sections = re.findall(
            r'\[([A-Z][A-Z\s]+(?:SECTION|REVEAL|HOOK|INTRO|OUTRO|CTA)[^\]]*)\]',
            script_text, re.IGNORECASE
        )

    print("\n" + "=" * 60)
    print("YOUTUBE DESCRIPTION GENERATOR")
    print("=" * 60 + "\n")
    print("[Building SEO-optimized description, chapters, and keywords...]\n")

    user_msg = f"""Video topic: "{topic}"

{channel_info}
{seo_context}

Script (first 2000 characters):
{script_text[:2000]}

Chapters found in script:
{json.dumps(chapter_markers) if chapter_markers else "No explicit timestamps — estimate from script structure at ~150 wpm"}

Generate a complete YouTube description as a JSON object with these exact keys:

"hook_line": String (first line, max 100 chars, appears in search preview,
  must make someone click "Show more" — a bold claim, question, or promise)

"second_line": String (second visible line, max 100 chars, reinforces the hook
  or previews the value they'll get)

"body": String (150-250 words, 3-4 short paragraphs. Naturally integrate the
  main keywords 2-3 times each. Describe what the viewer will learn/get.
  Written in creator's tone. NO keyword stuffing — must read naturally.)

"whats_covered": Array of 5-7 strings, each a bullet point of what's in the video
  (readers scan these to decide if the video is worth their time)

"chapters": Array of objects with "timestamp" and "title":
  - Always start with "0:00 Introduction"
  - Estimate timestamps based on script structure (~150 words per minute)
  - Chapter titles max 40 characters
  - Minimum 5 chapters, maximum 12

"resources_placeholder": String — template text for links section
  (e.g., "🔗 Resources mentioned:\\n→ [Link 1]\\n→ [Link 2]")

"about_channel": String — 2-3 sentence "About this channel" blurb in creator's voice
  (appears at bottom, helps new visitors decide to subscribe)

"hashtags": Array of 5 hashtag strings (include # symbol).
  Mix: 1 broad (#productivity), 2 niche (#timeblocking), 2 video-specific.
  These display ABOVE the video title on mobile — make them good.

"keywords": Array of 15-20 keyword strings (not hashtags — these are plain phrases
  for SEO, listed at bottom of description where YouTube algorithm reads them)

"meta_note": String — one sentence on the main keyword this description is optimized for

Output ONLY valid JSON. No markdown fences. No explanation."""

    result = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start" and event.content_block.type == "thinking":
                print("[Optimizing for YouTube search...]")
            elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                result += event.delta.text

    try:
        clean = re.sub(r'^```json\s*|```\s*$', '', result.strip(), flags=re.MULTILINE)
        data = json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                print("\n[Warning: Could not parse JSON — saving raw output]")
                save_stage(topic, "description", result)
                return result
        else:
            save_stage(topic, "description", result)
            return result

    output = _format_description(data, topic)
    print(output)
    save_stage(topic, "description", output)
    print(f"\n✓ YouTube description saved to project.")
    return output


def _format_description(data: dict, topic: str) -> str:
    lines = [
        "=" * 70,
        f"YOUTUBE DESCRIPTION: {topic}",
        f"Optimized for: {data.get('meta_note', '')}",
        "=" * 70,
        "",
        "┌─────────────────────────────────────────────────────────────────┐",
        "│  COPY-PASTE THIS INTO YOUTUBE DESCRIPTION  (exactly as shown)  │",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
    ]

    # ── The actual description text ──────────────────────────────────────────
    desc_lines = []

    desc_lines.append(data.get("hook_line", ""))
    desc_lines.append(data.get("second_line", ""))
    desc_lines.append("")
    desc_lines.append(data.get("body", ""))
    desc_lines.append("")

    what = data.get("whats_covered", [])
    if what:
        desc_lines.append("In this video:")
        for item in what:
            desc_lines.append(f"✅ {item}")
        desc_lines.append("")

    desc_lines.append(data.get("resources_placeholder", ""))
    desc_lines.append("")

    chapters = data.get("chapters", [])
    if chapters:
        desc_lines.append("📌 CHAPTERS")
        for ch in chapters:
            desc_lines.append(f"{ch.get('timestamp', '0:00')} {ch.get('title', '')}")
        desc_lines.append("")

    about = data.get("about_channel", "")
    if about:
        desc_lines.append("─────────────────────")
        desc_lines.append(about)
        desc_lines.append("")

    keywords = data.get("keywords", [])
    if keywords:
        desc_lines.append(", ".join(keywords))
        desc_lines.append("")

    hashtags = data.get("hashtags", [])
    if hashtags:
        desc_lines.append(" ".join(hashtags))

    # Print the copy-paste block
    lines.append("▼ START COPYING HERE ▼")
    lines.append("")
    lines.extend(desc_lines)
    lines.append("")
    lines.append("▲ STOP COPYING HERE ▲")

    # ── Reference section ─────────────────────────────────────────────────────
    lines += [
        "",
        "─── REFERENCE: CHAPTERS LIST ────────────────────────────────────────",
        "",
    ]
    for ch in chapters:
        lines.append(f"  {ch.get('timestamp', '0:00')}  {ch.get('title', '')}")

    lines += [
        "",
        "─── REFERENCE: HASHTAGS ─────────────────────────────────────────────",
        "",
        " ".join(data.get("hashtags", [])),
        "",
        "─── REFERENCE: KEYWORDS ─────────────────────────────────────────────",
        "",
    ]
    for kw in keywords:
        lines.append(f"  • {kw}")

    lines.append("")
    return "\n".join(lines)
