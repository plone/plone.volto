### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

BASE_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VENV_FOLDER=$(BASE_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin


# Python checks
PYTHON?=python3

# installed?
ifeq (, $(shell which $(PYTHON) ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif

# version ok?
PYTHON_VERSION_MIN=3.8
PYTHON_VERSION_OK=$(shell $(PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_VERSION_MIN)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Need python $(PYTHON_VERSION) >= $(PYTHON_VERSION_MIN)")
endif

# Set distributions still in development
DISTRIBUTIONS="volto"

all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: clean-build clean-pyc clean-test clean-venv clean-instance ## remove all build, test, coverage and Python artifacts

.PHONY: clean-instance
clean-instance: ## remove existing instance
	rm -fr instance etc inituser var

.PHONY: clean-venv
clean-venv: ## remove virtual environment
	rm -fr $(BIN_FOLDER) env pyvenv.cfg .tox .pytest_cache requirements-mxdev.txt

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

$(BIN_FOLDER)/pip $(BIN_FOLDER)/tox $(BIN_FOLDER)/mxdev:
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)"
	$(PYTHON) -m venv $(VENV_FOLDER)
	$(BIN_FOLDER)/pip install -U "pip" "pipx" "wheel" "cookiecutter" "mxdev" "tox" "pre-commit"
	$(BIN_FOLDER)/pre-commit install

.PHONY: config
config: $(BIN_FOLDER)/pip  ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	$(BIN_FOLDER)/pipx run cookiecutter -f --no-input --config-file instance.yaml gh:plone/cookiecutter-zope-instance

.PHONY: install-plone-6
install-plone-6: config ## pip install Plone packages
	@echo "$(GREEN)==> Setup Build$(RESET)"
	$(BIN_FOLDER)/mxdev -c mx.ini
	$(BIN_FOLDER)/pip install -r requirements-mxdev.txt

.PHONY: install
install: install-plone-6 ## Install Plone 6

.PHONY: start
start: ## Start a Plone instance on localhost:8080
	DEVELOP_DISTRIBUTIONS=$(DISTRIBUTIONS) PYTHONWARNINGS=ignore $(BIN_FOLDER)/runwsgi instance/etc/zope.ini

.PHONY: check
check: $(BIN_FOLDER)/tox ## Format the codebase according to our standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	$(BIN_FOLDER)/tox -e lint

# i18n
$(BIN_FOLDER)/i18ndude:	$(BIN_FOLDER)/pip
	@echo "$(GREEN)==> Install translation tools$(RESET)"
	$(BIN_FOLDER)/pip install i18ndude

.PHONY: i18n
i18n: $(BIN_FOLDER)/i18ndude ## Update locales
	@echo "$(GREEN)==> Updating locales$(RESET)"
	$(BIN_FOLDER)/update_locale

# Tests
.PHONY: test
test: $(BIN_FOLDER)/tox ## run tests
	DEVELOP_DISTRIBUTIONS=$(DISTRIBUTIONS) $(BIN_FOLDER)/tox -e test

.PHONY: test-coverage
test-coverage: $(BIN_FOLDER)/tox ## run tests with coverage
	DEVELOP_DISTRIBUTIONS=$(DISTRIBUTIONS) $(BIN_FOLDER)/tox -e coverage
