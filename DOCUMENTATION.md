# MathSearch - Complete Documentation

A sophisticated search engine optimized for mathematical content with BM25 ranking, semantic re-ranking, and intelligent query expansion.

## Table of Contents
1. [Features & Overview](#features--overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Development Guide](#development-guide)
5. [API & Usage](#api--usage)
6. [FAQ](#faq)
7. [Contributing](#contributing)
8. [Changelog](#changelog)

---

## Features & Overview

### Core Features

- **BM25 Ranking**: Industry-standard information retrieval ranking algorithm
- **Hybrid Semantic Re-ranking**: Optional two-stage retrieval using sentence transformers for semantic similarity
- **Query Expansion**: Spell correction, synonym expansion, and optional LLM-based expansion
- **Intelligent Snippet Extraction**: Context-aware snippets with relevant sentences around matches
- **PageRank Scoring**: Link-based authority scoring integrated into results
- **Modern Web Interface**: Beautiful, responsive UI built with Flask
- **Mathematical Synonyms**: Domain-specific synonym expansion for math terminology

---

## Architecture

### Module Dependencies

```
app.py (Flask Web App)
├── search.py (Search Engine)
│   ├── database.py (Data Access)
│   ├── query_expansion.py (Query Processing)
│   └── snippets.py (Snippet Extraction)
├── config.py (Configuration)
└── (HTML/CSS templates embedded)

Database Management
├── database.py (SQLite Interface)
├── indexer.py (Index Building)
│   ├── crawler.py (Web Scraping)
│   └── database.py
├── pagerank.py (Authority Scoring)
│   ├── database.py
│   └── crawler.py
└── init.py (Setup Script)
```

### Core Components

- **app.py**: Flask web application with UI and search endpoints
- **search.py**: Two-stage BM25 and semantic search implementation
- **database.py**: SQLite database management with normalized schema
- **config.py**: Centralized configuration for all tunable parameters
- **crawler.py**: Web crawler for Wikipedia math pages
- **indexer.py**: Inverted index builder with BM25 support
- **pagerank.py**: PageRank computation for link graph authority scoring
- **snippets.py**: Intelligent snippet extraction from documents
- **query_expansion.py**: Spell correction and synonym expansion
- **init.py**: Database initialization and crawler runner

### Database Schema

#### Documents Table

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    doc_length INTEGER DEFAULT 0,
    pagerank REAL DEFAULT 0.0
)
```

**Fields:**
- `id`: Unique document identifier
- `url`: Document URL (unique constraint)
- `title`: Page title (extracted from URL or content)
- `content`: Full text content of the page
- `doc_length`: Word count (used for BM25 normalization)
- `pagerank`: Computed authority score

**Indexes:**
- Primary key on `id`
- Unique constraint on `url`

#### Inverted Index Table

```sql
CREATE TABLE inverted_index (
    word TEXT NOT NULL,
    doc_id INTEGER NOT NULL,
    tf REAL NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    PRIMARY KEY (word, doc_id)
)
```

**Fields:**
- `word`: Indexed term (lowercase)
- `doc_id`: Document containing the term
- `tf`: Term frequency in the document

**Indexes:**
- Primary key on `(word, doc_id)`
- Index on `word` for efficient lookups
- Index on `doc_id` for document retrieval

### BM25 Ranking Algorithm

The BM25 (Best Matching 25) algorithm scores documents based on term importance.

**Formula:**
```
score = Σ IDF(term) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (|D| / avgdl)))
```

**Components:**
- `IDF(term)` = log((N - df + 0.5) / (df + 0.5) + 1)
- `tf` = term frequency in document
- `|D|` = document length
- `avgdl` = average document length
- `k1` = 1.5 (term frequency saturation)
- `b` = 0.75 (length normalization)

**Time Complexity:** O(k * M) where k = number of query terms, M = average inverted list length

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Quick Setup

#### Windows

```bash
git clone <repository-url>
cd Search-Engine
setup.bat
```

#### Linux/macOS

```bash
git clone <repository-url>
cd Search-Engine
bash setup.sh
```

#### Manual Setup

```bash
# Clone repository
git clone <repository-url>
cd Search-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init.py --no-crawl
```

### Using Makefile Commands

```bash
# Install base dependencies
make install

# Install with development tools
make dev-install

# Run the web application
make run

# Run linting
make lint

# Format code
make format

# Clean cache files
make clean
```

---

## Development Guide

### Code Style

We follow Python best practices:

- **Formatting**: Use `black` with line length 100
  ```bash
  make format
  # or: black *.py --line-length=100
  ```

- **Linting**: Run `flake8` before committing
  ```bash
  make lint
  # or: flake8 *.py --max-line-length=100
  ```

- **Type hints**: Use type hints where possible (checked with mypy)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Search-Engine.git
   cd Search-Engine
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   make dev-install
   # or: pip install -r requirements.txt && pip install pytest black flake8 mypy
   ```

4. **Initialize the database**
   ```bash
   python init.py --no-crawl
   ```

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Refactor, etc.)
- Keep the first line under 50 characters
- Reference issues when applicable: `Fixes #123`

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Keep changes focused and related
   - Add docstrings to new functions
   - Update documentation if adding features

3. **Run tests and linting**
   ```bash
   make lint
   make format
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add: descriptive message"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Describe what you changed and why
   - Reference any related issues
   - Ensure CI checks pass

### File Naming Conventions
- Python modules: `lowercase_with_underscores.py`
- Configuration: All settings centralized in `config.py`
- Database: SQLite with normalized schema

---

## API & Usage

### Running the Web Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Search Engine Programmatically

```python
from search import Search
from database import Database

# Initialize search engine
db = Database()
search = Search(db)

# Perform a search
results = search.search("calculus", use_semantic=True)

# Results format
for result in results:
    print(f"Title: {result['title']}")
    print(f"Score: {result['score']}")
    print(f"Snippet: {result['snippet']}")
```

### Crawling Wikipedia Data

```bash
# Default crawl (1000 pages from Wikipedia)
python init.py

# Custom crawl with parameters
python init.py --max-pages 500 --seed-url "https://en.wikipedia.org/wiki/Calculus"

# Skip crawling (use existing data)
python init.py --no-crawl
```

---

## FAQ

### Installation & Setup

**Q: I get "ModuleNotFoundError" when running the app**

A: You need to install dependencies first:
```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
# Windows
setup.bat

# Linux/macOS
bash setup.sh
```

**Q: The setup script fails on Windows**

A: Make sure you have:
1. Python 3.8+ installed
2. Python in your PATH (check with `python --version`)
3. Administrator privileges if needed

If issues persist, try manual setup:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init.py --no-crawl
```

**Q: How do I install for development?**

A: Use dev-install:
```bash
make dev-install
```

This installs testing and linting tools.

### Database & Indexing

**Q: Where is the database file?**

A: The SQLite database is stored as `search_engine.db` in the project root directory. The path is configured in `config.py`.

**Q: How do I reset the database?**

A: Delete the database and reinitialize:
```bash
rm search_engine.db
python init.py --no-crawl
```

**Q: How do I crawl Wikipedia?**

A: Run the initialization with crawling:
```bash
python init.py
```

Or specify custom parameters:
```bash
python init.py --max-pages 1000 --seed-url "https://en.wikipedia.org/wiki/Calculus"
```

**Q: Crawling is very slow - how can I speed it up?**

A:
1. Reduce max_pages: `python init.py --max-pages 100`
2. Stop and retry (it continues from where it left off)
3. The sentence transformer downloads ~60MB on first use - this is one-time

**Q: Can I use existing crawled data?**

A: Yes! Save the crawler data:
```python
from crawler import crawl, save_data
link_graph, page_content = crawl(seed_url, max_pages=100)
save_data(link_graph, page_content)
```

Then reuse it:
```bash
python init.py --no-crawl
```

### Using the Search Engine

**Q: How do I run the web app?**

A:
```bash
python app.py
```

The application opens at `http://localhost:5000`

---

## Contributing

Thank you for your interest in contributing to MathSearch! This section provides guidelines and instructions.

### Code of Conduct

Please be respectful and constructive in all interactions. We're building a community that welcomes everyone.

### Getting Started

#### Prerequisites

- Python 3.8+
- Git
- Virtual environment (venv, conda, or similar)

#### Areas for Contribution

- Performance optimizations
- Additional query expansion features
- Semantic search improvements
- UI/UX enhancements
- Documentation and examples
- Bug reports and fixes
- Additional mathematical synonyms

---

## Changelog

### [1.0.0] - 2024-05-21

#### Added
- Initial release of MathSearch - Advanced Mathematical Search Engine
- BM25 ranking algorithm implementation
- Hybrid two-stage retrieval with semantic re-ranking
- Query expansion with spell correction and synonym expansion
- PageRank computation for link authority scoring
- Intelligent snippet extraction with context awareness
- Flask web application with modern UI
- SQLite database with normalized schema
- Web crawler for Wikipedia mathematics pages
- Comprehensive configuration system
- Command-line search interface
- REST API for search functionality

#### Core Features
- **BM25 Ranking**: Industry-standard information retrieval ranking
- **Semantic Re-ranking**: Optional sentence transformer integration
- **Query Expansion**: Spell correction and domain-specific synonyms
- **PageRank**: Link-based authority scoring
- **Snippet Extraction**: Context-aware result snippets
- **Web Interface**: Modern, responsive Flask-based UI

#### Project Structure
- `app.py`: Flask web application and routes
- `search.py`: BM25 and hybrid search implementation
- `database.py`: SQLite database management
- `crawler.py`: Wikipedia web crawler
- `indexer.py`: Inverted index builder
- `pagerank.py`: PageRank computation
- `query_expansion.py`: Query processing and expansion
- `snippets.py`: Snippet extraction and highlighting
- `config.py`: Centralized configuration
- `init.py`: Database initialization script

#### Documentation
- `README.md`: Project overview
- `DOCUMENTATION.md`: Comprehensive guide
- `LICENSE`: MIT License
- `requirements.txt`: Python dependencies
- `setup.py`: Package installation configuration
- Setup scripts for Windows and Unix/Linux

#### Version History Details
- Complete refactor from original prototype to production-ready system
- Renamed files from `prod_*` prefix to clean names
- Established consistent import structure
- Added comprehensive documentation
- Implemented proper error handling
- Created reproducible setup process
- Added git repository structure with .gitignore and .gitattributes

#### Bug Fixes (Version 1.0.0)
- **crawler.py (Line 68)**: Fixed `_is_valid_wikipedia_url()` method call
  - Issue: Function called with `self` in non-class context
  - Impact: Crawler would fail when filtering URLs

### [Unreleased]

#### Planned Features
- LLM-based query expansion (with Ollama integration)
- Advanced filtering options
- Search result clustering
- Faceted search
- User search history and bookmarks
- Performance optimizations
- Advanced caching mechanisms
- Multi-language support
