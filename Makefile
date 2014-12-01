all:
	cat Makefile
	@echo ""
	@echo "Don't forget to change the version number in setup.py, in profiles/default/metadata.xml, and in version.txt"

clean:
	rm -rf build dist

egg:
	python2.4 setup.py sdist

dist4:
	python2.6 setup.py sdist upload -r ourbasket
