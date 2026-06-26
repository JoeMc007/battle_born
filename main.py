#!/usr/bin/env python3
"""YouTube Creator App — AI-powered script generation and idea validation."""

import argparse
import sys


# ── Command handlers ──────────────────────────────────────────────────────────

def cmd_setup(args: argparse.Namespace) -> None:
    from youtube_creator.channel_dna import setup_dna_interactive
    setup_dna_interactive()


def cmd_validate(args: argparse.Namespace) -> None:
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.projects import create_project
    from youtube_creator.idea_vault import add_idea, _load
    create_project(args.idea, args.niche or "")
    validate_and_improve(idea=args.idea, niche=args.niche or "")


def cmd_research(args: argparse.Namespace) -> None:
    from youtube_creator.research import research_idea
    research_idea(idea=args.idea, niche=args.niche or "")


def cmd_workflow(args: argparse.Namespace) -> None:
    """Run the full validate → research pipeline."""
    from youtube_creator.validate_idea import validate_and_improve
    from youtube_creator.research import research_idea
    from youtube_creator.projects import create_project
    from youtube_creator.idea_vault import add_idea

    create_project(args.idea, args.niche or "")

    print("\n" + "█" * 60)
    print("  STEP 1 OF 2 — IDEA VALIDATION")
    print("█" * 60)
    validate_and_improve(idea=args.idea, niche=args.niche or "")

    print("\n" + "█" * 60)
    print("  STEP 2 OF 2 — RESEARCH")
    print("█" * 60)
    research_idea(idea=args.idea, niche=args.niche or "")

    # Auto-save idea to vault after full workflow
    add_idea(idea=args.idea, niche=args.niche or "", source="validated", tags=["workflow"])
    print(f"\n✓ Idea saved to vault. Run 'python main.py script \"{args.idea}\"' when ready.")


def cmd_script(args: argparse.Namespace) -> None:
    from youtube_creator.generate_script import generate_script
    from youtube_creator.projects import save_stage, load_stage
    from youtube_creator.idea_vault import get_ideas, update_idea
    from youtube_creator.learning import collect_feedback, regenerate_learning_profile

    key_points = [p.strip() for p in args.points.split(",")] if args.points else None

    research_notes = ""
    if args.research_file:
        try:
            with open(args.research_file) as f:
                research_notes = f.read()
        except FileNotFoundError:
            print(f"Warning: research file '{args.research_file}' not found.")
    elif not args.no_project:
        # Auto-load research from project if it exists
        saved = load_stage(args.topic, "research")
        if saved:
            research_notes = saved
            print("[Loaded research from project]")

    script_text = generate_script(
        topic=args.topic,
        duration_minutes=args.duration,
        style=args.style,
        audience=args.audience or "",
        key_points=key_points,
        research_notes=research_notes,
    )

    # Save to project
    if script_text and not args.no_project:
        path = save_stage(args.topic, "script", script_text)
        print(f"✓ Script saved → {path}")

        # Update vault status if idea exists there
        from youtube_creator.idea_vault import _load as vault_load
        vault = vault_load()
        for entry in vault:
            if entry["idea"].lower() == args.topic.lower():
                update_idea(entry["id"], status="scripted")
                break

    # Auto-export for ElevenLabs if requested
    if getattr(args, "export_elevenlabs", False) and script_text and not args.no_project:
        from youtube_creator.elevenlabs_export import export_for_elevenlabs
        print("\n" + "─" * 60)
        print("Auto-exporting for ElevenLabs...")
        export_for_elevenlabs(topic=args.topic, script_text=script_text)

    # Collect feedback and update learning profile
    if not args.no_feedback and script_text:
        result = collect_feedback(args.topic)
        if result:
            regenerate_learning_profile()


def cmd_visuals(args: argparse.Namespace) -> None:
    from youtube_creator.visual_prompts import generate_visual_prompts
    generate_visual_prompts(
        topic=args.topic,
        visual_style=args.style,
        sentences_per_chunk=args.chunk,
        broll_count=args.broll,
        output_file=args.output or "",
    )


def cmd_export(args: argparse.Namespace) -> None:
    from youtube_creator.elevenlabs_export import export_for_elevenlabs
    export_for_elevenlabs(
        topic=args.topic,
        output_file=args.output or "",
        polish=not args.no_polish,
    )


def cmd_learn(args: argparse.Namespace) -> None:
    """Manually trigger a learning profile regeneration."""
    from youtube_creator.learning import regenerate_learning_profile, print_learning_summary
    regenerate_learning_profile()
    print_learning_summary()


def cmd_projects(args: argparse.Namespace) -> None:
    from youtube_creator.projects import print_project_list, get_project, delete_project
    if args.project_action == "list" or not args.project_action:
        print_project_list()
    elif args.project_action == "show":
        p = get_project(args.name)
        if p:
            import json
            print(json.dumps(p, indent=2))
        else:
            print(f"No project found for: {args.name}")
    elif args.project_action == "delete":
        if delete_project(args.name):
            print(f"✓ Deleted project: {args.name}")
        else:
            print(f"No project found for: {args.name}")


def cmd_vault(args: argparse.Namespace) -> None:
    from youtube_creator.idea_vault import (
        add_idea, get_ideas, get_all, print_vault, update_idea, advance_status
    )

    action = args.vault_action

    if action == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        entry = add_idea(idea=args.idea, niche=args.niche or "", tags=tags)
        print(f"\n✓ Idea #{entry['id']} added to vault: {args.idea}")

    elif action == "list":
        ideas = get_all()
        if args.status:
            ideas = [i for i in ideas if i.get("status") == args.status]
        if args.tag:
            ideas = [i for i in ideas if args.tag in i.get("tags", [])]
        print_vault(ideas)

    elif action == "tag":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        result = update_idea(args.id, tags=tags)
        if result:
            print(f"✓ Updated tags on idea #{args.id}")
        else:
            print(f"No idea found with id {args.id}")

    elif action == "advance":
        new_status = advance_status(args.id)
        if new_status:
            print(f"✓ Idea #{args.id} → {new_status}")
        else:
            print(f"Could not advance idea #{args.id}")

    elif action == "note":
        result = update_idea(args.id, notes=args.text)
        if result:
            print(f"✓ Note saved on idea #{args.id}")
        else:
            print(f"No idea found with id {args.id}")


# ── Parser builder ────────────────────────────────────────────────────────────

def _add_idea_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("idea", help="Your video idea (put it in quotes)")
    parser.add_argument("--niche", help="Your channel niche or focus area", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube-creator",
        description="AI-powered YouTube creator tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = sub.add_parser("setup", help="Set up your Channel DNA (voice, tone, catchphrases)")
    p_setup.set_defaults(func=cmd_setup)

    # workflow
    p_workflow = sub.add_parser(
        "workflow", help="Full pipeline: validate idea → research facts (recommended)"
    )
    _add_idea_args(p_workflow)
    p_workflow.set_defaults(func=cmd_workflow)

    # validate
    p_validate = sub.add_parser("validate", help="Validate and improve a video idea")
    _add_idea_args(p_validate)
    p_validate.set_defaults(func=cmd_validate)

    # research
    p_research = sub.add_parser("research", help="Research facts, stats, and sources for an idea")
    _add_idea_args(p_research)
    p_research.set_defaults(func=cmd_research)

    # script
    p_script = sub.add_parser(
        "script", help="Generate a world-class video script with retention engineering"
    )
    p_script.add_argument("topic", help="Video topic or title (put it in quotes)")
    p_script.add_argument(
        "--duration", type=int, default=10,
        choices=[3, 5, 7, 10, 15, 20, 30],
        help="Target duration in minutes (default: 10)",
    )
    p_script.add_argument(
        "--style", default="educational",
        choices=["educational", "entertainment", "tutorial", "storytime",
                 "review", "vlog", "documentary", "rant"],
        help="Video style (default: educational)",
    )
    p_script.add_argument("--audience", default="", help="Target audience description")
    p_script.add_argument("--points", default="", help="Key points to cover, comma-separated")
    p_script.add_argument(
        "--research-file", default="", metavar="FILE",
        help="Path to a text file with research notes to incorporate",
    )
    p_script.add_argument(
        "--no-feedback", action="store_true",
        help="Skip the feedback prompt after generation",
    )
    p_script.add_argument(
        "--no-project", action="store_true",
        help="Don't save output to the project system",
    )
    p_script.add_argument(
        "--export-elevenlabs", action="store_true",
        help="Automatically export a clean ElevenLabs version after generation",
    )
    p_script.set_defaults(func=cmd_script)

    # projects
    p_projects = sub.add_parser("projects", help="View and manage video projects")
    proj_sub = p_projects.add_subparsers(dest="project_action")
    proj_sub.add_parser("list", help="List all projects")
    p_show = proj_sub.add_parser("show", help="Show project details")
    p_show.add_argument("name", help="Video idea / project name")
    p_del = proj_sub.add_parser("delete", help="Delete a project")
    p_del.add_argument("name", help="Video idea / project name")
    p_projects.set_defaults(func=cmd_projects, project_action="list")

    # vault
    p_vault = sub.add_parser("vault", help="Manage your idea vault")
    vault_sub = p_vault.add_subparsers(dest="vault_action")

    p_vadd = vault_sub.add_parser("add", help="Add an idea to the vault")
    p_vadd.add_argument("idea", help="Video idea")
    p_vadd.add_argument("--niche", default="")
    p_vadd.add_argument("--tags", default="", help="Comma-separated tags")

    p_vlist = vault_sub.add_parser("list", help="List vault ideas")
    p_vlist.add_argument("--status", default="", help="Filter by status")
    p_vlist.add_argument("--tag", default="", help="Filter by tag")

    p_vtag = vault_sub.add_parser("tag", help="Tag an idea by ID")
    p_vtag.add_argument("id", type=int, help="Idea ID")
    p_vtag.add_argument("--tags", required=True, help="Comma-separated tags")

    p_vadv = vault_sub.add_parser("advance", help="Advance idea to next pipeline stage")
    p_vadv.add_argument("id", type=int, help="Idea ID")

    p_vnote = vault_sub.add_parser("note", help="Add a note to a vault idea")
    p_vnote.add_argument("id", type=int, help="Idea ID")
    p_vnote.add_argument("text", help="Note text")

    p_vault.set_defaults(func=cmd_vault, vault_action="list")

    # visuals
    p_visuals = sub.add_parser(
        "visuals",
        help="Generate image + video prompts for every scene and B-roll (OpenArt ready)",
    )
    p_visuals.add_argument("topic", help="Video topic / project name (must have a saved script)")
    p_visuals.add_argument(
        "--style",
        default="cinematic documentary, photorealistic, shallow depth of field",
        help="Master visual style description applied to every prompt",
    )
    p_visuals.add_argument(
        "--chunk", type=int, default=3, choices=[2, 3, 4],
        help="Sentences per visual scene (default: 3)",
    )
    p_visuals.add_argument(
        "--broll", type=int, default=8,
        help="Number of B-roll prompt sets to generate (default: 8)",
    )
    p_visuals.add_argument(
        "--output", default="", metavar="FILE",
        help="Output file path (default: saved to project folder as visual_prompts.txt)",
    )
    p_visuals.set_defaults(func=cmd_visuals)

    # export
    p_export = sub.add_parser(
        "export",
        help="Export a clean spoken-only script for ElevenLabs (no directions or markers)",
    )
    p_export.add_argument("topic", help="Video topic / project name (must match your script)")
    p_export.add_argument(
        "--output", default="", metavar="FILE",
        help="Output file path (default: saved to project folder as elevenlabs.txt)",
    )
    p_export.add_argument(
        "--no-polish", action="store_true",
        help="Skip the Claude polish pass (faster, regex-only strip)",
    )
    p_export.set_defaults(func=cmd_export)

    # learn
    p_learn = sub.add_parser(
        "learn", help="Regenerate learning profile from all script feedback"
    )
    p_learn.set_defaults(func=cmd_learn)

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
