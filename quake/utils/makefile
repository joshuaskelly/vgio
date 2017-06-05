.PHONY: build clean

build:
	pyinstaller --onefile bsp2wad.py
	pyinstaller --onefile pak.py
	pyinstaller --onefile unpak.py
	pyinstaller --onefile wad.py
	pyinstaller --onefile unwad.py

install_dependencies:
	pip install -r requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build
	rm *.spec
