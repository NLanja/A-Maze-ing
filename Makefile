all: install run

venv:
	python3 -m venv .venv

install: venv
	.venv/bin/python3 -m pip install mlx-2.2-py3-none-any.whl
	.venv/bin/python3 -m pip install build
	.venv/bin/python3 -m pip install flake8
	.venv/bin/python3 -m pip install mypy

run:
	.venv/bin/python3 a_maze_ing.py config.txt

debug:
	.venv/bin/python3 -m pdb a_maze_ing.py config.txt

lint:
	.venv/bin/python3 -m flake8 . --exclude=.venv
	.venv/bin/python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	.venv/bin/python3 -m flake8 . --exclude=.venv
	.venv/bin/python3 -m mypy --strict . --exclude=.venv 

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
	find . -type f -name "*.pyc" -delete
	rm -rf .venv

.PHONY: install run debug lint lint-strict clean