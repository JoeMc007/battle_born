"""Generate a full YouTube video script using Claude with streaming."""

from .client import get_client, MODEL, MAX_TOKENS

SYSTEM_PROMPT = """You are a professional YouTube scriptwriter who crafts engaging, high-retention
video scripts. You understand pacing, storytelling, and how to keep viewers watching.

Script structure you always follow:
- HOOK (0-30 sec): Grab attention immediately — open with a bold claim, surprising fact, or question
- INTRO (30-60 sec): Who you are, what the video delivers, why they should stay
- BODY: 3-7 main sections with smooth transitions, stories, examples, and pattern interrupts
- CTA (call-to-action): Natural, non-pushy ask for likes/subscribe/comment
- OUTRO: Tease next video or related content

Style guidelines:
- Write conversational, spoken-word language (contractions, short sentences)
- Add [VISUAL CUE] notes for B-roll, graphics, or on-screen text
- Mark [PAUSE] for dramatic effect where needed
- Include [TITLE CARD] markers for chapter titles
- Aim for ~150 words per minute (typical YouTube pacing)"""


def generate_script(
    topic: str,
    duration_minutes: int = 10,
    style: str = "educational",
    audience: str = "",
    key_points: list[str] | None = None,
) -> None:
    """Stream a complete YouTube video script."""
    client = get_client()

    target_words = duration_minutes * 150
    points_section = ""
    if key_points:
        points_list = "\n".join(f"  - {p}" for p in key_points)
        points_section = f"\nKey points to cover:\n{points_list}"

    audience_section = f"\nTarget audience: {audience}" if audience else ""

    user_message = f"""Write a complete YouTube script for the following:

Topic: {topic}
Video style: {style}
Target duration: {duration_minutes} minutes (~{target_words} words){audience_section}{points_section}

Write the full script with all visual cues, pacing notes, and chapter markers.
Make it ready to record — every word should be spoken naturally out loud."""

    print("\n" + "=" * 60)
    print(f"SCRIPT: {topic}")
    print(f"Style: {style} | Duration: ~{duration_minutes} min")
    print("=" * 60 + "\n")

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        showing_response = False

        for event in stream:
            if event.type == "content_block_start":
                block = event.content_block
                if block.type == "thinking":
                    print("[Crafting your script...]\n")
                elif block.type == "text":
                    showing_response = True

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta" and showing_response:
                    print(delta.text, end="", flush=True)

    print("\n")
