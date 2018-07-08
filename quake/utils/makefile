.PHONY: build bsp2wad pak unpak wad unwad qmount image2spr spr2image install_dependencies install_dev_dependencies clean

build: bsp2wad pak unpak wad unwad qmount image2spr spr2image

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

image2spr:
	pyinstaller --onefile image2spr.py

spr2image:
	pyinstaller --onefile spr2image.py

install_dependencies:
	pip install -r requirements.txt

install_dev_dependencies:
	pip install -r dev-requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build
	rm *.spec
