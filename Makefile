# Config
# ======
# This section contains various special targets and variables that affect the behavior
# of make.

# Delete targets that fail (to prevent subsequent attempts to make incorrectly
# assuming the target is up to date). Especially useful with the envoy pattern.
.DELETE_ON_ERROR: ;

SHELL=/bin/bash


# Definitions
# ===========
# This section contains reusable functionality such as
# * Macros (or _recursively expanded variables_)
# * Constants (or _simply expanded variables_)

CLEAN_DIR_TARGET = git clean -xdf $(@D); mkdir -p $(@D)


## Verbs
## =====
# This section contains targets that
# * May have side effect
# * Should not have side effects should not affect nouns

## Print this help message
help:
	@mkhelp print_docs $(firstword $(MAKEFILE_LIST)) help

## Run all checks that have not yet passed
check_all: check_format check_types check_lint check_dist check_docs check_tests
	rm $^

## _
check_format:
	isort --check kindly_aliases.pyl src/ tests/
	black --check kindly_aliases.pyl src/ tests/
	touch $@

## _
check_lint:
	pylint src/ tests/
	flake8 src/ tests/
	touch $@

# TODO: Consider moving into tox for cases where non-universal wheels are built for more than one target
## Check that distribution can be built and will render correctly on PyPi
check_dist: dist/_envoy;
	touch $@

## Check that documentation can be built
check_docs:
	touch $@

# No coverage here to avoid race conditions?
## Check that unit tests pass in reference environment
check_tests:
	pytest --durations=10 --doctest-modules src/kindly tests/
	touch $@

## Check that unit tests pass in all supported environments
check_tests_all:
	tox
	touch $@

## _
check_types:
	mypy \
		--cobertura-xml-report=reports/type_coverage/ \
		--html-report=reports/type_coverage/html/ \
		--package kindly
	touch $@

## Install dev dependencies into the current environment
sync_env:
	poetry install --sync

## Nouns
## =====
# This section contains targets that
# * Should have no side effects
# * Must have no side effects on other nouns
# * Must not have any prerequisites that are verbs
# * Ordered first by specificity, second by name

constraints.txt: poetry.lock
	poetry export \
		--format=constraints.txt \
		--output=$@ \
		--with dev \
		--without-hashes

dist/_envoy:
	$(CLEAN_DIR_TARGET)
	poetry build

reports/test_coverage/.coverage: $(wildcard .coverage.*)
	coverage combine --keep --data-file=$@ $^

reports/test_coverage/html/index.html: reports/test_coverage/.coverage
	coverage html --data-file=$< --directory=$(@D)

reports/test_coverage/coverage.xml: reports/test_coverage/.coverage
	coverage xml --data-file=$< -o $@
