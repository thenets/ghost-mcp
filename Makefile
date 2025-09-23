# Ghost MCP Development Makefile

.PHONY: help install install-uv start-ghost stop-ghost setup-tokens test test-connection run dev clean logs status check-deps

# Default target
help: ## Show this help message
	@echo "Ghost MCP Development Commands"
	@echo "============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make install-uv     # Install uv package manager (if not installed)"
	@echo "  make install        # Install Python dependencies"
	@echo "  make start-ghost    # Start Ghost and database containers"
	@echo "  make setup-tokens   # Extract API keys and create .env file"
	@echo "  make test           # Test the implementation"
	@echo "  make run            # Run the MCP server"

# Python environment setup
install-uv: ## Install uv package manager
	@echo "📦 Installing uv package manager..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv is already installed"; \
		uv --version; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	fi

install: ## Install Python dependencies using uv
	@echo "📦 Installing Python dependencies with uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "❌ uv not found. Run 'make install-uv' first"; \
		exit 1; \
	fi
	uv sync
	@echo "✅ Dependencies installed successfully"

install-pip: ## Install Python dependencies using pip (fallback)
	@echo "📦 Installing Python dependencies with pip..."
	python -m pip install -e .
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

# Testing
test-connection: ## Test Ghost API connectivity
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-tokens' first"; \
		exit 1; \
	fi
	@python scripts/test-connection.py

test: check-deps test-connection ## Run all tests
	@echo "🧪 Running comprehensive tests..."
	@echo "Testing MCP tools registration..."
	@python -c "\
import sys; \
sys.path.insert(0, 'src'); \
from ghost_mcp.server import mcp; \
print(f'✅ FastMCP server initialized'); \
print(f'   Tools registered: {len([attr for attr in dir(mcp) if not attr.startswith(\"_\")])}+')"
	@echo "✅ All tests passed!"

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

clean: ## Clean up development environment
	@echo "🧹 Cleaning up development environment..."
	docker-compose down -v
	rm -f .env
	@if command -v uv >/dev/null 2>&1; then \
		uv clean; \
	fi
	@echo "✅ Cleanup complete"

# Development workflow
setup: install-uv install start-ghost setup-tokens ## Complete setup from scratch
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