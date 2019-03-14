# convenience makefile to boostrap & run buildout
SHELL := /bin/bash
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

version = 2.7

all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: bin/buildout *.cfg
	@echo "$(GREEN)==> Setup Build$(RESET)"
	bin/buildout

.PHONY: build-travis
build-travis: bin/buildout *.cfg
	@echo "$(GREEN)==> Setup Build$(RESET)"
	bin/buildout -c travis.cfg

bin/buildout: bin/pip
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)"
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	@touch -c $@

bin/python bin/pip:
	virtualenv --clear --python=python$(version) .

.PHONY: clean
clean: ## Clean env and build
	rm -rf bin lib include share .Python parts .installed.cfg
	git clean -Xdf

.PHONY: test
test: ## Run tests
	bin/test

.PHONY: test-acceptance
test-acceptance: ## Run acceptance tests
	@echo "$(GREEN)==> Run Acceptance Tests$(RESET)"
	bin/test-acceptance

.PHONY: code-analysis
code-analysis: ## Run static code analysis
	@echo "$(GREEN)==> Run static code analysis$(RESET)"
	bin/code-analysis

.PHONY: all clean
