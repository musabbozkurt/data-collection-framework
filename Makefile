PYTHON ?= python3
# Absolute project root, so every target works from any directory: make -f /path/to/Makefile server
ROOT   := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
VENV   := $(ROOT)/.venv
BIN    := $(VENV)/bin
APP    := $(ROOT)/data_collection_framework
LOAD_ENV = set -a; [ -f "$(ROOT)/.env" ] && . "$(ROOT)/.env"; set +a

.PHONY: setup browsers x-login server menu scraper test

# Creates .venv and installs every Python dependency (re-runs only when requirements change)
setup: $(VENV)/.installed

$(VENV)/.installed: $(APP)/requirements.txt $(APP)/requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r $(APP)/requirements-dev.txt
	touch $@

# Downloads the Chromium build used by the X profile scraper (once, about 100 MB)
browsers: setup
	$(BIN)/python -m playwright install chromium

# Opens a browser to sign in to X once; the session is reused by the profile scraper
x-login: browsers
	@$(LOAD_ENV); $(BIN)/python $(APP)/x_profile_scraper.py login

# Reads PY_SERVER_TOKEN and the TWITTER_* variables from the environment, or from .env if present
server: setup
	@$(LOAD_ENV); $(BIN)/python $(APP)/server.py

menu: setup
	@$(LOAD_ENV); $(BIN)/python $(APP)/menu.py

# Extra arguments: make scraper ARGS='"Data Science" --live 60'
scraper: setup
	@$(LOAD_ENV); $(BIN)/python $(APP)/x_batch_scraper.py $(ARGS)

test: setup
	cd $(ROOT) && $(BIN)/python -m pytest
