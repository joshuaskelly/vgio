.PHONY: install uninstall test clean

install:
	pip install .

uninstall:
	pip uninstall vgio

publish:
	python setup.py sdist upload

test:
	python -m unittest discover

clean:
	find . -name "*.pyc" -delete
	rm -rf dist
	rm -rf *.egg-info
