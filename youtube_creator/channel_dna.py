"""Channel DNA — store and load a creator's voice profile."""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field

DNA_PATH = Path.home() / ".youtube_creator" / "channel_dna.json"


@dataclass
class ChannelDNA:
    channel_name: str = ""
    niche: str = ""
    one_liner: str = ""                     # e.g. "We keep it real so you don't have to."
    catchphrases: list[str] = field(default_factory=list)   # recurring phrases
    tone: str = ""                          # e.g. "casual, direct, slightly sarcastic"
    pacing: str = ""                        # e.g. "fast, punchy, no filler"
    audience: str = ""                      # who watches
    taboo_words: list[str] = field(default_factory=list)    # words they never say
    sample_lines: list[str] = field(default_factory=list)   # actual lines from past videos
    swear_level: str = "none"               # none / mild / moderate / heavy
    story_style: str = ""                   # e.g. "uses personal failures, then lessons"
    call_to_action: str = ""                # their specific CTA phrasing
    outro_phrase: str = ""                  # how they always end

    def is_empty(self) -> bool:
        return not self.channel_name

    def to_prompt_block(self) -> str:
        """Render DNA as a system prompt section."""
        if self.is_empty():
            return ""

        lines = [
            "## CREATOR VOICE — FOLLOW THIS EXACTLY",
            f"Channel: {self.channel_name}",
            f"Niche: {self.niche}",
            f"One-liner / tagline: \"{self.one_liner}\"",
            f"Tone: {self.tone}",
            f"Pacing: {self.pacing}",
            f"Audience: {self.audience}",
            f"Swear level: {self.swear_level}",
            f"Story style: {self.story_style}",
        ]
        if self.catchphrases:
            lines.append("Catchphrases to weave in naturally: " + ", ".join(f'"{p}"' for p in self.catchphrases))
        if self.taboo_words:
            lines.append("NEVER use these words/phrases: " + ", ".join(self.taboo_words))
        if self.sample_lines:
            lines.append("\nSample lines from their actual content (match this energy exactly):")
            for s in self.sample_lines:
                lines.append(f'  "{s}"')
        if self.call_to_action:
            lines.append(f"\nTheir CTA phrasing: \"{self.call_to_action}\"")
        if self.outro_phrase:
            lines.append(f"Their outro: \"{self.outro_phrase}\"")
        return "\n".join(lines)


def load_dna() -> ChannelDNA:
    if not DNA_PATH.exists():
        return ChannelDNA()
    with open(DNA_PATH) as f:
        return ChannelDNA(**json.load(f))


def save_dna(dna: ChannelDNA) -> None:
    DNA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DNA_PATH, "w") as f:
        json.dump(asdict(dna), f, indent=2)


def setup_dna_interactive() -> ChannelDNA:
    """Walk the creator through setting up their Channel DNA."""
    print("\n" + "=" * 60)
    print("CHANNEL DNA SETUP")
    print("This is your voice profile. Be specific — the more detail")
    print("you give, the less the script sounds like AI wrote it.")
    print("=" * 60 + "\n")

    existing = load_dna()

    def ask(prompt: str, current: str = "", required: bool = False) -> str:
        hint = f" [{current}]" if current else ""
        while True:
            val = input(f"{prompt}{hint}: ").strip()
            if not val and current:
                return current
            if val or not required:
                return val
            print("  (required — please enter a value)")

    def ask_list(prompt: str, current: list[str] = []) -> list[str]:
        hint = f" [{', '.join(current)}]" if current else ""
        print(f"{prompt}{hint}")
        print("  (enter one per line, blank line when done)")
        items = []
        while True:
            item = input("  > ").strip()
            if not item:
                break
            items.append(item)
        return items if items else current

    dna = ChannelDNA(
        channel_name=ask("Channel name", existing.channel_name, required=True),
        niche=ask("Niche / topic area (be specific)", existing.niche, required=True),
        one_liner=ask(
            "Your one-liner / tagline (the phrase that defines your channel)",
            existing.one_liner,
        ),
        tone=ask(
            "Describe your tone (e.g. 'casual, direct, mildly sarcastic, never corporate')",
            existing.tone,
        ),
        pacing=ask(
            "Describe your pacing (e.g. 'fast-paced, no filler, punchy sentences')",
            existing.pacing,
        ),
        audience=ask(
            "Who watches you (age, mindset, why they come to your channel)",
            existing.audience,
        ),
        swear_level=ask(
            "Swear level — none / mild / moderate / heavy",
            existing.swear_level or "none",
        ),
        story_style=ask(
            "How do you tell stories? (e.g. 'start with failure, then lesson')",
            existing.story_style,
        ),
        call_to_action=ask(
            "Your exact CTA phrasing (how you ask for likes/subs)",
            existing.call_to_action,
        ),
        outro_phrase=ask(
            "Your outro / sign-off phrase",
            existing.outro_phrase,
        ),
    )

    print()
    dna.catchphrases = ask_list(
        "Catchphrases you use regularly (leave blank to keep existing)",
        existing.catchphrases,
    )
    dna.taboo_words = ask_list(
        "Words/phrases you NEVER say (AI clichés to ban, formal words you hate, etc.)",
        existing.taboo_words,
    )
    dna.sample_lines = ask_list(
        "Paste 3-5 actual lines from your best videos (exact quotes):",
        existing.sample_lines,
    )

    save_dna(dna)
    print(f"\n✓ Channel DNA saved to {DNA_PATH}")
    return dna
