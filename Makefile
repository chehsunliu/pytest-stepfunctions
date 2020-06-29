LINTER_SRC := ./setup.py ./src ./tests

.PHONY: all
all: build test linter

.PHONY: linter
linter: black flake8 mypy

.PHONY: build
build:
	@echo "> Build the package"
	@python ./setup.py sdist bdist_wheel

.PHONY: test
test:
	@echo "> Run the tests"
	@pytest --cov-report=xml --cov-report=term --cov-report=html --cov=pytest_stepfunctions ./tests

.PHONY: black
black:
	@echo "> Check black"
	@black -l 120 --check $(LINTER_SRC)

.PHONY: flake8
flake8:
	@echo "> Check flake8"
	@flake8 $(LINTER_SRC)

.PHONY: mypy
mypy:
	@echo "> Check mypy"
	@mypy $(LINTER_SRC)

.PHONY: clean
clean:
	@echo "> Clean artifacts and caches"
	@rm -rf \
	    ./.mypy_cache \
	    ./.pytest_cache \
	    ./build ./dist \
	    ./htmlcov ./.coverage ./coverage.xml
