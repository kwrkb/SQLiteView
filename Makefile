PYTHON ?= python3
VENV ?= .venv
PIP ?= $(VENV)/bin/pip
PYTEST ?= $(VENV)/bin/pytest
PACKAGE_NAME ?= sqliteviewer

venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

install: venv ## Create a virtual environment and install dependencies.

lint: ## Run static checks.
	$(PYTHON) -m compileall src

fmt: ## Placeholder for formatting (no-op for now).
	@echo "Nothing to format—Python code follows PEP 8 by construction."

build: ## Build wheel and sdist packages.
	$(PYTHON) -m build

package: ## Build Debian package into dist/.
	./scripts/build_deb.sh

test: ## Run the full pytest suite.
	$(PYTHON) -m pytest

clean: ## Remove build artifacts.
	rm -rf build dist *.egg-info $(VENV)

help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; { printf "%-10s %s\n", $$1, $$2 }'

.PHONY: venv install lint fmt build package test clean help
