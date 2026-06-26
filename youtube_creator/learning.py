"""Recursive Learning Loop — the app gets smarter every video you make.

How it works:
1. After each script, creator rates it (1-5) and leaves notes on what was off.
2. Feedback is saved to the project and aggregated into a learning profile.
3. Claude analyzes all feedback to extract patterns: what it consistently nails,
   what it consistently misses, and specific corrections for the creator's voice.
4. That analysis is injected into every future script/validate/research call
   as a "lessons learned" block — making each generation smarter than the last.
"""

import json
from datetime import datetime
from pathlib import Path

from .client import get_client, MODEL, MAX_TOKENS
from .projects import list_projects, save_feedback as _save_project_feedback, PROJECTS_DIR

LEARNING_PROFILE_PATH = Path.home() / ".youtube_creator" / "learning_profile.json"


# ── Feedback collection ───────────────────────────────────────────────────────

def collect_feedback(idea: str) -> tuple[int, str] | None:
    """Prompt the creator for feedback on a generated script. Returns (rating, notes)."""
    print("\n" + "─" * 60)
    print("HOW DID THAT SCRIPT LAND?")
    print("Your feedback trains the app to write better scripts for you.")
    print("─" * 60)

    while True:
        raw = input("Rate this script 1-5 (or Enter to skip): ").strip()
        if not raw:
            return None
        try:
            rating = int(raw)
            if 1 <= rating <= 5:
                break
            print("  Enter a number between 1 and 5.")
        except ValueError:
            print("  Enter a number between 1 and 5.")

    print("\nWhat was off? What did it nail? (be specific — this trains your voice profile)")
    print("Examples: 'hook was too generic', 'nailed my sarcasm', 'too formal in section 2'")
    notes = input("> ").strip()

    _save_project_feedback(idea, rating, notes)
    print(f"\n✓ Feedback saved (rating: {rating}/5)")
    return rating, notes


# ── Learning profile generation ───────────────────────────────────────────────

def _gather_all_feedback() -> list[dict]:
    """Collect feedback entries from all projects."""
    entries = []
    projects = list_projects()
    for p in projects:
        if not p.get("rating"):
            continue
        slug = p.get("slug", "")
        project_dir = PROJECTS_DIR / slug
        script_path = project_dir / "script.md"
        script_excerpt = ""
        if script_path.exists():
            script_excerpt = script_path.read_text()[:800]

        for fb in p.get("feedback", []):
            entries.append({
                "idea": p.get("idea", ""),
                "rating": fb.get("rating"),
                "notes": fb.get("notes", ""),
                "script_excerpt": script_excerpt,
            })
    return entries


def regenerate_learning_profile() -> str:
    """Ask Claude to analyze all feedback and extract a learning profile."""
    client = get_client()
    feedback_entries = _gather_all_feedback()

    if not feedback_entries:
        return ""

    feedback_json = json.dumps(feedback_entries, indent=2)

    print("\n[Analyzing your feedback history to improve future scripts...]\n")

    system = """You are analyzing feedback a YouTube creator has given on AI-generated scripts.
Your job is to identify precise, actionable patterns that will make future scripts better.

Output a JSON object with exactly these keys:
{
  "voice_corrections": ["specific things to fix about the voice/tone"],
  "structural_wins": ["script structures or techniques the creator rated highly"],
  "structural_misses": ["structural patterns the creator consistently dislikes"],
  "hook_guidance": "what works and doesn't work for this creator's hooks",
  "pacing_notes": "what the creator says about pacing — too fast, too slow, wrong rhythm",
  "what_to_avoid": ["specific phrases, styles, or approaches to never repeat"],
  "what_to_keep": ["specific things creator explicitly praised"],
  "overall_pattern": "one paragraph summary of the key lesson across all feedback",
  "confidence": "low/medium/high based on how much feedback exists"
}

Be specific. "Too formal" is useless. "Uses 'furthermore' when creator never uses connector words" is useful.
Only output valid JSON — no markdown, no explanation."""

    user_message = f"""Here is all the feedback this creator has given on generated scripts:

{feedback_json}

Analyze the patterns and return the learning profile JSON."""

    result_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                result_text += event.delta.text

    try:
        profile = json.loads(result_text.strip())
        profile["generated_at"] = datetime.now().isoformat()
        profile["feedback_count"] = len(feedback_entries)
        LEARNING_PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LEARNING_PROFILE_PATH.write_text(json.dumps(profile, indent=2))
        print(f"✓ Learning profile updated from {len(feedback_entries)} feedback entries.")
        return _profile_to_prompt_block(profile)
    except json.JSONDecodeError:
        return ""


def load_learning_profile() -> str:
    """Load the current learning profile as a prompt block."""
    if not LEARNING_PROFILE_PATH.exists():
        return ""
    try:
        profile = json.loads(LEARNING_PROFILE_PATH.read_text())
        return _profile_to_prompt_block(profile)
    except (json.JSONDecodeError, KeyError):
        return ""


def _profile_to_prompt_block(profile: dict) -> str:
    if not profile or profile.get("confidence") == "low":
        return ""

    lines = [
        "## LESSONS LEARNED FROM PAST SCRIPTS",
        f"(Based on {profile.get('feedback_count', 0)} rated scripts — confidence: {profile.get('confidence', 'unknown')})",
        "",
        f"Pattern summary: {profile.get('overall_pattern', '')}",
        "",
    ]

    if profile.get("hook_guidance"):
        lines += [f"Hook guidance: {profile['hook_guidance']}", ""]

    if profile.get("pacing_notes"):
        lines += [f"Pacing: {profile['pacing_notes']}", ""]

    if profile.get("voice_corrections"):
        lines.append("Voice corrections (apply these):")
        for c in profile["voice_corrections"]:
            lines.append(f"  - {c}")
        lines.append("")

    if profile.get("what_to_avoid"):
        lines.append("NEVER do these (creator explicitly disliked):")
        for w in profile["what_to_avoid"]:
            lines.append(f"  ✗ {w}")
        lines.append("")

    if profile.get("what_to_keep"):
        lines.append("Always do these (creator explicitly praised):")
        for w in profile["what_to_keep"]:
            lines.append(f"  ✓ {w}")

    return "\n".join(lines)


def print_learning_summary() -> None:
    """Print a human-readable summary of the current learning profile."""
    if not LEARNING_PROFILE_PATH.exists():
        print("\nNo learning profile yet. Rate scripts after generating them to build it.")
        return

    try:
        profile = json.loads(LEARNING_PROFILE_PATH.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        print("\nCould not read learning profile.")
        return

    print("\n" + "=" * 60)
    print("LEARNING PROFILE")
    print(f"Built from {profile.get('feedback_count', 0)} rated scripts")
    print("=" * 60)
    print(f"\n{profile.get('overall_pattern', '')}")

    if profile.get("what_to_avoid"):
        print("\nThings to avoid:")
        for w in profile["what_to_avoid"]:
            print(f"  ✗ {w}")

    if profile.get("what_to_keep"):
        print("\nThings that work:")
        for w in profile["what_to_keep"]:
            print(f"  ✓ {w}")
    print()
