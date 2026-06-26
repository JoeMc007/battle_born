"""ElevenLabs export — strip everything except spoken words from a script."""

import re
from pathlib import Path

from .client import get_client, MODEL, MAX_TOKENS
from .projects import load_stage, PROJECTS_DIR


# ── Regex-based stripping ─────────────────────────────────────────────────────

# Bracket tags that are never spoken
_VISUAL_TAGS = re.compile(
    r'\[('
    r'VISUAL[^]]*|B-ROLL[^]]*|ZOOM[^]]*|SMASH CUT[^]]*'
    r'|TEXT ON SCREEN[^]]*|GRAPHIC[^]]*|SOUND EFFECT[^]]*'
    r'|REACTION[^]]*|TITLE CARD[^]]*|RE-HOOK[^]]*'
    r'|PAUSE'
    r')\]',
    re.IGNORECASE,
)

# Timestamp / section marker lines like [0:00 — HOOK] or [SECTION TITLE — ...]
_SECTION_MARKER = re.compile(
    r'^\s*\[\d+:\d+\s*[-—][^]]*\]\s*$|'     # [0:00 — HOOK]
    r'^\s*\[RE-HOOK[^]]*\]\s*$|'              # [RE-HOOK @ ~2:00]
    r'^\s*\[SECTION[^]]*\]\s*$|'              # [SECTION TITLE — ...]
    r'^\s*\[FINAL[^]]*\]\s*$|'               # [FINAL REVEAL]
    r'^\s*\[OPEN LOOP[^]]*\]\s*$|'           # [OPEN LOOP PLANTED]
    r'^\s*\[CHANNEL INTRO\]\s*$|'            # [CHANNEL INTRO]
    r'^\s*\[CTA\]\s*$|'                      # [CTA]
    r'^\s*\[OUTRO\]\s*$',                    # [OUTRO]
    re.IGNORECASE,
)

# Markdown headers (## Section Name)
_MD_HEADER = re.compile(r'^\s*#{1,6}\s+.*$')

# Stage directions in parentheses on their own line
_PAREN_DIRECTION = re.compile(r'^\s*\(.*\)\s*$')


def _strip_script(raw: str) -> str:
    """Remove all non-spoken content from a script using regex."""
    # Cut everything from ## EDITOR NOTES onward
    editor_notes_match = re.search(r'^##\s*EDITOR NOTES', raw, re.IGNORECASE | re.MULTILINE)
    if editor_notes_match:
        raw = raw[:editor_notes_match.start()]

    lines = raw.splitlines()
    cleaned = []

    for line in lines:
        # Drop pure section marker lines
        if _SECTION_MARKER.match(line):
            continue
        # Drop markdown headers
        if _MD_HEADER.match(line):
            continue
        # Drop parenthetical stage directions on their own line
        if _PAREN_DIRECTION.match(line):
            continue

        # Strip inline visual/direction tags from spoken lines
        line = _VISUAL_TAGS.sub("", line)

        # Convert [PAUSE] to em-dash pause for natural TTS rhythm
        line = re.sub(r'\[PAUSE\]', '...', line, flags=re.IGNORECASE)

        # Clean up leftover double spaces and trailing whitespace
        line = re.sub(r'  +', ' ', line).strip()

        cleaned.append(line)

    # Collapse runs of 3+ blank lines to a single blank line
    text = "\n".join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Claude polish pass ────────────────────────────────────────────────────────

def _claude_polish(raw_spoken: str) -> str:
    """Ask Claude to do a final clean pass — catch anything regex missed."""
    client = get_client()

    system = """You are cleaning a YouTube video script for text-to-speech synthesis in ElevenLabs.

Your ONLY job: return the script with nothing but the spoken words.

REMOVE completely:
- Any remaining stage directions, visual cues, or production notes
- Anything in square brackets: [TEXT ON SCREEN: X], [VISUAL: X], [B-ROLL: X], etc.
- Any timestamp markers or section headers
- Any markdown formatting (**, ##, *, _)
- Any parenthetical directions like (pause here) or (gestures to camera)
- Any lines that are clearly notes to the editor or creator, not spoken words
- The "EDITOR NOTES" section and everything in it

KEEP exactly as-is:
- Every word meant to be spoken out loud
- Natural punctuation that helps TTS pacing (commas, periods, ellipses)
- Paragraph breaks (they create natural pauses in ElevenLabs)
- Numbers written as digits (ElevenLabs reads them correctly)

DO NOT:
- Rewrite any spoken sentences
- Change any words
- Add anything
- Summarize or shorten
- Add a preamble like "Here is the cleaned script:"

Output ONLY the cleaned spoken text. Nothing else."""

    result = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": raw_spoken}],
    ) as stream:
        for event in stream:
            if (event.type == "content_block_delta"
                    and event.delta.type == "text_delta"):
                result += event.delta.text
                print(event.delta.text, end="", flush=True)

    print()
    return result.strip()


# ── Public entry point ────────────────────────────────────────────────────────

def export_for_elevenlabs(
    topic: str,
    output_file: str = "",
    polish: bool = True,
    script_text: str = "",
) -> str:
    """
    Export a clean spoken-only script for ElevenLabs.

    Priority order for source:
      1. script_text argument (passed directly)
      2. Saved project file for this topic
      3. Prompt the user to run `script` first
    """
    # Resolve source
    if not script_text:
        script_text = load_stage(topic, "script") or ""

    if not script_text:
        print(
            f"\nNo script found for: {topic}\n"
            f"Run this first:\n"
            f"  python main.py script \"{topic}\"\n"
        )
        return ""

    print("\n" + "=" * 60)
    print("ELEVENLABS EXPORT")
    print("Stripping stage directions, visuals, and markers...")
    print("=" * 60 + "\n")

    # Phase 1: regex strip
    stripped = _strip_script(script_text)

    # Phase 2: Claude polish (catches edge cases regex misses)
    if polish:
        print("[Claude polishing — removing any remaining non-spoken content...]\n")
        final = _claude_polish(stripped)
    else:
        final = stripped

    # Save output
    if not output_file:
        slug = re.sub(r"[^\w\s-]", "", topic.lower())
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-")[:50]
        output_file = str(PROJECTS_DIR / slug / "elevenlabs.txt")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(final)

    word_count = len(final.split())
    est_minutes = round(word_count / 150)

    print(f"\n✓ ElevenLabs script saved → {output_file}")
    print(f"  {word_count} words  |  ~{est_minutes} min read time")

    return final
