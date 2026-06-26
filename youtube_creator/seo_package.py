"""SEO Package — titles, thumbnail concepts, description, tags, chapters, pinned comment."""

import re
import json
from .client import get_client, MODEL, MAX_TOKENS
from .projects import load_stage, save_stage
from .channel_dna import load_dna

SYSTEM = """You are an elite YouTube SEO strategist and title copywriter.
You have deep knowledge of YouTube's search algorithm, click-through psychology,
and what makes thumbnails and titles perform.

Every output you produce is grounded in:
- Keyword intent matching (what people actually type to find this content)
- Emotional triggers that drive clicks (curiosity gap, fear of missing out, transformation)
- Pattern interrupts that stand out in a crowded feed
- The creator's voice and channel DNA — never generic, always on-brand"""


def generate_seo_package(topic: str, script_text: str = "") -> str:
    """Generate a full SEO package from a saved or provided script."""
    client = get_client()
    dna = load_dna()

    if not script_text:
        script_text = load_stage(topic, "script") or ""

    if not script_text:
        print(f"\nNo script found for: {topic}")
        print(f"Run first:  python main.py script \"{topic}\"\n")
        return ""

    # Pull first 1500 chars of script for context
    script_excerpt = script_text[:1500]

    channel_context = ""
    if not dna.is_empty():
        channel_context = (
            f"Channel: {dna.channel_name}\n"
            f"Niche: {dna.niche}\n"
            f"Tone: {dna.tone}\n"
            f"One-liner: \"{dna.one_liner}\"\n"
            f"Audience: {dna.audience}\n"
        )

    # Extract chapter markers from script for timestamps
    chapter_pattern = re.compile(
        r'\[(\d+:\d+)\s*[-—]\s*([^\]]+)\]|\[([A-Z][A-Z\s]+)\s*[-—]\s*([^\]]+)\]'
    )
    chapters_found = chapter_pattern.findall(script_text)

    user_msg = f"""Topic: "{topic}"

{channel_context}

Script excerpt (first section):
{script_excerpt}

Generate a complete YouTube SEO package as a JSON object with these exact keys:

"titles": array of 10 title options, each an object with:
  "title": the title text (max 70 characters)
  "type": one of [question, number, howto, controversy, transformation, story, secret, comparison]
  "ctr_reasoning": one sentence on why this title gets clicks
  "keyword_target": the primary search phrase this targets

"thumbnail_concepts": array of 3 objects, each with:
  "concept": one-sentence visual description
  "text_overlay": exact words to appear on thumbnail (max 4 words, high contrast)
  "emotion": the facial expression or emotional state to convey
  "composition": brief layout note (e.g. "creator left, bold text right, dark bg")
  "color_direction": 2-3 colors that will pop in feed

"description": object with:
  "hook_line": first line (appears in search preview, max 100 chars, no clickbait)
  "body": 150-200 word description with natural keyword integration
  "cta_line": one line asking viewers to subscribe/like
  "links_placeholder": "[Add links here: related videos, resources mentioned]"

"tags": array of 20 tag strings, ordered from most to least specific.
  Mix: exact match (3-4 word phrases), broad (1-2 words), long-tail (5+ words)

"chapters": array of chapter objects extracted from the script structure:
  "timestamp": "0:00" format — estimate based on script length (~150 wpm)
  "title": chapter title (max 40 chars)
  Note: always start with "0:00 Introduction"

"pinned_comment": string — a comment the creator pins immediately after upload.
  Should: ask a question to drive comments, tease the best moment in the video,
  or give a bonus tip not in the video. 1-3 sentences, creator's voice.

"best_posting_time": one sentence recommendation on when to post this topic.

Output ONLY valid JSON. No markdown fences."""

    print("\n" + "=" * 60)
    print("SEO PACKAGE")
    print("=" * 60 + "\n")
    print("[Generating titles, thumbnails, description, tags, chapters...]\n")

    result = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=6000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start" and event.content_block.type == "thinking":
                print("[Analyzing script for SEO opportunities...]")
            elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                result += event.delta.text

    # Parse and format
    try:
        # Strip markdown fences if present
        clean = re.sub(r'^```json\s*|```\s*$', '', result.strip(), flags=re.MULTILINE)
        data = json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                print("\n[Warning: Could not parse SEO JSON — saving raw output]")
                save_stage(topic, "seo", result)
                return result
        else:
            save_stage(topic, "seo", result)
            return result

    output = _format_seo_sheet(data, topic)
    print(output)
    save_stage(topic, "seo", output)

    print(f"\n✓ SEO package saved to project.")
    return output


def _format_seo_sheet(data: dict, topic: str) -> str:
    lines = [
        "=" * 70,
        f"SEO PACKAGE: {topic}",
        "=" * 70,
        "",
        "─── TITLES ─────────────────────────────────────────────────────────",
        "",
    ]

    for i, t in enumerate(data.get("titles", []), 1):
        lines += [
            f"{i:>2}. [{t.get('type', '').upper()}] {t.get('title', '')}",
            f"    Target keyword: {t.get('keyword_target', '')}",
            f"    Why it clicks: {t.get('ctr_reasoning', '')}",
            "",
        ]

    lines += [
        "─── THUMBNAIL CONCEPTS ──────────────────────────────────────────────",
        "",
    ]
    for i, th in enumerate(data.get("thumbnail_concepts", []), 1):
        lines += [
            f"THUMBNAIL {i}",
            f"  Visual: {th.get('concept', '')}",
            f"  Text overlay: \"{th.get('text_overlay', '')}\"",
            f"  Emotion: {th.get('emotion', '')}",
            f"  Layout: {th.get('composition', '')}",
            f"  Colors: {th.get('color_direction', '')}",
            "",
        ]

    desc = data.get("description", {})
    lines += [
        "─── DESCRIPTION ─────────────────────────────────────────────────────",
        "",
        f"HOOK LINE (search preview):",
        desc.get("hook_line", ""),
        "",
        desc.get("body", ""),
        "",
        desc.get("cta_line", ""),
        "",
        desc.get("links_placeholder", ""),
        "",
        "─── TAGS (copy all) ─────────────────────────────────────────────────",
        "",
        ", ".join(data.get("tags", [])),
        "",
        "─── CHAPTERS ────────────────────────────────────────────────────────",
        "",
    ]
    for ch in data.get("chapters", []):
        lines.append(f"{ch.get('timestamp', '0:00')} {ch.get('title', '')}")

    pinned = data.get("pinned_comment", "")
    posting = data.get("best_posting_time", "")
    lines += [
        "",
        "─── PINNED COMMENT ──────────────────────────────────────────────────",
        "",
        pinned,
        "",
        "─── POSTING TIME ────────────────────────────────────────────────────",
        "",
        posting,
        "",
    ]
    return "\n".join(lines)
