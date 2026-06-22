install:
	pip install uv
	uv sync

run:
	$(install)
	uv run python3 main.py maps/easy/01_linear_path.txt

debug:
	python3 -m pdb main.py maps/easy/01_linear_path.txt

clean:
	$(install)
	uv run -m pyclean .   
	rm -rf .mypy_cache .venv
	rm -rf .vscode


lint:
	$(install)
	-flake8 . --exclude .venv
	-uv run python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs