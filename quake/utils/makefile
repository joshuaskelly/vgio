.PHONY: build clean

build:
	pyinstaller --onefile bsp2wad.py
	pyinstaller --onefile pak.py
	pyinstaller --onefile unpak.py
	pyinstaller --onefile wad.py
	pyinstaller --onefile unwad.py

install_dependencies:
	pip install -r requirements.txt

install_dev_dependencies:
	pip install -r dev-requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build
	rm *.spec
