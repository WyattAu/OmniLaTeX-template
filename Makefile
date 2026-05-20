.PHONY: test test-fast test-slow test-lean lint format clean build build-all preflight validate-digest check-semver

PYTHON := python3
LAKE := lake
TEST_DIR := tests
PROOF_DIR := specs/proofs

test: test-fast

test-fast:
	$(PYTHON) -m pytest $(TEST_DIR)/test_modules.py $(TEST_DIR)/test_ctan.py $(TEST_DIR)/test_properties.py $(TEST_DIR)/test_visual_regression.py $(TEST_DIR)/test_build_py.py $(TEST_DIR)/test_institutions.py $(TEST_DIR)/test_negative.py $(TEST_DIR)/test_config.py $(TEST_DIR)/test_edge_cases.py $(TEST_DIR)/test_unicode.py -v --timeout=60 -m "not slow" --tb=short

test-slow:
	$(PYTHON) -m pytest $(TEST_DIR)/ -v --timeout=300 --tb=short

test-lean:
	cd $(PROOF_DIR) && $(LAKE) build

lint:
	black --check tests/*.py
	isort --check --profile black tests/*.py
	flake8 tests/*.py --max-line-length=100 --extend-ignore=E203,W503

format:
	black tests/*.py
	isort --profile black tests/*.py

clean:
	find . -name "*.aux" -delete
	find . -name "*.log" -delete
	find . -name "*.toc" -delete
	find . -name "*.lof" -delete
	find . -name "*.lot" -delete
	find . -name "*.out" -delete
	find . -name "*.bbl" -delete
	find . -name "*.bcf" -delete
	find . -name "*.blg" -delete
	find . -name "*.run.xml" -delete
	find . -name "*.fls" -delete
	find . -name "*.fdb_latexmk" -delete
	find . -name "main.pdf" -delete
	find . -name "texput.pdf" -delete
	rm -rf build/ _minted/ .pytest_cache/ .hypothesis/ .ruff_cache/

build:
	$(PYTHON) build.py build-root

build-all:
	$(PYTHON) build.py build-examples

preflight: test-fast test-lean lint
	@echo "All preflight checks passed."

validate-digest: ## Validate Docker digest consistency across CI configs
	@python3 scripts/validate-digest-consistency.py

check-semver: ## Validate semantic versioning consistency
	@python3 scripts/check_semver.py
