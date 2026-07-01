VENV := .venv
PYTHON_VERSION := python3.12
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

.PHONY: run install clean

run: install
	$(PYTHON) main.py

install:
	@test -d $(VENV) || $(PYTHON_VERSION) -m venv $(VENV)
	$(PIP) install -r requirements.txt

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +