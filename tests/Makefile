# Get this file's directory, allows this Makefile to be run on its own or via
# `include` from a root Makefile. From:
# https://www.systutorials.com/how-to-get-a-makefiles-directory-for-including-other-makefiles/
SELF_DIR = $(dir $(lastword $(MAKEFILE_LIST)))

# No Docker image available for this yet. Refer to the CI config to configure this for
# local use.
TEST = poetry run pytest
TESTS_DIR = tests

.PHONY: test test-self test-pdfs

define run_test
	cd $(SELF_DIR) && \
		$(TEST) $(TESTS_DIR)/$(subst -,_,$(1)).py $(TEST_FLAGS)
endef

ifdef CI
	TEST_FLAGS = --verbose
else
	TEST_FLAGS =
endif

test: test-modules test-config test-properties test-build-py test-institutions test-negative test-edge-cases test-unicode test-visual-regression
	@echo "All tests passed."

# Target names correspond to actual Python test files, with some modifications made, see
# the `run_test` function.

test-modules:
	@$(call run_test,modules)

test-config:
	@$(call run_test,config)

test-properties:
	@$(call run_test,properties)

test-build-py:
	@$(call run_test,build_py)

test-institutions:
	@$(call run_test,institutions)

test-negative:
	@$(call run_test,negative)

test-edge-cases:
	@$(call run_test,edge_cases)

test-unicode:
	@$(call run_test,unicode)

test-visual-regression:
	@$(call run_test,visual_regression)
