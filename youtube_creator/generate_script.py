"""Generate a world-class YouTube video script with retention engineering."""

from .client import get_client, MODEL, MAX_TOKENS
from .channel_dna import load_dna
from .learning import load_learning_profile

# ─── Anti-AI-tell word list ────────────────────────────────────────────────────
AI_BANNED = [
    "delve", "delving", "in conclusion", "in summary", "it's worth noting",
    "it is important to note", "furthermore", "moreover", "additionally",
    "this is crucial", "this is essential", "as we explore", "let's explore",
    "let's dive into", "dive deep", "embark on", "journey", "tapestry",
    "landscape", "paradigm", "utilize", "leverage", "synergy", "holistic",
    "game-changer", "at the end of the day", "the fact of the matter",
    "in today's world", "in today's fast-paced world", "ever-evolving",
    "shed light on", "it goes without saying", "needless to say",
    "without further ado", "stay tuned", "make sure to like and subscribe",
    "hit that bell", "transformative", "revolutionize", "unprecedented",
]

# ─── Retention architecture ────────────────────────────────────────────────────
RETENTION_BLUEPRINT = """
## RETENTION ENGINEERING — MANDATORY RULES

### Visual Change Cadence
Every 5-6 seconds of spoken content must have a [VISUAL] tag.
At ~150 words/min that's roughly every 12-15 words of spoken text.
Each [VISUAL] tag tells the editor exactly what to show.
Format: [VISUAL: description of shot/graphic/text/b-roll]

### Hook Architecture (first 30 seconds — do or die)
1. OPEN HOOK: First line must be a pattern interrupt. Start MID-THOUGHT or with a bold
   claim, a question that creates dread/desire, or a surprising fact. Never start with
   "Hey guys" or "Welcome back." No channel intro until AFTER the first hook lands.
2. TEASE: Within 10 seconds, tell them what they'll get and why they CANNOT stop watching.
   Create an open loop — a question they NEED answered.
3. CREDENTIAL DROP: 15-20 seconds in, one sentence on why they should trust you.
   Make it casual, not a resume recitation.

### Re-Hook System (prevent drop-off at 30s, 2min, 5min, 8min marks)
Place a [RE-HOOK] at each of these timestamps. A re-hook is:
- A callback to the open loop ("remember what I said about X...")
- A new question that creates fresh curiosity
- A teaser for what's coming up next ("and in 60 seconds I'm going to show you Y")
- A surprising pivot or reveal

### Pattern Interrupt Toolkit (use all of these)
- [ZOOM] — sudden zoom for emphasis
- [SMASH CUT] — abrupt cut to different scene/angle
- [TEXT ON SCREEN: exact words] — words pop on screen
- [GRAPHIC: description] — chart, diagram, callout
- [SOUND EFFECT: type] — whoosh, ding, record scratch
- [REACTION] — creator reacts directly to camera
- [B-ROLL: description] — cutaway footage
- [VISUAL: description] — general visual change

### Open Loop Technique
Plant 2-3 open loops in the first 2 minutes (questions or promises).
Close each loop at strategic points — never too early.
The last loop closes only at the very end, right before CTA.

### Pacing Rules
- Sentences in the script: max 15 words each. Then break.
- Use incomplete sentences for emphasis. Like this.
- Vary sentence length violently. Short. Medium length for context. Short again.
- Read it aloud — if you'd need a breath, add a comma or [PAUSE].
- No paragraph longer than 4 lines of spoken text.

### Anti-AI Tells — BANNED WORDS AND PHRASES
NEVER use any of these: """ + ", ".join(f'"{w}"' for w in AI_BANNED) + """

### What a human YouTuber actually says instead:
- Not "In conclusion" → just end the point and move on
- Not "Furthermore" → "Also—" or just start the next thought
- Not "It's worth noting" → just say the thing
- Not "Let's dive in" → start with the content
- Not "Make sure to like and subscribe" → use the creator's actual CTA phrasing
- Not "In today's video" → creator already said what the video is; don't repeat
- Opinions are good: "I think", "honestly", "look—", "here's the thing"
- Specific beats vague: "3 hours" not "some time", "$47" not "some money"
"""

SCRIPT_SYSTEM = """You are the best YouTube scriptwriter alive. You've written for creators
with 10M+ subscribers across every niche. You understand human psychology, attention spans,
and exactly why people click away — and how to stop them.

You write scripts that:
- Sound 100% human — like the creator sat down and just TALKED
- Keep viewers watching with ironclad retention architecture
- Never, ever sound like AI wrote them
- Make editors' lives easy with precise visual direction
- Land the creator's personality in every single line

{dna_block}

{learning_block}

{retention_rules}

## SCRIPT FORMAT
Use this exact structure with timestamps:

[0:00 — HOOK]
(first spoken words — NO channel intro yet)

[0:15 — OPEN LOOP PLANTED]
(tease what they're about to learn, create the question in their mind)

[0:30 — CHANNEL INTRO]
(one sentence max — quick, casual, then straight back into content)

[RE-HOOK @ ~2:00]
(callback + new hook before anyone can click away)

[SECTION TITLE — chapter title for editor]
(content body)

[RE-HOOK @ ~5:00]
... (continue for remaining re-hooks)

[FINAL REVEAL]
(close the last open loop here)

[CTA]
(creator's exact CTA phrasing — not generic)

[OUTRO]
(creator's exact sign-off)

At the end, add:
## EDITOR NOTES
- Total word count and estimated runtime
- Key b-roll shots needed
- Any graphics or animations required
- Thumbnail moment (the most visual/emotional point in the video)
"""


def generate_script(
    topic: str,
    duration_minutes: int = 10,
    style: str = "educational",
    audience: str = "",
    key_points: list[str] | None = None,
    research_notes: str = "",
) -> str:
    """Stream a world-class YouTube script with full retention engineering. Returns full text."""
    client = get_client()
    dna = load_dna()

    dna_block = dna.to_prompt_block() if not dna.is_empty() else (
        "## CREATOR VOICE\n"
        "No channel DNA set up yet. Write in a natural, direct, conversational human voice. "
        "Run `python main.py setup` to personalize the voice to this creator."
    )

    learning_block = load_learning_profile()

    audience_line = audience or (dna.audience if not dna.is_empty() else "general YouTube audience")
    target_words = duration_minutes * 150

    points_section = ""
    if key_points:
        points_list = "\n".join(f"  - {p}" for p in key_points)
        points_section = f"\nKey points to cover (weave in naturally — not as a listicle unless style demands it):\n{points_list}"

    research_section = ""
    if research_notes:
        research_section = f"\n\n## RESEARCH TO INCORPORATE\nUse these verified facts and sources in the script:\n{research_notes}"

    system = SCRIPT_SYSTEM.format(
        dna_block=dna_block,
        learning_block=learning_block,
        retention_rules=RETENTION_BLUEPRINT,
    )

    style_guidance = {
        "educational": "teach one clear thing, use the 'explain then show' rhythm",
        "entertainment": "pure entertainment — laughs and surprises over information",
        "tutorial": "step-by-step but make each step feel like a reveal not a manual",
        "storytime": "narrative arc with tension — failure, lesson, redemption",
        "review": "verdict first, then proof — never bury the lede",
        "vlog": "conversational and intimate — viewer is a friend riding shotgun",
        "documentary": "high stakes narrative — facts feel like a thriller",
        "rant": "passionate and opinionated — hold nothing back",
    }

    user_message = f"""Write a complete, ready-to-record YouTube script.

TOPIC: {topic}
STYLE: {style} — {style_guidance.get(style, style)}
DURATION: {duration_minutes} minutes (~{target_words} words of spoken content)
AUDIENCE: {audience_line}{points_section}{research_section}

Critical requirements:
1. Every 5-6 seconds of spoken content needs a [VISUAL] or [B-ROLL] or pattern interrupt tag
2. Place [RE-HOOK] sections at the ~2 min, ~5 min{', ~8 min' if duration_minutes >= 10 else ''} marks
3. Plant 2-3 open loops in the first 90 seconds
4. ZERO words from the banned list
5. Sound like a specific human person said every single word — not AI
6. Include precise [TEXT ON SCREEN] tags for any key points worth emphasizing
7. Start the script IMMEDIATELY — no preamble, no "Here is the script:"

Begin with the first spoken word."""

    print("\n" + "=" * 60)
    print(f"SCRIPT: {topic}")
    print(f"Style: {style}  |  Duration: ~{duration_minutes} min  |  Voice: {dna.channel_name or 'default'}")
    print("=" * 60 + "\n")

    full_script = ""

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        showing_response = False

        for event in stream:
            if event.type == "content_block_start":
                block = event.content_block
                if block.type == "thinking":
                    print("[Building your script...]\n")
                elif block.type == "text":
                    showing_response = True

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "text_delta" and showing_response:
                    print(delta.text, end="", flush=True)
                    full_script += delta.text

    print("\n")
    return full_script
