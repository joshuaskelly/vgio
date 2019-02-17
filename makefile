.PHONY: install uninstall test clean

install:
	pip install .

uninstall:
	pip uninstall vgio

test:
	python -m unittest discover

clean:
	find . -name "*.pyc" -delete
