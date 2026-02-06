VIRTUALENV := $(PWD)/.venv

export PATH := $(VIRTUALENV)/bin:$(PATH)

.venv:
	python3.12 -m venv $(VIRTUALENV)
	pip3 install --upgrade pip

install-dev: .venv
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi