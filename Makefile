SHELL = bash

DJANGO_DIR = dj
VIRTUAL_ENV = var/ve
LOCALPATH = $(CURDIR)
PYTHONPATH = $(LOCALPATH)/$(DJANGO_DIR)
SETTINGS = dev.sqlite
DJANGO_SETTINGS_MODULE = $(DJANGO_DIR).settings.$(SETTINGS)
DJANGO_POSTFIX = --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
PYTHON_BIN = $(VIRTUAL_ENV)/bin
OS = $(shell uname)


clean:
	find . -name "*.pyc" -exec rm -rf {} \;
	
cleanvirtualenv:
	rm -rf $(VIRTUAL_ENV)

cleanvar: clean cleanvirtualenv
	rm -rf $(LOCALPATH)/var

cleanall: cleanvar clean

pip:
	$(PYTHON_BIN)/pip install -r requirements.txt

initvirtualenv:
	virtualenv --no-site-packages $(VIRTUAL_ENV)

bootstrap: initvirtualenv pip

reinstalvirtualenv: cleanvirtualenv bootstrap initvirtualenv initenv

initenv:
	echo -e '\nDJANGO_SETTINGS_MODULE="$(DJANGO_SETTINGS_MODULE)"' >> $(VIRTUAL_ENV)/bin/activate
	echo -e 'export DJANGO_SETTINGS_MODULE' >> $(VIRTUAL_ENV)/bin/activate

install: cleanall bootstrap initenv
