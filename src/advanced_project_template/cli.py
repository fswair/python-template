from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import default_config, load_config, write_config
from .models import (
    PROFILE_NAMES,
    HelperPackage,
    cli_name_from_project,
    docs_site_url_from_owner_project,
    package_name_from_project,
    repo_url_from_owner_project,
)
from .renderer import generate_project

__all__ = ["main"]


def _ask(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def _ask_bool(prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "1", "true"}


def _apply_args(config, args: argparse.Namespace):
    project_name = args.project_name or config.project_name
    package_name = args.package_name or config.package_name
    cli_name = args.cli_name or config.cli_name
    if args.project_name and not args.package_name:
        package_name = package_name_from_project(project_name)
    if args.project_name and not args.cli_name:
        cli_name = cli_name_from_project(project_name)
    repo_owner = args.repo_owner or config.repo_owner
    repo_url = args.repo_url or config.repo_url
    docs_site_url = args.docs_site_url or config.docs_site_url
    if (args.project_name or args.repo_owner) and not args.repo_url:
        repo_url = repo_url_from_owner_project(repo_owner, project_name)
    if (args.project_name or args.repo_owner) and not args.docs_site_url:
        docs_site_url = docs_site_url_from_owner_project(repo_owner, project_name)

    updates = {
        "project_name": project_name,
        "package_name": package_name,
        "cli_name": cli_name,
        "description": args.description or config.description,
        "author_name": args.author_name or config.author_name,
        "author_email": args.author_email or config.author_email,
        "repo_owner": repo_owner,
        "repo_url": repo_url,
        "docs_site_url": docs_site_url,
    }
    for attr, value in (
        ("include_cli", args.cli),
        ("include_docs", args.docs),
        ("include_tests", args.tests),
        ("include_github", args.github),
        ("include_pre_commit", args.pre_commit),
        ("include_examples", args.examples),
        ("include_release", args.release),
        ("include_rename_script", args.rename_script),
        ("include_security", args.security),
        ("include_agent_files", args.agent_files),
        ("include_packages", args.packages),
    ):
        if value is not None:
            updates[attr] = value
    if args.agent_files is True and args.security is None:
        updates["include_security"] = True
    helpers = tuple(HelperPackage.from_name(name) for name in args.helper_package)
    if helpers:
        updates["helper_packages"] = helpers
        updates["include_packages"] = True
    return config.with_updates(**updates)


def _interactive(config, destination: Path | None):
    project_name = _ask("Project name", config.project_name)
    if destination is None:
        destination = Path(_ask("Project directory", project_name))
    package_name = _ask("Import package", package_name_from_project(project_name))
    cli_name = _ask("CLI command", cli_name_from_project(project_name))
    repo_owner = _ask("GitHub username", config.repo_owner)
    repo_url = repo_url_from_owner_project(repo_owner, project_name)
    docs_site_url = docs_site_url_from_owner_project(repo_owner, project_name)
    include_packages = _ask_bool("Create packages/helpers workspace", config.include_packages)
    helpers: tuple[HelperPackage, ...] = ()
    if include_packages:
        raw_helpers = _ask("Helper package names, comma separated", "")
        helpers = tuple(
            HelperPackage.from_name(item.strip()) for item in raw_helpers.split(",") if item.strip()
        )
    include_agent_files = _ask_bool(
        "Open to coding agents (AGENTS.md, llms.txt)", config.include_agent_files
    )
    include_security_default = True if include_agent_files else config.include_security
    config = config.with_updates(
        project_name=project_name,
        package_name=package_name,
        cli_name=cli_name,
        repo_owner=repo_owner,
        repo_url=repo_url,
        docs_site_url=docs_site_url,
        description=_ask("Description", config.description),
        author_name=_ask("Author name", config.author_name),
        author_email=_ask("Author email", config.author_email),
        include_cli=_ask_bool("Include CLI", config.include_cli),
        include_docs=_ask_bool("Include docs", config.include_docs),
        include_tests=_ask_bool("Include tests", config.include_tests),
        include_github=_ask_bool("Include GitHub Actions", config.include_github),
        include_pre_commit=_ask_bool("Include pre-commit", config.include_pre_commit),
        include_examples=_ask_bool("Include examples", config.include_examples),
        include_release=_ask_bool("Include release helpers", config.include_release),
        include_rename_script=_ask_bool("Include rename script", config.include_rename_script),
        include_security=_ask_bool("Include SECURITY.md", include_security_default),
        include_agent_files=include_agent_files,
        include_packages=include_packages,
        helper_packages=helpers,
    )
    return config, destination


def _add_feature_args(parser: argparse.ArgumentParser) -> None:
    for name in (
        "cli",
        "docs",
        "tests",
        "github",
        "pre-commit",
        "examples",
        "release",
        "rename-script",
        "security",
        "agent-files",
        "packages",
    ):
        dest = name.replace("-", "_")
        group = parser.add_mutually_exclusive_group()
        group.add_argument(f"--enable-{name}", dest=dest, action="store_true", default=None)
        group.add_argument(f"--disable-{name}", dest=dest, action="store_false")


def _add_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-name")
    parser.add_argument("--package-name")
    parser.add_argument("--cli-name")
    parser.add_argument("--description")
    parser.add_argument("--author-name")
    parser.add_argument("--author-email")
    parser.add_argument("--repo-owner")
    parser.add_argument("--repo-url")
    parser.add_argument("--docs-site-url")
    parser.add_argument("--helper-package", action="append", default=[])
    _add_feature_args(parser)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="advanced_project_template")
    parser.add_argument("--version", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config", help="Write a starter YAML config.")
    config_parser.add_argument("path", type=Path)
    config_parser.add_argument("--profile", choices=PROFILE_NAMES, default="full")
    _add_config_args(config_parser)

    new_parser = subparsers.add_parser("new", help="Generate a new project.")
    new_parser.add_argument("destination", type=Path, nargs="?")
    new_parser.add_argument("--config", type=Path)
    new_parser.add_argument("--profile", choices=PROFILE_NAMES, default="full")
    new_parser.add_argument("--no-input", action="store_true")
    new_parser.add_argument("--force", action="store_true")
    _add_config_args(new_parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.command == "config":
        config = _apply_args(default_config(args.profile), args)
        write_config(config, args.path)
        print(f"Wrote {args.path}")
        return 0
    if args.command == "new":
        config = load_config(args.config) if args.config else default_config(args.profile)
        destination = args.destination
        if destination is not None and not args.project_name and not args.config:
            project_name = destination.name
            config = config.with_updates(
                project_name=project_name,
                package_name=package_name_from_project(project_name),
                cli_name=cli_name_from_project(project_name),
                repo_url=repo_url_from_owner_project(config.repo_owner, project_name),
                docs_site_url=docs_site_url_from_owner_project(config.repo_owner, project_name),
            )
        config = _apply_args(config, args)
        if not args.no_input:
            config, destination = _interactive(config, destination)
        if destination is None:
            destination = Path(config.project_name)
        generated = generate_project(config, destination, force=args.force)
        print(f"Generated {generated.destination} ({len(generated.files)} files)")
        return 0
    parser.print_help()
    return 0
