# Makefile for Blood Donation Dashboard Project

# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
DATA_DIR = data/raw
EXCEL_FILE = $(DATA_DIR)/blood_donation_data.xlsx

.DEFAULT_GOAL := help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Environment Setup

venv:  ## Create Python virtual environment
	python -m venv $(VENV)
	@echo "Virtual environment created at $(VENV)"

install: venv  ## Install requirements
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Packages installed successfully"

##@ Data Ingestion

data-dirs:  ## Create data directories
	@mkdir -p $(DATA_DIR)
	@echo "Created data directory structure"

check-data: data-dirs  ## Verify raw data exists
	@if [ ! -f $(EXCEL_FILE) ]; then \
		echo "Error: Excel file not found at $(EXCEL_FILE)"; \
		echo "Please ensure blood_donation_data.xlsx exists in data/raw"; \
		exit 1; \
	fi
	@echo "Data file verification successful"

ingest: check-data  ## Load data into system
	@echo "Starting data ingestion..."
	$(PYTHON) src/data_loader.py
	@echo "Data loading completed successfully"

##@ Project Management

clean:  ## Clean project artifacts
	rm -rf $(VENV)
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

.PHONY: help venv install data-dirs check-data ingest clean