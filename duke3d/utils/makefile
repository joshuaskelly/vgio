.PHONY: build art unart grp ungrp install_dependencies install_dev_dependencies clean

build: art unart grp ungrp

art:
	pyinstaller --onefile art.py

unart:
	pyinstaller --onefile unart.py

grp:
	pyinstaller --onefile grp.py

ungrp:
	pyinstaller --onefile ungrp.py

install_dependencies:
	pip install -r requirements.txt

install_dev_dependencies:
	pip install -r dev-requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build
	rm *.spec
