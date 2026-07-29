install:
	python3 -m pip install mlx-2.2-py3-none-any.whl
	python3 -m pip install flake8
	python3 -m pip install mypy

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy --strict .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
	find . -type f -name "*.pyc" -delete

.PHONY: run debug lint lint strict clean