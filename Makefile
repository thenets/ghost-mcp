# Ghost MCP Development Makefile

.PHONY: help install install-local deps-install-python deps-install-dev deps-deps-install-uv install-pip venv start-ghost stop-ghost restart-ghost setup-tokens test test-unit test-integration test-coverage test-fast test-parallel test-e2e test-connection clean-test run dev format lint clean logs status check-deps setup docs

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Python environment setup
venv: ## Create a virtual environment
	python3 -m venv venv
	./venv/bin/pip install -U pip setuptools
	./venv/bin/pip install -e ".[dev]"

deps-deps-install-uv: ## Install uv package manager
	@echo "📦 Installing uv package manager..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv is already installed"; \
		uv --version; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	fi

# Install the MCP server system-wide
install: ## Install the MCP server system-wide
	claude mcp remove ghost-mcp -s user || true
	claude mcp add ghost-mcp -s user -- \
		bash -c "cd $(PWD) && uv run python -m ghost_mcp.server"

# Install the MCP server in the project scope only
install-local: ## Install the MCP server in the project scope only
	claude mcp remove ghost-mcp || true
	claude mcp add ghost-mcp -- \
		bash -c "cd $(PWD) && uv run python -m ghost_mcp.server"

deps-install-python: ## Install Python dependencies using uv
	@echo "📦 Installing Python dependencies with uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "❌ uv not found. Run 'make deps-deps-install-uv' first"; \
		exit 1; \
	fi
	uv sync
	@echo "✅ Dependencies installed successfully"

# Install dev dependencies
deps-install-dev: ## Install development dependencies
	uv sync --extra dev

install-pip: ## Install Python dependencies using pip (fallback)
	@echo "📦 Installing Python dependencies with pip..."
	python -m pip install -e ".[dev]"
	@echo "✅ Dependencies installed successfully"

# Docker environment
start-ghost: ## Start Ghost and database containers
	@echo "🐳 Starting Ghost development environment..."
	docker-compose up -d
	@echo "⏳ Waiting for containers to be healthy..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
		if docker-compose ps | grep -q "ghost-mcp-dev.*Up" && docker-compose ps | grep -q "ghost-db-dev.*Up.*healthy"; then \
			echo "✅ Ghost containers are running and healthy"; \
			break; \
		fi; \
		echo "   Waiting for containers... ($$timeout seconds remaining)"; \
		sleep 2; \
		timeout=$$((timeout - 2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "❌ Containers did not start properly"; \
		make logs; \
		exit 1; \
	fi
	@echo ""
	@echo "🎉 Ghost is ready!"
	@echo "   Ghost admin: http://localhost:2368/ghost/"
	@echo "   Ghost site:  http://localhost:2368/"
	@echo "   Database:    Available on port 3306"

stop-ghost: ## Stop Ghost and database containers
	@echo "🛑 Stopping Ghost development environment..."
	docker-compose down
	@echo "✅ Ghost containers stopped"

restart-ghost: ## Restart Ghost and database containers
	@echo "🔄 Restarting Ghost development environment..."
	docker-compose restart
	@echo "✅ Ghost containers restarted"

# API token setup
setup-tokens: ## Extract API keys from Ghost database and create .env file
	@echo "🔑 Setting up API tokens..."
	./scripts/setup-tokens.sh

# Testing targets
test: ## Run all tests
	uv run pytest tests/ -v

test-unit: ## Run unit tests only
	uv run pytest tests/test_models.py tests/test_client.py -v

test-integration: ## Run integration tests
	uv run pytest tests/test_mcp_tools.py tests/test_server.py -v

test-coverage: ## Run tests with coverage report
	uv run pytest tests/ --cov=. --cov-report=html --cov-report=term

test-fast: ## Run tests with fail-fast and short traceback
	uv run pytest tests/ -x --tb=short

test-parallel: ## Run tests in parallel
	uv run pytest tests/ -n auto

test-e2e: ## Run end-to-end tests against real Ghost instance
	@echo "🧪 Running end-to-end tests..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	@echo "⚠️  Note: These tests require a running Ghost instance (make start-ghost)"
	uv run pytest tests/e2e/ -v -m e2e

test-connection: ## Test Ghost API connectivity
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	@python scripts/test-connection.py

# Clean up test artifacts
clean-test: ## Clean up test artifacts
	rm -rf .coverage htmlcov/ .pytest_cache/ tests/__pycache__/ __pycache__/

# Running the server
run: check-deps ## Run the Ghost MCP server
	@echo "🚀 Starting Ghost MCP server..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	python -m ghost_mcp.server

dev: check-deps ## Run the Ghost MCP server in development mode with auto-reload
	@echo "🚀 Starting Ghost MCP server in development mode..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	python -m ghost_mcp.server --dev

# Utilities
logs: ## Show Docker container logs
	@echo "📋 Showing container logs..."
	docker-compose logs -f

status: ## Show status of all components
	@echo "📊 Ghost MCP Status"
	@echo "=================="
	@echo ""
	@echo "🐳 Docker Containers:"
	@docker-compose ps || echo "   No containers running"
	@echo ""
	@echo "📁 Configuration:"
	@if [ -f .env ]; then \
		echo "   ✅ .env file exists"; \
		echo "   📍 Ghost URL: $$(grep GHOST_URL .env | cut -d= -f2)"; \
		echo "   🔑 Content API: $$(grep GHOST_CONTENT_API_KEY .env | cut -d= -f2 | cut -c1-10)..."; \
		echo "   🔑 Admin API: $$(grep GHOST_ADMIN_API_KEY .env | cut -d= -f2 | cut -c1-10)..."; \
	else \
		echo "   ❌ .env file missing"; \
	fi
	@echo ""
	@echo "🐍 Python Environment:"
	@if command -v uv >/dev/null 2>&1; then \
		echo "   ✅ uv: $$(uv --version)"; \
	else \
		echo "   ❌ uv not installed"; \
	fi
	@echo "   🐍 Python: $$(python --version)"
	@if python -c "import ghost_mcp" 2>/dev/null; then \
		echo "   ✅ ghost_mcp package installed"; \
	else \
		echo "   ❌ ghost_mcp package not installed"; \
	fi

check-deps: ## Check if all dependencies are available
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	@if ! python -c "import ghost_mcp" 2>/dev/null; then \
		echo "❌ ghost_mcp package not installed. Run 'make install' first"; \
		exit 1; \
	fi

# Code quality
.PHONY: format
format: ## Format code with ruff and black
	@echo "🎨 Formatting code..."
	uv run ruff format .
	uv run black .
	@echo "✅ Code formatting completed"

.PHONY: lint
lint: ## Run linting with ruff and mypy
	@echo "🔍 Running linters..."
	uv run ruff check .
	uv run mypy src/
	@echo "✅ Linting completed"

clean: ## Clean up temporary files and development environment
	@echo "🧹 Cleaning up development environment..."
	find . -type f -name "*.pyc" -delete || true
	find . -type d -name "__pycache__" -delete || true
	find . -type d -name ".pytest_cache" -delete || true
	rm -rf .ruff_cache/ || true
	rm -rf venv/ || true
	rm -rf .pytest_cache/ || true
	rm -rf htmlcov/ || true
	rm -f .coverage* coverage.xml || true
	docker-compose down -v || true
	rm -f .env || true
	@if command -v uv >/dev/null 2>&1; then \
		uv clean; \
	fi
	@echo "✅ Cleanup complete"

# Development workflow
setup: deps-deps-install-uv deps-install-python start-ghost setup-tokens ## Complete setup from scratch
	@echo ""
	@echo "🎉 Ghost MCP setup complete!"
	@echo ""
	@echo "Ready to use:"
	@echo "  make test    # Test the implementation"
	@echo "  make run     # Run the MCP server"
	@echo "  make status  # Check system status"

# Documentation
docs: ## Show important URLs and information
	@echo "📚 Ghost MCP Documentation"
	@echo "========================="
	@echo ""
	@echo "🌐 Web Interfaces:"
	@echo "   Ghost Admin:    http://localhost:2368/ghost/"
	@echo "   Ghost Site:     http://localhost:2368/"
	@echo "   phpMyAdmin:     http://localhost:8080/ (if enabled)"
	@echo ""
	@echo "📁 Important Files:"
	@echo "   Configuration:  .env"
	@echo "   Project:        pyproject.toml"
	@echo "   Docker:         docker-compose.yml"
	@echo "   Setup Script:   scripts/setup-tokens.sh"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "   make setup      # Complete initial setup"
	@echo "   make test       # Test functionality"
	@echo "   make run        # Run MCP server"
	@echo "   make logs       # View container logs"
	@echo "   make status     # Check system status"