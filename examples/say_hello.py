from pathlib import Path
from tempfile import TemporaryDirectory

from advanced_project_template import default_config, generate_project


def main() -> int:
    with TemporaryDirectory() as tmp_dir:
        destination = Path(tmp_dir) / "example-project"
        generate_project(
            default_config("thin").with_updates(
                project_name="example-project",
                package_name="example_project",
                cli_name="example-project",
            ),
            destination,
        )
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
