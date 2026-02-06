VIRTUALENV := $(PWD)/.venv

export PATH := $(VIRTUALENV)/bin:$(PATH)

.venv:
	python3.12 -m venv $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install --upgrade pip

install-dev: .venv
	if [ -f requirements.txt ]; then $(VIRTUALENV)/bin/pip install -r requirements.txt; fi
	@if [ ! -f .env ]; then \
		echo 'API_KEY="ADICIONE_SUA_API_KEY_AQUI"' > .env; \
		echo ".env file created with default keys"; \
	fi