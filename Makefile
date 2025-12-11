.PHONY: help n8n-start n8n-stop n8n-logs n8n-restart

# Default target
help:
	@echo "Available commands:"
	@echo "  make n8n-start         - Start n8n Docker container"
	@echo "  make n8n-stop          - Stop n8n Docker container"
	@echo "  make n8n-restart       - Restart n8n Docker container"
	@echo "  make n8n-logs          - Show n8n logs"

# Start n8n
n8n-start:
	@cd n8n && docker compose up -d
	@echo "Waiting for n8n to start..."
	@sleep 5
	@echo "n8n is running at http://localhost:5678"

# Stop n8n
n8n-stop:
	@cd n8n && docker compose down

# Restart n8n
n8n-restart:
	@cd n8n && docker compose restart
	@echo "n8n restarted"

# Show n8n logs
n8n-logs:
	@cd n8n && docker compose logs -f

# ==========================================
# n8n Workflow Management
# ==========================================

# Import workflows (cleans and imports recursively)
.PHONY: import
import:
	@echo "Importing cleaned workflows (IDs stripped, inactive)..."
	@if [ -f .env ]; then set -a; . .env; set +a; fi; \
	cd n8n && python3 scripts/clean_import.py


# Delete all workflows
.PHONY: n8n-clean
delete:
	@echo "WARNING: This will delete ALL workflows in n8n."
	@if [ -f .env ]; then set -a; . .env; set +a; fi; \
	if [ -z "$$N8N_API_KEY" ]; then echo "Error: N8N_API_KEY is not set"; exit 1; fi; \
	cd n8n && python3 scripts/delete_workflows.py
