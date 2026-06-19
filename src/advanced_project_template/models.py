from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

PROFILE_NAMES = ("thin", "base", "full")


def package_name_from_project(project_name: str) -> str:
    normalized = project_name.strip().lower().replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "python_template"


def cli_name_from_project(project_name: str) -> str:
    normalized = project_name.strip().lower().replace("_", "-").replace(" ", "-")
    normalized = re.sub(r"[^a-z0-9_.-]", "", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "pytemp"


def repo_url_from_owner_project(repo_owner: str, project_name: str) -> str:
    return f"https://github.com/{repo_owner.strip() or 'yourusername'}/{project_name}"


def docs_site_url_from_owner_project(repo_owner: str, project_name: str) -> str:
    return f"https://{repo_owner.strip() or 'yourusername'}.github.io/{project_name}/"


def validate_import_name(value: str) -> None:
    if not value.isidentifier():
        raise ValueError(f"Invalid Python package import name: {value!r}")


def validate_project_name(value: str) -> None:
    if not value or any(part in value for part in ("/", "\\")):
        raise ValueError(f"Invalid project name: {value!r}")


@dataclass(frozen=True, slots=True)
class HelperPackage:
    project_name: str
    package_name: str
    description: str = "Helper package."

    @classmethod
    def from_name(cls, name: str) -> HelperPackage:
        project_name = name.strip().lower().replace("_", "-")
        return cls(
            project_name=project_name,
            package_name=package_name_from_project(project_name),
            description=f"Helper package for {project_name}.",
        )

    def validate(self) -> None:
        validate_project_name(self.project_name)
        validate_import_name(self.package_name)


@dataclass(frozen=True, slots=True)
class TemplateConfig:
    project_name: str = "python-template"
    package_name: str = "python_template"
    cli_name: str = "pytemp"
    description: str = "A modern Python project."
    author_name: str = "John Doe"
    author_email: str = "john@doe.com"
    version: str = "0.1.0"
    license: str = "MIT"
    repo_owner: str = "yourusername"
    repo_url: str = "https://github.com/yourusername/python-template"
    docs_site_url: str = "https://yourusername.github.io/python-template/"
    profile: str = "full"
    include_cli: bool = True
    include_docs: bool = True
    include_tests: bool = True
    include_github: bool = True
    include_pre_commit: bool = True
    include_examples: bool = True
    include_release: bool = True
    include_rename_script: bool = True
    include_security: bool = True
    include_agent_files: bool = True
    include_packages: bool = False
    helper_packages: tuple[HelperPackage, ...] = ()

    def validate(self) -> None:
        validate_project_name(self.project_name)
        validate_import_name(self.package_name)
        if self.profile not in PROFILE_NAMES:
            raise ValueError(f"profile must be one of {', '.join(PROFILE_NAMES)}")
        for helper in self.helper_packages:
            helper.validate()

    def with_updates(self, **updates: object) -> TemplateConfig:
        config = replace(self, **updates)
        config.validate()
        return config


@dataclass(frozen=True, slots=True)
class GeneratedProject:
    destination: Path
    files: tuple[Path, ...]
