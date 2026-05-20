.PHONY: help install dev-install clean lint format test run init crawl docs

# Default target
help:
	@echo "MathSearch - Available targets:"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make dev-install  - Install dependencies including dev tools"
	@echo "  make run          - Run the Flask web application"
	@echo "  make init         - Initialize database (without crawling)"
	@echo "  make crawl        - Crawl Wikipedia and build index"
	@echo "  make clean        - Remove database and compiled files"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black"
	@echo "  make test         - Run tests"
	@echo "  make help         - Show this help message"

# Install dependencies
install:
	pip install -r requirements.txt

# Install dev dependencies
dev-install:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy pytest-cov

# Run the web application
run:
	python app.py

# Initialize database
init:
	python init.py --no-crawl

# Crawl Wikipedia and build index
crawl:
	python init.py

# Clean up database and compiled files
clean:
	rm -f search_engine.db
	rm -f link_graph.json page_content.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete

# Run linting
lint:
	flake8 *.py --max-line-length=100 --exclude=__pycache__
	mypy *.py --ignore-missing-imports || true

# Format code
format:
	black *.py --line-length=100

# Run tests
test:
	pytest -v

# Interactive search
search:
	python search.py

# Build PageRank
pagerank:
	python pagerank.py

# View top PageRank pages
pagerank-top:
	python pagerank.py | tail -25

# Show database statistics
db-stats:
	python -c "from database import init_db, get_document_count, get_avg_doc_length, get_inverted_index; init_db(); print(f'Documents: {get_document_count()}'); print(f'Average doc length: {get_avg_doc_length():.1f}'); print(f'Unique terms: {len(get_inverted_index())}')" || echo "Run 'make init' first"

# Development server with debug
dev:
	FLASK_ENV=development FLASK_DEBUG=1 python app.py
