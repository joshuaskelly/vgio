OS := $(shell python -c 'import sys; print({"win32": "windows", "darwin": "osx"}.get(sys.platform, sys.platform))')

.PHONY: build bsp2wad pak unpak wad unwad qmount image2spr spr2image install_dependencies install_dev_dependencies clean

build: bsp2wad pak unpak wad unwad qmount image2spr spr2image

bsp2wad:
	pyinstaller --onefile ./spec/bsp2wad.spec

pak:
	pyinstaller --onefile ./spec/pak.spec

unpak:
	pyinstaller --onefile ./spec/unpak.spec

wad:
	pyinstaller --onefile ./spec/wad.spec

unwad:
	pyinstaller --onefile ./spec/unwad.spec

qmount:
	pyinstaller --onefile ./spec/qmount.spec

image2spr:
	pyinstaller --onefile ./spec/image2spr.spec

spr2image:
	pyinstaller --onefile ./spec/spr2image.spec

install_dependencies:
	pip install -r requirements.txt

install_dev_dependencies:
	pip install -r dev-requirements.txt

package:
	cd ./dist && \
	ls | zip -@ quake-tools_$(OS).zip && \
	cd ..

publish:
	cd ./dist && \
	butler push quake-tools_$(OS).zip joshua/quake-tools:$(OS) && \
	cd ..

clean:
	rm -rf ./dist
	rm -rf ./build
