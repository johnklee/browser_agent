.PHONY: init test lint dist

all: init test lint

init:
	pip3 install -r requirements.txt

init_test:
	pip3 install -r requirements_test.txt

test:
	python -m pytest tests

dist: init test
	rm -f dist/*
	python3 setup.py sdist bdist_wheel

lint:
	ruff check browser_agent

output_requirements:
	uv pip compile pyproject.toml -o requirements.txt

output_test_requirements:
	uv pip compile pyproject.toml --group dev -o requirements_test.txt

upload: dist
	twine upload --skip-existing dist/*
