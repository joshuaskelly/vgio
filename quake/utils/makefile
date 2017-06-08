.PHONY: build clean

build: bsp2wad pak unpak wad unwad qmount

bsp2wad:
	pyinstaller --onefile bsp2wad.py

pak:
	pyinstaller --onefile pak.py

unpak:
	pyinstaller --onefile unpak.py

wad:
	pyinstaller --onefile wad.py

unwad:
	pyinstaller --onefile unwad.py

qmount:
	pyinstaller --onefile qmount.py

install_dependencies:
	pip install -r requirements.txt

install_dev_dependencies:
	pip install -r dev-requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build
	rm *.spec
