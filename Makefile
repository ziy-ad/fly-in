install:
	pip install uv
	uv sync

run:
	uv run python3 main.py maps/challenger/01_the_impossible_dream.txt

debug:
	python3 -m pdb main.py maps/challenger/01_the_impossible_dream.txt

clean:
	rm -rf *__pycache__*
	rm -rf llm_sdk/llm_sdk/__pycache__
	rm -rf src/__pycache__
	rm -rf .mypy_cache
	rm -rf .vscode

lint:
	flake8 . --exclude .venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs