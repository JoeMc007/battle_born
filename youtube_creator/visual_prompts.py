"""Visual Prompts — turn a script into a complete OpenArt image + video prompt sheet.

Pipeline:
1. Claude reads the full script and derives a master style prompt (the visual DNA
   that every image and video clip must match).
2. Script is split into 3-4 sentence chunks (one visual per chunk).
3. For each chunk Claude generates:
      - An image prompt  (what to render in OpenArt)
      - A video motion prompt  (how to animate it into a 6-8 sec clip)
      - An on-screen text note  (any caption/lower-third to overlay)
4. Claude generates 6-10 standalone B-roll prompts for cutaways.
5. Everything is saved as a structured prompt sheet and printed for easy copy-paste.
"""

import json
import re
from pathlib import Path

from .client import get_client, MODEL, MAX_TOKENS
from .projects import load_stage, save_stage, PROJECTS_DIR
from .elevenlabs_export import _strip_script          # reuse spoken-only cleaner


# ── Sentence chunker ──────────────────────────────────────────────────────────

def _chunk_sentences(text: str, sentences_per_chunk: int = 3) -> list[str]:
    """Split spoken text into groups of N sentences."""
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        if chunk:
            chunks.append(chunk)
    return chunks


# ── Claude prompt generation ──────────────────────────────────────────────────

_STYLE_SYSTEM = """You are a world-class visual director and AI image prompt engineer.
You specialize in creating cohesive visual identities for YouTube videos using AI image tools.

Your image prompts are:
- Specific and painterly — every prompt describes composition, lighting, color, and mood
- Optimized for cinematic realism in OpenArt / Stable Diffusion / Flux workflows
- Consistent — every prompt in a video shares the same visual DNA via a style anchor
- Never generic — no "a person thinking" or "a group of people" vague descriptions

Video motion prompts (for 6-8 second clips) describe:
- Camera movement (slow push in, gentle pan left, parallax drift, orbital pull-back)
- Subject motion (subtle breathing, slow zoom, particles floating, light shifting)
- Mood of movement (contemplative, urgent, hopeful, tense)
- Duration anchor: always 6-8 seconds, smooth loop-friendly if possible"""

_BROLL_SYSTEM = """You are generating B-roll image prompts for a YouTube video.
B-roll shots are atmospheric cutaways that support the emotional tone of the content
without depicting the main subject directly.

Each B-roll prompt should:
- Be a standalone cinematic image prompt with style anchor applied
- Depict something thematically related but visually distinct (environments, textures,
  metaphors, abstract concepts made visual)
- Be varied — no two shots should feel similar in composition or subject"""


def _generate_style_prompt(script_excerpt: str, visual_style: str, topic: str) -> str:
    """Generate the master style prompt for all images and video clips."""
    client = get_client()

    user_msg = f"""YouTube video topic: "{topic}"
Visual style preference: {visual_style}

Opening of the script:
{script_excerpt[:1200]}

Generate a MASTER STYLE PROMPT — a single block of descriptive text (80-120 words)
that will be appended to every image and video prompt in this project to ensure
visual consistency.

It must define:
- Color palette and grade (warm/cool, saturated/desaturated, specific color references)
- Lighting style (cinematic Rembrandt, soft diffused, high contrast, golden hour, etc.)
- Texture and render feel (photorealistic, painterly, film grain, clean digital, etc.)
- Mood and atmosphere (intimate, epic, urgent, contemplative, etc.)
- Camera aesthetic (anamorphic lens, shallow depth of field, wide angle, etc.)
- Any recurring visual motifs that should appear throughout

Output ONLY the style prompt text. No labels, no explanation."""

    result = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=500,
        system=_STYLE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                result += event.delta.text
                print(event.delta.text, end="", flush=True)
    print()
    return result.strip()


def _generate_scene_prompts(
    chunks: list[str],
    style_prompt: str,
    topic: str,
) -> list[dict]:
    """Generate image + video prompt for each script chunk."""
    client = get_client()

    chunks_json = json.dumps(
        [{"chunk_index": i + 1, "spoken_text": c} for i, c in enumerate(chunks)],
        indent=2,
    )

    user_msg = f"""YouTube video topic: "{topic}"

MASTER STYLE PROMPT (append this to every image and video prompt):
{style_prompt}

SCRIPT CHUNKS (each chunk = 3-4 spoken sentences ≈ one visual):
{chunks_json}

For EVERY chunk, generate a JSON object with these exact keys:
  "chunk_index": integer
  "spoken_text": the original text (copy it verbatim)
  "scene_description": one sentence describing what this moment is about visually
  "image_prompt": a detailed OpenArt/Flux image prompt (100-140 words) that:
      - Describes a specific scene, NOT a generic concept
      - Includes composition, foreground/background, lighting, color
      - Ends with the full master style prompt appended
  "video_prompt": a motion prompt for a 6-8 second video clip (40-60 words) describing:
      - Exact camera move (push in / pull back / pan / orbit / parallax)
      - Any subject motion (subtle only — avoid jarring motion)
      - Mood of the movement
      - "6-8 second clip, smooth" must appear verbatim
  "on_screen_text": if any key phrase from this chunk should appear as a caption or
      lower-third, write it here (max 8 words). Empty string if none.

Return a JSON array of objects — one per chunk.
Output ONLY valid JSON. No markdown fences, no explanation."""

    result = ""
    print(f"\n[Generating {len(chunks)} scene prompts...]\n")
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=_STYLE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start" and event.content_block.type == "thinking":
                print("[Analyzing script scenes...]")
            elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                result += event.delta.text

    try:
        return json.loads(result.strip())
    except json.JSONDecodeError:
        # Attempt to extract JSON array if wrapped in text
        match = re.search(r'\[.*\]', result, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []


def _generate_broll_prompts(
    style_prompt: str,
    topic: str,
    script_excerpt: str,
    count: int = 8,
) -> list[dict]:
    """Generate standalone B-roll image + video prompts."""
    client = get_client()

    user_msg = f"""YouTube video topic: "{topic}"

Script excerpt for context:
{script_excerpt[:800]}

MASTER STYLE PROMPT (append to every prompt):
{style_prompt}

Generate {count} B-roll prompt sets as a JSON array.
Each object must have:
  "broll_index": integer (1 to {count})
  "concept": one-sentence description of what this B-roll represents thematically
  "image_prompt": detailed OpenArt/Flux image prompt (80-120 words) — must be a
      cinematic ENVIRONMENT, TEXTURE, METAPHOR, or ABSTRACT VISUAL (never a person
      looking directly at camera). End with the master style prompt.
  "video_prompt": motion prompt for 6-8 second clip — slow, atmospheric movement.
      "6-8 second clip, smooth" must appear verbatim.

Make each B-roll visually distinct. Vary: interiors vs. exteriors, close-up textures
vs. wide environments, literal vs. metaphorical visuals.

Output ONLY valid JSON array. No markdown, no explanation."""

    result = ""
    print(f"\n[Generating {count} B-roll prompts...]\n")
    with client.messages.stream(
        model=MODEL,
        max_tokens=6000,
        system=_BROLL_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                result += event.delta.text

    try:
        return json.loads(result.strip())
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', result, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []


# ── Output formatter ──────────────────────────────────────────────────────────

def _format_prompt_sheet(
    topic: str,
    style_prompt: str,
    scenes: list[dict],
    broll: list[dict],
) -> str:
    lines = [
        "=" * 70,
        f"VISUAL PROMPT SHEET",
        f"Topic: {topic}",
        f"Scenes: {len(scenes)}  |  B-Roll: {len(broll)}",
        "=" * 70,
        "",
        "┌─────────────────────────────────────────────────────────────────┐",
        "│  MASTER STYLE PROMPT  (append this to every prompt you paste)  │",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
        style_prompt,
        "",
        "=" * 70,
        "  SCENE-BY-SCENE PROMPTS",
        "=" * 70,
        "",
    ]

    for scene in scenes:
        idx = scene.get("chunk_index", "?")
        lines += [
            f"── SCENE {idx} ──────────────────────────────────────────────────────",
            "",
            "SPOKEN TEXT:",
            scene.get("spoken_text", ""),
            "",
            f"SCENE: {scene.get('scene_description', '')}",
        ]
        if scene.get("on_screen_text"):
            lines.append(f"ON-SCREEN TEXT: \"{scene['on_screen_text']}\"")
        lines += [
            "",
            "[ IMAGE PROMPT — paste into OpenArt ]",
            scene.get("image_prompt", ""),
            "",
            "[ VIDEO PROMPT — 6-8 sec clip ]",
            scene.get("video_prompt", ""),
            "",
        ]

    lines += [
        "=" * 70,
        "  B-ROLL PROMPTS",
        "=" * 70,
        "",
    ]

    for br in broll:
        idx = br.get("broll_index", "?")
        lines += [
            f"── B-ROLL {idx} ─────────────────────────────────────────────────────",
            "",
            f"CONCEPT: {br.get('concept', '')}",
            "",
            "[ IMAGE PROMPT — paste into OpenArt ]",
            br.get("image_prompt", ""),
            "",
            "[ VIDEO PROMPT — 6-8 sec clip ]",
            br.get("video_prompt", ""),
            "",
        ]

    return "\n".join(lines)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_visual_prompts(
    topic: str,
    visual_style: str = "cinematic documentary, photorealistic",
    sentences_per_chunk: int = 3,
    broll_count: int = 8,
    script_text: str = "",
    output_file: str = "",
) -> str:
    """Generate a complete visual prompt sheet from a saved or provided script."""

    # Resolve script source
    if not script_text:
        script_text = load_stage(topic, "script") or ""
    if not script_text:
        print(
            f"\nNo script found for: {topic}\n"
            f"Run first:  python main.py script \"{topic}\"\n"
        )
        return ""

    # Strip to spoken words only for chunking
    spoken = _strip_script(script_text)

    print("\n" + "=" * 60)
    print("VISUAL PROMPT GENERATOR")
    print(f"Style: {visual_style}")
    print("=" * 60)

    # Step 1 — Master style prompt
    print("\n[Step 1/3] Generating master style prompt...\n")
    style_prompt = _generate_style_prompt(spoken[:1500], visual_style, topic)

    # Step 2 — Scene prompts (chunk every N sentences)
    print(f"\n[Step 2/3] Chunking script and generating scene prompts...")
    chunks = _chunk_sentences(spoken, sentences_per_chunk)
    scenes = _generate_scene_prompts(chunks, style_prompt, topic)

    # Step 3 — B-roll
    print(f"\n[Step 3/3] Generating {broll_count} B-roll prompts...")
    broll = _generate_broll_prompts(style_prompt, topic, spoken, broll_count)

    # Format and save
    sheet = _format_prompt_sheet(topic, style_prompt, scenes, broll)

    if not output_file:
        slug = re.sub(r"[^\w\s-]", "", topic.lower())
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-")[:50]
        output_file = str(PROJECTS_DIR / slug / "visual_prompts.txt")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(sheet)
    save_stage(topic, "visual_prompts", sheet)

    print(f"\n✓ Visual prompt sheet saved → {output_file}")
    print(f"  {len(scenes)} scene prompts  |  {len(broll)} B-roll prompts")
    print(f"  Total clips to produce: {len(scenes) + len(broll)}\n")

    return sheet
