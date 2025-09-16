# Python Quant Project Makefile

.PHONY: clean help

# Clean all temporary files including __pycache__
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Show help
help:
	@echo "Available commands:"
	@echo "  clean        - Remove all temporary files including __pycache__"
	@echo "  help         - Show this help message"
