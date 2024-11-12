# Makefile for building and uploading a Python package

.PHONY: clean build upload new-version

# Python binary to use
PYTHON := python3

# Target to run tests 
test:
	tox

# Setup dev environment
setup-dev:
	./scripts/setup-dev.sh

# Target to upload the package to PyPI (requires Twine)
upload:
	twine upload dist/*

# Target to clean up build artifacts
clean:
	rm -rf build dist *.egg-info

# Target to build the package (source distribution and wheel)
build:
	$(PYTHON) setup.py sdist

# Target to upload the package to PyPI with new version
new-version:
	make clean && make build  && make upload

