PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin

.PHONY: setup server menu test

# Creates .venv and installs every Python dependency (re-runs only when requirements change)
setup: $(VENV)/.installed

$(VENV)/.installed: data_collection_framework/requirements.txt data_collection_framework/requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r data_collection_framework/requirements-dev.txt
	touch $@

# Reads PY_SERVER_TOKEN and the TWITTER_* variables from the environment, or from .env if present
server: setup
	@set -a; [ -f .env ] && . ./.env; set +a; $(BIN)/python data_collection_framework/server.py

menu: setup
	@set -a; [ -f .env ] && . ./.env; set +a; $(BIN)/python data_collection_framework/menu.py

test: setup
	$(BIN)/python -m pytest
