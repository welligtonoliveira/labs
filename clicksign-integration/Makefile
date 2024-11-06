# project settings
PROJECT_NAME  := "clicksign-integration"
PROJECT_PATH  := .

# venv settings
export PYTHONPATH := $(PROJECT_PATH):tests/fixtures
export VIRTUALENV := $(PWD)/.venv
export PATH       := $(VIRTUALENV)/bin:$(PATH)

# fix make < 3.81 (macOS and old Linux distros)
ifeq ($(filter undefine,$(value .FEATURES)),)
SHELL = env PATH="$(PATH)" /bin/bash
endif

.PHONY: .env .venv

all:

.env:
	echo 'PYTHONPATH="$(PYTHONPATH)"' > .env

.venv:
	python3.10 -m venv $(VIRTUALENV)
	pip install --upgrade pip

clean:
	rm -rf dependencies .pytest_cache .coverage .aws-sam
	find $(PROJECT_PATH) -name __pycache__ | xargs rm -rf
	find tests -name __pycache__ | xargs rm -rf

install:  .venv .env
	if [ -f requirements.txt ]; then $(VIRTUALENV)/bin/pip install -r requirements.txt; fi
