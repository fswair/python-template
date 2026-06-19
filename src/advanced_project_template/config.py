from __future__ import annotations

from pathlib import Path

import yaml

from .models import (
    HelperPackage,
    TemplateConfig,
    cli_name_from_project,
    docs_site_url_from_owner_project,
    package_name_from_project,
    repo_url_from_owner_project,
)

__all__ = ["config_to_dict", "default_config", "load_config", "write_config"]


def default_config(profile: str = "full") -> TemplateConfig:
    if profile == "thin":
        return TemplateConfig(
            profile="thin",
            include_docs=False,
            include_github=False,
            include_pre_commit=False,
            include_examples=False,
            include_release=False,
            include_rename_script=False,
            include_security=False,
            include_agent_files=False,
        )
    if profile == "base":
        return TemplateConfig(
            profile="base",
            include_docs=False,
            include_examples=False,
            include_release=False,
            include_rename_script=False,
        )
    if profile != "full":
        raise ValueError("profile must be one of 'thin', 'base', or 'full'")
    return TemplateConfig(profile="full")


def _as_mapping(value: object, context: str) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a YAML mapping")
    return {str(key): item for key, item in value.items()}


def _as_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ValueError(f"Expected boolean value, got {value!r}")


def _as_str(value: object, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected string value, got {value!r}")


def _helper_packages(raw: object) -> tuple[HelperPackage, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ValueError("helper_packages must be a YAML list")

    helpers: list[HelperPackage] = []
    for item in raw:
        if isinstance(item, str):
            helpers.append(HelperPackage.from_name(item))
            continue
        mapping = _as_mapping(item, "helper package")
        project_name = _as_str(mapping.get("project_name"), "")
        if not project_name:
            project_name = _as_str(mapping.get("name"), "")
        if not project_name:
            raise ValueError("helper package requires project_name or name")
        helpers.append(
            HelperPackage(
                project_name=project_name,
                package_name=_as_str(
                    mapping.get("package_name"),
                    HelperPackage.from_name(project_name).package_name,
                ),
                description=_as_str(mapping.get("description"), "Helper package."),
            )
        )
    return tuple(helpers)


def config_to_dict(config: TemplateConfig) -> dict[str, object]:
    return {
        "project": {
            "name": config.project_name,
            "package": config.package_name,
            "cli": config.cli_name,
            "description": config.description,
            "author_name": config.author_name,
            "author_email": config.author_email,
            "version": config.version,
            "license": config.license,
        },
        "repository": {
            "owner": config.repo_owner,
            "url": config.repo_url,
            "docs_site_url": config.docs_site_url,
        },
        "features": {
            "profile": config.profile,
            "cli": config.include_cli,
            "docs": config.include_docs,
            "tests": config.include_tests,
            "github": config.include_github,
            "pre_commit": config.include_pre_commit,
            "examples": config.include_examples,
            "release": config.include_release,
            "rename_script": config.include_rename_script,
            "security": config.include_security,
            "agent_files": config.include_agent_files,
            "packages": config.include_packages,
        },
        "helper_packages": [
            {
                "project_name": helper.project_name,
                "package_name": helper.package_name,
                "description": helper.description,
            }
            for helper in config.helper_packages
        ],
    }


def config_from_mapping(raw: dict[str, object]) -> TemplateConfig:
    features = _as_mapping(raw.get("features"), "features")
    profile = _as_str(features.get("profile"), "full")
    base = default_config(profile)
    project = _as_mapping(raw.get("project"), "project")
    repository = _as_mapping(raw.get("repository"), "repository")
    include_agent_files = _as_bool(features.get("agent_files"), base.include_agent_files)
    security_default = True if include_agent_files else base.include_security
    project_name = _as_str(project.get("name"), base.project_name)
    package_name = _as_str(project.get("package"), package_name_from_project(project_name))
    cli_name = _as_str(project.get("cli"), cli_name_from_project(project_name))
    repo_owner = _as_str(repository.get("owner"), base.repo_owner)

    config = base.with_updates(
        project_name=project_name,
        package_name=package_name,
        cli_name=cli_name,
        description=_as_str(project.get("description"), base.description),
        author_name=_as_str(project.get("author_name"), base.author_name),
        author_email=_as_str(project.get("author_email"), base.author_email),
        version=_as_str(project.get("version"), base.version),
        license=_as_str(project.get("license"), base.license),
        repo_owner=repo_owner,
        repo_url=_as_str(
            repository.get("url"), repo_url_from_owner_project(repo_owner, project_name)
        ),
        docs_site_url=_as_str(
            repository.get("docs_site_url"),
            docs_site_url_from_owner_project(repo_owner, project_name),
        ),
        include_cli=_as_bool(features.get("cli"), base.include_cli),
        include_docs=_as_bool(features.get("docs"), base.include_docs),
        include_tests=_as_bool(features.get("tests"), base.include_tests),
        include_github=_as_bool(features.get("github"), base.include_github),
        include_pre_commit=_as_bool(features.get("pre_commit"), base.include_pre_commit),
        include_examples=_as_bool(features.get("examples"), base.include_examples),
        include_release=_as_bool(features.get("release"), base.include_release),
        include_rename_script=_as_bool(features.get("rename_script"), base.include_rename_script),
        include_security=_as_bool(features.get("security"), security_default),
        include_agent_files=include_agent_files,
        include_packages=_as_bool(features.get("packages"), base.include_packages),
        helper_packages=_helper_packages(raw.get("helper_packages")),
    )
    config.validate()
    return config


def load_config(path: Path) -> TemplateConfig:
    raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw = _as_mapping(raw_data, str(path))
    return config_from_mapping(raw)


def write_config(config: TemplateConfig, path: Path) -> None:
    path.write_text(
        yaml.safe_dump(config_to_dict(config), sort_keys=False),
        encoding="utf-8",
    )
