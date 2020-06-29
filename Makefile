LINTER_SRC := ./setup.py ./src ./tests

.PHONY: all
all: build test linter

.PHONY: build
build:
	@echo "Build the package"
	@python ./setup.py sdist bdist_wheel

.PHONY: test
test:
	@echo "Run the tests"
	@pytest ./tests

.PHONY: linter
linter: black flake8 mypy

.PHONY: black
black:
	@echo "Check black"
	@black -l 120 --check $(LINTER_SRC)

.PHONY: flake8
flake8:
	@echo "Check flake8"
	@flake8 $(LINTER_SRC)

.PHONY: mypy
mypy:
	@echo "Check mypy"
	@mypy $(LINTER_SRC)
