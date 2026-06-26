#!/usr/bin/env python3
"""YouTube Creator App — AI-powered script generation and idea validation."""

import argparse
import sys


def cmd_validate(args: argparse.Namespace) -> None:
    from youtube_creator.validate_idea import validate_and_improve
    validate_and_improve(idea=args.idea, niche=args.niche or "")


def cmd_script(args: argparse.Namespace) -> None:
    from youtube_creator.generate_script import generate_script
    key_points = args.points.split(",") if args.points else None
    generate_script(
        topic=args.topic,
        duration_minutes=args.duration,
        style=args.style,
        audience=args.audience or "",
        key_points=key_points,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube-creator",
        description="AI-powered YouTube creator tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # validate subcommand
    p_validate = sub.add_parser("validate", help="Validate and improve a video idea")
    p_validate.add_argument("idea", help="Your video idea (put it in quotes)")
    p_validate.add_argument("--niche", help="Your channel niche or focus area", default="")
    p_validate.set_defaults(func=cmd_validate)

    # script subcommand
    p_script = sub.add_parser("script", help="Generate a full video script")
    p_script.add_argument("topic", help="Video topic or title (put it in quotes)")
    p_script.add_argument(
        "--duration", type=int, default=10, help="Target duration in minutes (default: 10)"
    )
    p_script.add_argument(
        "--style",
        default="educational",
        choices=["educational", "entertainment", "tutorial", "storytime", "review", "vlog"],
        help="Video style (default: educational)",
    )
    p_script.add_argument("--audience", default="", help="Target audience description")
    p_script.add_argument(
        "--points", default="", help="Key points to cover, comma-separated"
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
