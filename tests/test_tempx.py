from __future__ import annotations

from pathlib import Path

from advanced_project_template import __version__, default_config, generate_project, load_config, write_config
from advanced_project_template.cli import main
from advanced_project_template.models import HelperPackage


def test_version_is_exported() -> None:
    assert __version__ == "0.1.0"


def test_config_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "starter.yml"
    config = default_config("thin").with_updates(project_name="demo-app")

    write_config(config, path)

    loaded = load_config(path)
    assert loaded.project_name == "demo-app"
    assert loaded.profile == "thin"
    assert not loaded.include_docs
    assert not loaded.include_agent_files


def test_agent_files_enable_security_by_default_in_yaml(tmp_path: Path) -> None:
    path = tmp_path / "starter.yml"
    path.write_text("features:\n  profile: thin\n  agent_files: true\n", encoding="utf-8")

    loaded = load_config(path)

    assert loaded.include_agent_files
    assert loaded.include_security


def test_config_derives_repository_urls_from_project_and_owner(tmp_path: Path) -> None:
    path = tmp_path / "starter.yml"
    path.write_text(
        "project:\n  name: demo-app\nrepository:\n  owner: mert\n",
        encoding="utf-8",
    )

    loaded = load_config(path)

    assert loaded.package_name == "demo_app"
    assert loaded.cli_name == "demo-app"
    assert loaded.repo_owner == "mert"
    assert loaded.repo_url == "https://github.com/mert/demo-app"
    assert loaded.docs_site_url == "https://mert.github.io/demo-app/"


def test_generate_thin_project(tmp_path: Path) -> None:
    destination = tmp_path / "demo-app"
    config = default_config("thin").with_updates(
        project_name="demo-app",
        package_name="demo_app",
        cli_name="demo",
    )

    generated = generate_project(config, destination)

    assert generated.destination == destination.resolve()
    assert (destination / "pyproject.toml").exists()
    assert (destination / "src" / "demo_app" / "__init__.py").exists()
    assert (destination / "src" / "demo_app" / "cli.py").exists()
    assert (destination / "tests" / "test_demo_app.py").exists()
    assert (destination / "advanced_project_template.yml").exists()
    assert not (destination / "docs").exists()
    assert not (destination / ".github").exists()
    assert not (destination / "SECURITY.md").exists()
    assert not (destination / "AGENTS.md").exists()
    assert not (destination / "llms.txt").exists()


def test_generate_base_project_includes_agent_files_without_docs_site(tmp_path: Path) -> None:
    destination = tmp_path / "demo-app"
    config = default_config("base").with_updates(
        project_name="demo-app",
        package_name="demo_app",
        cli_name="demo",
    )

    generate_project(config, destination)

    assert (destination / "SECURITY.md").exists()
    assert (destination / "AGENTS.md").exists()
    assert (destination / "llms.txt").exists()
    assert (destination / ".github" / "workflows" / "test.yml").exists()
    assert not (destination / "mkdocs.yml").exists()
    assert not (destination / "docs" / "index.md").exists()


def test_generate_full_project_with_helper_package(tmp_path: Path) -> None:
    destination = tmp_path / "demo-app"
    config = default_config("full").with_updates(
        project_name="demo-app",
        package_name="demo_app",
        cli_name="demo",
        include_packages=True,
        helper_packages=(HelperPackage.from_name("demo-helper"),),
    )

    generate_project(config, destination)

    assert (destination / "docs" / "index.md").exists()
    assert (destination / "docs" / "llms.txt").exists()
    assert (destination / "SECURITY.md").exists()
    assert (destination / "AGENTS.md").exists()
    assert (destination / ".github" / "workflows" / "test.yml").exists()
    assert (destination / "packages" / "helpers" / "demo-helper" / "pyproject.toml").exists()
    assert (
        destination / "packages" / "helpers" / "demo-helper" / "src" / "demo_helper" / "__init__.py"
    ).exists()


def test_force_regeneration_removes_disabled_feature_files(tmp_path: Path) -> None:
    destination = tmp_path / "demo-app"
    full_config = default_config("full").with_updates(
        project_name="demo-app",
        package_name="demo_app",
    )
    thin_config = default_config("thin").with_updates(
        project_name="demo-app",
        package_name="demo_app",
    )

    generate_project(full_config, destination)
    assert (destination / "docs" / "index.md").exists()

    generate_project(thin_config, destination, force=True)

    assert (destination / "src" / "demo_app" / "__init__.py").exists()
    assert not (destination / "docs").exists()
    assert not (destination / ".github").exists()
    assert not (destination / "SECURITY.md").exists()
    assert not (destination / "AGENTS.md").exists()


def test_disabled_workflow_features_are_removed_from_makefile(tmp_path: Path) -> None:
    destination = tmp_path / "demo-app"
    config = default_config("full").with_updates(
        project_name="demo-app",
        package_name="demo_app",
        include_docs=False,
        include_tests=False,
        include_pre_commit=False,
        include_rename_script=False,
    )

    generate_project(config, destination)

    makefile = (destination / "Makefile").read_text(encoding="utf-8")
    assert "tests:" not in makefile
    assert "docs:" not in makefile
    assert "pre-commit:" not in makefile
    assert "rename:" not in makefile
    assert "prod: check-formatted check check-version\n" in makefile


def test_cli_writes_config(tmp_path: Path, capsys) -> None:
    config_path = tmp_path / "starter.yml"

    exit_code = main(["config", str(config_path), "--profile", "thin"])

    assert exit_code == 0
    assert config_path.exists()
    assert "Wrote" in capsys.readouterr().out
    assert load_config(config_path).profile == "thin"


def test_cli_writes_custom_config_with_feature_flags(tmp_path: Path) -> None:
    config_path = tmp_path / "starter.yml"

    exit_code = main(
        [
            "config",
            str(config_path),
            "--profile",
            "base",
            "--project-name",
            "custom-app",
            "--repo-owner",
            "mert",
            "--disable-security",
            "--enable-packages",
            "--helper-package",
            "custom-helper",
        ]
    )

    loaded = load_config(config_path)
    assert exit_code == 0
    assert loaded.profile == "base"
    assert loaded.project_name == "custom-app"
    assert loaded.package_name == "custom_app"
    assert loaded.cli_name == "custom-app"
    assert loaded.repo_owner == "mert"
    assert loaded.repo_url == "https://github.com/mert/custom-app"
    assert loaded.docs_site_url == "https://mert.github.io/custom-app/"
    assert not loaded.include_security
    assert loaded.include_packages
    assert loaded.helper_packages == (HelperPackage.from_name("custom-helper"),)


def test_cli_generates_non_interactive_project(tmp_path: Path, capsys) -> None:
    destination = tmp_path / "cli-app"

    exit_code = main(
        [
            "new",
            str(destination),
            "--profile",
            "thin",
            "--no-input",
            "--project-name",
            "cli-app",
            "--package-name",
            "cli_app",
            "--cli-name",
            "cli-app",
        ]
    )

    assert exit_code == 0
    assert (destination / "src" / "cli_app" / "cli.py").exists()
    loaded = load_config(destination / "advanced_project_template.yml")
    assert loaded.repo_url == "https://github.com/yourusername/cli-app"
    assert loaded.docs_site_url == "https://yourusername.github.io/cli-app/"
    assert "Generated" in capsys.readouterr().out


def test_cli_interactive_generates_project_without_destination(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    destination = tmp_path / "interactive-app"

    def fake_input(prompt: str) -> str:
        if prompt.startswith("Project name"):
            return "interactive-app"
        if prompt.startswith("Project directory"):
            return str(destination)
        if prompt.startswith("GitHub username"):
            return "mert"
        if prompt.startswith("Include docs"):
            return "n"
        if prompt.startswith("Include GitHub Actions"):
            return "n"
        if prompt.startswith("Include pre-commit"):
            return "n"
        if prompt.startswith("Include examples"):
            return "n"
        if prompt.startswith("Include release helpers"):
            return "n"
        if prompt.startswith("Include rename script"):
            return "n"
        return ""

    monkeypatch.setattr("builtins.input", fake_input)

    exit_code = main(["new"])

    assert exit_code == 0
    assert (destination / "src" / "interactive_app" / "cli.py").exists()
    assert (destination / "AGENTS.md").exists()
    assert not (destination / "docs").exists()
    loaded = load_config(destination / "advanced_project_template.yml")
    assert loaded.repo_owner == "mert"
    assert loaded.repo_url == "https://github.com/mert/interactive-app"
    assert loaded.docs_site_url == "https://mert.github.io/interactive-app/"
    assert "Generated" in capsys.readouterr().out


def test_cli_generates_from_config_without_destination(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "starter.yml"
    config = default_config("thin").with_updates(
        project_name="from-config",
        package_name="from_config",
        cli_name="from-config",
    )
    write_config(config, config_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["new", "--config", str(config_path), "--no-input"])

    assert exit_code == 0
    assert (tmp_path / "from-config" / "src" / "from_config" / "cli.py").exists()
