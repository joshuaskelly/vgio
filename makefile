.PHONY: install uninstall test clean

install:
	pip install .

uninstall:
	pip uninstall vgio

package:
	python setup.py sdist

publish: package
	python -m twine upload dist/*

publish-test: package
	python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test:
	python -m unittest discover

docs:
	cd ./docs && $(MAKE) html

clean:
	find . -name "*.pyc" -delete
	rm -rf dist
	rm -rf *.egg-info
	$(MAKE) -C ./docs clean
