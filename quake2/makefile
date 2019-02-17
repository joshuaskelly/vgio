.PHONY: install uninstall test clean

install:
	pip install .

uninstall:
	pip uninstall quake2-tools

test:
	python -m unittest discover -s tests

clean:
	find . -name "*.pyc" -delete
