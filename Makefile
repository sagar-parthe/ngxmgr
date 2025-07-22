help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	export PATH="/Users/sagar/.local/bin:$$PATH" && poetry install

test: ## Run tests
	export PATH="/Users/sagar/.local/bin:$$PATH" && poetry run pytest

lint: ## Run linting
	export PATH="/Users/sagar/.local/bin:$$PATH" && poetry run ruff check .

format: ## Format code
	export PATH="/Users/sagar/.local/bin:$$PATH" && poetry run ruff format .

type-check: ## Run type checking
	export PATH="/Users/sagar/.local/bin:$$PATH" && poetry run mypy src/