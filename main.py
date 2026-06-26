#!/usr/bin/env python3
"""YouTube Creator App — AI-powered script generation and idea validation."""

import argparse
import sys
from io import StringIO


def cmd_setup(args: argparse.Namespace) -> None:
    from youtube_creator.channel_dna import setup_dna_interactive
    setup_dna_interactive()


def cmd_validate(args: argparse.Namespace) -> None:
    from youtube_creator.validate_idea import validate_and_improve
    validate_and_improve(idea=args.idea, niche=args.niche or "")


def cmd_research(args: argparse.Namespace) -> None:
    from youtube_creator.research import research_idea
    research_idea(idea=args.idea, niche=args.niche or "")


def cmd_workflow(args: argparse.Namespace) -> None:
    """Run the full validate → research pipeline, then optionally generate script."""
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.research import research_idea

    print("\n" + "█" * 60)
    print("  STEP 1 OF 2 — IDEA VALIDATION")
    print("█" * 60)
    validate_and_improve(idea=args.idea, niche=args.niche or "")

    print("\n" + "█" * 60)
    print("  STEP 2 OF 2 — RESEARCH")
    print("█" * 60)
    research_idea(idea=args.idea, niche=args.niche or "")


def cmd_script(args: argparse.Namespace) -> None:
    from youtube_creator.generate_script import generate_script
    key_points = [p.strip() for p in args.points.split(",")] if args.points else None

    research_notes = ""
    if args.research_file:
        try:
            with open(args.research_file) as f:
                research_notes = f.read()
        except FileNotFoundError:
            print(f"Warning: research file '{args.research_file}' not found — continuing without it.")

    generate_script(
        topic=args.topic,
        duration_minutes=args.duration,
        style=args.style,
        audience=args.audience or "",
        key_points=key_points,
        research_notes=research_notes,
    )


def _add_idea_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("idea", help="Your video idea (put it in quotes)")
    parser.add_argument("--niche", help="Your channel niche or focus area", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube-creator",
        description="AI-powered YouTube creator tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # setup — capture channel DNA
    p_setup = sub.add_parser(
        "setup",
        help="Set up your Channel DNA (voice, tone, catchphrases, one-liner)",
    )
    p_setup.set_defaults(func=cmd_setup)

    # workflow — validate + research
    p_workflow = sub.add_parser(
        "workflow",
        help="Full pipeline: validate idea → research facts (recommended)",
    )
    _add_idea_args(p_workflow)
    p_workflow.set_defaults(func=cmd_workflow)

    # validate
    p_validate = sub.add_parser("validate", help="Validate and improve a video idea")
    _add_idea_args(p_validate)
    p_validate.set_defaults(func=cmd_validate)

    # research
    p_research = sub.add_parser(
        "research",
        help="Research facts, stats, and sources for an idea",
    )
    _add_idea_args(p_research)
    p_research.set_defaults(func=cmd_research)

    # script
    p_script = sub.add_parser(
        "script",
        help="Generate a world-class video script with retention engineering",
    )
    p_script.add_argument("topic", help="Video topic or title (put it in quotes)")
    p_script.add_argument(
        "--duration",
        type=int,
        default=10,
        choices=[3, 5, 7, 10, 15, 20, 30],
        help="Target duration in minutes (default: 10)",
    )
    p_script.add_argument(
        "--style",
        default="educational",
        choices=[
            "educational", "entertainment", "tutorial",
            "storytime", "review", "vlog", "documentary", "rant",
        ],
        help="Video style (default: educational)",
    )
    p_script.add_argument("--audience", default="", help="Target audience description")
    p_script.add_argument(
        "--points", default="", help="Key points to cover, comma-separated"
    )
    p_script.add_argument(
        "--research-file",
        default="",
        metavar="FILE",
        help="Path to a text file with research notes to incorporate",
    )
    p_script.set_defaults(func=cmd_script)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n[Interrupted]")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
