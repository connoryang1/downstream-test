PROJECT := downstream

CXX ?= g++-12
CXXCLANG ?= clang++
PYTHON ?= python3

CFLAGS_all := -Wall -Wno-unused-function -std=c++20 -I.
CFLAGS_nat := -O3 -DNDEBUG $(CFLAGS_all)
CFLAGS_nat_debug := -g $(CFLAGS_all)

HEADERS := $(shell find include -name '*.hpp')

MAIN_BIN := test_downstream/test_dstream/main

default: build test

.PHONY: all clean test check debug default build run validate
all: build test validate
debug: CFLAGS_nat := $(CFLAGS_nat_debug)
debug: build

build: $(MAIN_BIN)

check:
	@echo "Checking C++20 compatibility..."
	@for file in $(HEADERS); do \
		echo "Checking $$file with GCC..."; \
		$(CXX) $(CFLAGS_nat) -fsyntax-only "$$file" || exit 1; \
		if command -v $(CXXCLANG) > /dev/null 2>&1; then \
			echo "Checking $$file with Clang..."; \
			$(CXXCLANG) $(CFLAGS_nat) -fsyntax-only "$$file" || exit 1; \
		fi \
	done
	@echo "All files pass C++20 syntax check"

$(MAIN_BIN): $(MAIN_BIN).cpp $(HEADERS)
	@mkdir -p $(dir $@)
	$(CXX) $(CFLAGS_nat) $< -o $@

validate: build
	@echo "Running validation tests..."
	@for algo in steady_algo stretched_algo tilted_algo; do \
		echo "Validating assign_storage_site with $$algo..."; \
		$(PYTHON) -m downstream.testing.validate_one \
			$(MAIN_BIN) \
			$$algo.assign_storage_site || exit 1; \
	done

clean:
	@echo "Cleaning build artifacts..."
	rm -f $(MAIN_BIN)