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

PLONE5=5.2.7
PLONE6=6.0.0a4

PACKAGE_NAME=kitconcept.contentcreator
PACKAGE_PATH=src/
CHECK_PATH=setup.py $(PACKAGE_PATH)

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

bin/pip:
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)"
	python3 -m venv .
	bin/pip install -U pip wheel

bin/black:
	bin/pip install black

bin/isort:
	bin/pip install isort

bin/flakeheaven:
	bin/pip install flakeheaven

.PHONY: build-plone-5.2
build-plone-5.2: bin/pip ## Build Plone 5.2
	@echo "$(GREEN)==> Build with Plone 5.2$(RESET)"
	bin/pip install Plone plone.app.testing -c https://dist.plone.org/release/$(PLONE5)/constraints.txt
	bin/pip install -e ".[test]"
	bin/mkwsgiinstance -d . -u admin:admin

.PHONY: build-plone-6.0
build-plone-6.0: bin/pip ## Build Plone 6.0
	@echo "$(GREEN)==> Build with Plone 6.0$(RESET)"
	bin/pip install Plone plone.app.testing -c https://dist.plone.org/release/$(PLONE6)/constraints.txt
	bin/pip install -e ".[test]"
	bin/mkwsgiinstance -d . -u admin:admin

.PHONY: build
build: build-plone-6.0 ## Build Plone 6.0

.PHONY: clean
clean: ## Remove old virtualenv and creates a new one
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	rm -rf bin lib lib64 include share etc var inituser pyvenv.cfg .installed.cfg

.PHONY: black
black: bin/black ## Format codebase
	./bin/black $(CHECK_PATH)

.PHONY: isort
isort: bin/isort ## Format imports in the codebase
	./bin/isort $(CHECK_PATH)

.PHONY: format
format: black isort ## Format the codebase according to our standards

.PHONY: lint
lint: lint-isort lint-black lint-flake8 ## check style with flake8

.PHONY: lint-flake8
lint-flake8: bin/flakeheaven ## validate black formating
	./bin/flakeheaven lint $(CHECK_PATH)


.PHONY: lint-black
lint-black: bin/black ## validate black formating
	./bin/black --check --diff $(CHECK_PATH)

.PHONY: lint-isort
lint-isort: bin/isort ## validate using isort
	./bin/isort --check-only $(CHECK_PATH)

.PHONY: test
test: ## run tests
	PYTHONWARNINGS=ignore ./bin/zope-testrunner --auto-color --auto-progress --test-path $(PACKAGE_PATH)

.PHONY: start
start: ## Start a Plone instance on localhost:8080
	PYTHONWARNINGS=ignore ./bin/runwsgi etc/zope.ini
