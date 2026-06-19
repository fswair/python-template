BLUE := \033[1;34m
GREEN := \033[1;32m
RESET := \033[0m

.PHONY: tests format check-formatted check check-version docs serve pre-commit all prod rename

# Hack to allow passing arguments to make commands (e.g. make rename my_project)
ifeq (rename,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "rename"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

rename:
	@if [ -z "$(RUN_ARGS)" ]; then \
		echo "Error: Name is not provided. Usage: make rename my_awesome_project"; \
		exit 1; \
	fi
	@printf "$(BLUE)==>$(RESET) Renaming advanced_project_template to $(RUN_ARGS)...\n"
	@python3 scripts/rename_workspace.py $(RUN_ARGS) || python scripts/rename_workspace.py $(RUN_ARGS)
	@printf "$(GREEN)✔ Project renamed to $(RUN_ARGS) successfully!$(RESET)\n"

format:
	@printf "$(BLUE)==>$(RESET) Formatting code with ruff...\n"
	@uv run --extra dev ruff format
	@printf "$(GREEN)✔ Formatting complete.$(RESET)\n"

check-formatted:
	@printf "$(BLUE)==>$(RESET) Checking formatting with ruff format --check...\n"
	@uv run --extra dev ruff format --check
	@printf "$(GREEN)✔ Formatting check complete.$(RESET)\n"

check:
	@printf "$(BLUE)==>$(RESET) Running ruff checks...\n"
	@uv run --extra dev ruff check
	@printf "$(BLUE)==>$(RESET) Type checking with ty...\n"
	@uv run --extra dev ty check
	@printf "$(BLUE)==>$(RESET) Type checking with basedpyright...\n"
	@uv run --extra dev basedpyright src tests examples scripts
	@printf "$(GREEN)✔ Checking complete.$(RESET)\n"

check-version:
	@printf "$(BLUE)==>$(RESET) Checking version consistency...\n"
	@python3 scripts/check_version.py
	@printf "$(GREEN)✔ Version check complete.$(RESET)\n"

tests:
	@printf "$(BLUE)==>$(RESET) Running tests with pytest...\n"
	@uv run --extra dev pytest
	@printf "$(GREEN)✔ Tests complete.$(RESET)\n"

docs:
	@printf "$(BLUE)==>$(RESET) Building docs with mkdocs --strict...\n"
	@uv run --extra docs mkdocs build --strict
	@printf "$(GREEN)✔ Docs build complete.$(RESET)\n"

serve:
	@printf "$(BLUE)==>$(RESET) Serving docs with mkdocs...\n"
	@uv run --extra docs mkdocs serve --dev-addr 127.0.0.1:8080

pre-commit:
	@printf "$(BLUE)==>$(RESET) Running pre-commit checks...\n"
	@uv run --extra dev pre-commit run --all-files
	@printf "$(GREEN)✔ Pre-commit checks complete.$(RESET)\n"

all: format check

prod: check-formatted check check-version tests docs
