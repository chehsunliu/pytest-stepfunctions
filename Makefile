LINTER_SRC := ./setup.py ./src ./tests

.PHONY: all
all: test lint

.PHONY: _base
_base:
	@docker-compose up --build --no-start

.PHONY: test
test: _base
	@echo "> Run the tests"
	@docker-compose up --build --exit-code-from tester
	@echo "> Copy coverage related files from the testing container"
	@docker cp `docker-compose ps -q tester`:/app/coverage.xml .
	@docker cp `docker-compose ps -q tester`:/app/htmlcov .

.PHONY: lint
lint: black flake8 mypy

.PHONY: black
black: _base
	@echo "> Check black"
	@docker-compose run --no-deps --rm tester \
	    black -l 120 --check $(LINTER_SRC)

.PHONY: flake8
flake8: _base
	@echo "> Check flake8"
	@docker-compose run --no-deps --rm tester \
	    flake8 $(LINTER_SRC)

.PHONY: mypy
mypy: _base
	@echo "> Check mypy"
	@docker-compose run --no-deps --rm tester \
	    mypy $(LINTER_SRC)
