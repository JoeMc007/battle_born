# YouTube Creator App

AI-powered CLI for YouTube creators — validate ideas, research facts, and generate
world-class scripts using Claude Opus 4.8.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## First Time: Set Up Your Channel DNA

Before generating scripts, tell the app who you are. This is what makes scripts sound
like YOU — not a generic AI.

```bash
python main.py setup
```

You'll enter:
- Your channel name and niche
- Your **one-liner** (the phrase that defines your channel)
- Your **tone** ("casual, direct, never corporate")
- Your **catchphrases** (phrases you say every video)
- Words you **never** say (AI clichés to ban)
- **Sample lines** from your actual videos (3-5 real quotes)
- Your exact **CTA phrasing** and **outro**
- Swear level (none / mild / moderate / heavy)

Channel DNA is saved to `~/.youtube_creator/channel_dna.json` and used every time
you generate a script.

---

## The Creator Workflow

```
setup (once) → workflow → script
```

### Step 1+2 combined: `workflow`

Runs idea validation and deep fact research back-to-back:

```bash
python main.py workflow "5 productivity hacks that actually work" --niche "self-improvement"
```

### Step 3: `script`

Generate a world-class script after reviewing your research.
Pass your research file to incorporate verified facts directly:

```bash
python main.py script "5 productivity hacks that actually work" \
  --duration 10 \
  --style educational \
  --audience "busy professionals aged 25-40" \
  --points "time blocking,pomodoro,deep work,batching,weekly review" \
  --research-file research.txt
```

---

## What Makes the Script Generator Different

### Retention Engineering
- **Visual change every 5-6 seconds** — `[VISUAL]`, `[B-ROLL]`, `[ZOOM]`, `[SMASH CUT]` tags
  tell your editor exactly what to cut to
- **Hook Architecture** — first line starts mid-thought or with a bold claim. No "Hey guys."
- **Re-Hook system** — `[RE-HOOK]` markers at the ~2 min, ~5 min, and ~8 min marks prevent
  drop-off at the moments viewers most commonly click away
- **Open Loops** — 2-3 open questions planted in the first 90 seconds, closed strategically
  to keep viewers watching for answers

### Zero AI Tells
50+ banned words and phrases the generator will never use:
"delve", "in conclusion", "furthermore", "let's dive in", "it's worth noting",
"game-changer", "transformative", "at the end of the day", "stay tuned", and more.

Scripts use:
- Contractions and incomplete sentences
- Direct opinions ("I think", "honestly", "here's the thing")
- Specific numbers over vague language ("3 hours" not "some time")
- Your actual catchphrases and sign-off

### Pattern Interrupt Toolkit
Every script uses the full toolkit:
| Tag | What it does |
|-----|-------------|
| `[ZOOM]` | Sudden zoom for emphasis |
| `[SMASH CUT]` | Abrupt cut to different angle |
| `[TEXT ON SCREEN: words]` | Words pop on screen |
| `[GRAPHIC: description]` | Chart, diagram, callout |
| `[SOUND EFFECT: type]` | Whoosh, ding, record scratch |
| `[REACTION]` | Direct camera reaction |
| `[B-ROLL: description]` | Cutaway footage |
| `[PAUSE]` | Dramatic breath |

### Script Lengths
`--duration` accepts: 3, 5, 7, 10, 15, 20, 30 minutes

### Script Styles
| Style | Best for |
|-------|----------|
| `educational` | Teach one clear thing (default) |
| `entertainment` | Pure entertainment — laughs and surprises |
| `tutorial` | Step-by-step with each step as a reveal |
| `storytime` | Narrative arc: failure → lesson → redemption |
| `review` | Verdict first, then proof |
| `vlog` | Conversational, viewer is a friend |
| `documentary` | High-stakes narrative, facts as a thriller |
| `rant` | Passionate, opinionated, hold nothing back |

---

## Individual Commands

```bash
# Set up your voice profile (do this first)
python main.py setup

# Full pipeline: validate → research
python main.py workflow "your idea" --niche "your niche"

# Validate an idea only
python main.py validate "your idea" --niche "your niche"

# Research only
python main.py research "your idea"

# Generate script only
python main.py script "your topic" --duration 10 --style educational
```
