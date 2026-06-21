install:
	pip install uv
	uv sync

run:
	$(install)
	uv run python3 main.py maps/easy/01_linear_path.txt

debug:
	python3 -m pdb main.py maps/easy/01_linear_path.txt

clean:
	rm -rf *__pycache__*
	rm -rf llm_sdk/llm_sdk/__pycache__
	rm -rf src/__pycache__
	rm -rf .mypy_cache
	rm -rf .vscode
	rm -rf .venv

lint:
	flake8 . --exclude .venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
