"""Script Revision Loop — iteratively refine sections of a script via feedback."""

import re
from .client import get_client, MODEL, MAX_TOKENS
from .channel_dna import load_dna
from .learning import load_learning_profile
from .projects import load_stage, save_stage

SYSTEM = """You are a precision script editor. You receive a complete YouTube script
and targeted feedback from the creator. You revise ONLY what the feedback addresses —
every other word in the script stays exactly the same.

Rules:
- Never rewrite sections the creator didn't ask about
- Match the creator's voice exactly (channel DNA is provided)
- When cutting for time, remove filler sentences — never gut the structure
- When strengthening a hook, punch it harder without losing the open loop
- When adding story, fit it to the existing pacing — no new [VISUAL] tags needed
  unless the addition genuinely needs one
- Output the COMPLETE revised script (not just the changed section)
- At the end add a short ## REVISION NOTES block: what you changed and why"""


def revise_script(topic: str, script_text: str = "") -> str:
    """Interactive revision loop — takes feedback, rewrites, loops until done."""
    client = get_client()
    dna = load_dna()

    # Load script from project if not provided
    if not script_text:
        script_text = load_stage(topic, "script") or ""

    if not script_text:
        print(f"\nNo script found for: {topic}")
        print(f"Run first:  python main.py script \"{topic}\"\n")
        return ""

    dna_block = dna.to_prompt_block() if not dna.is_empty() else ""
    learning_block = load_learning_profile()

    system_with_dna = SYSTEM
    if dna_block:
        system_with_dna += f"\n\n{dna_block}"
    if learning_block:
        system_with_dna += f"\n\n{learning_block}"

    current_script = script_text
    revision_count = 0

    print("\n" + "=" * 60)
    print("SCRIPT REVISION LOOP")
    print("=" * 60)
    print("\nCurrent script is loaded. Tell me what to fix.")
    print("Examples:")
    print('  "make the hook stronger — it\'s too soft"')
    print('  "cut about 2 minutes from section 3"')
    print('  "add a personal story after the first re-hook"')
    print('  "the outro feels rushed, expand it"')
    print("\nType 'done' when you're happy with the script.")
    print("Type 'show' to print the current script.")
    print("Type 'undo' to revert to the previous version.")
    print()

    previous_script = current_script

    while True:
        feedback = input(f"[Revision {revision_count + 1}] Your feedback > ").strip()

        if not feedback:
            continue

        if feedback.lower() == "done":
            print("\n✓ Revision complete.")
            break

        if feedback.lower() == "show":
            print("\n" + "─" * 60)
            print(current_script)
            print("─" * 60 + "\n")
            continue

        if feedback.lower() == "undo":
            if revision_count == 0:
                print("  Nothing to undo.")
            else:
                current_script = previous_script
                revision_count = max(0, revision_count - 1)
                print("  ✓ Reverted to previous version.")
            continue

        previous_script = current_script
        revision_count += 1

        user_msg = f"""Script to revise:

{current_script}

Creator feedback:
{feedback}

Apply the feedback and return the complete revised script."""

        print(f"\n[Applying revision {revision_count}...]\n")

        revised = ""
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=system_with_dna,
            messages=[{"role": "user", "content": user_msg}],
        ) as stream:
            showing = False
            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "thinking":
                        print("[Thinking through the revision...]")
                    elif event.content_block.type == "text":
                        showing = True
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta" and showing:
                        print(event.delta.text, end="", flush=True)
                        revised += event.delta.text

        print("\n")

        if revised.strip():
            current_script = revised.strip()
            # Save after every successful revision
            save_stage(topic, "script", current_script)
            print(f"✓ Revision {revision_count} saved to project.")
        else:
            print("[Warning: empty response — keeping previous version]")
            current_script = previous_script

    return current_script
