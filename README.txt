# MathSearch - Simplified

A streamlined mathematical search engine with BM25 ranking, PageRank, and query expansion.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run (First Time)

```bash
python main.py
```

The first time you run it, you'll be prompted to initialize the database. Say yes (Y), and it will:
- Crawl ~100 Wikipedia math pages
- Build the search index
- Calculate PageRank scores
- Start the web server

This takes 2-3 minutes. After that, the web interface opens at **http://localhost:5000**

### 3. Run (Subsequent Times)

```bash
python main.py
```

Goes straight to the web server.

## Commands

```bash
# Start web server
python main.py

# Initialize/reset database
python main.py setup

# Search from command line
python main.py search "calculus derivatives"

# Show statistics
python main.py stats
```

## Features

- **BM25 Ranking**: Industry-standard search algorithm
- **PageRank**: Link-based authority scoring
- **Query Expansion**: Automatic synonym expansion for math terms
- **Smart Snippets**: Extracts relevant context around matches
- **Modern UI**: Clean, responsive web interface

## Files

- `main.py` - Entry point and web server (200 lines)
- `search_engine.py` - Core search logic (400 lines)
- `requirements.txt` - Dependencies (4 packages)
- `search_engine.db` - Database (auto-created)

## How It Works

1. **Crawls** Wikipedia math pages starting from the Mathematics page
2. **Indexes** content with BM25 term frequencies
3. **Computes** PageRank scores from the link graph
4. **Searches** using BM25 + PageRank combined scoring
5. **Expands** queries with mathematical synonyms
6. **Extracts** relevant snippets with highlighted terms

## Customization

Edit values in `search_engine.py`:

```python
BM25_K1 = 1.5           # Term frequency saturation
BM25_B = 0.75           # Length normalization
SNIPPET_LENGTH = 200     # Snippet character limit
```

Add more synonyms:

```python
MATH_SYNONYMS = {
    "calc": ["calculus"],
    "derivative": ["differentiation"],
    # Add your own...
}
```

## Requirements

- Python 3.8+
- Flask (web framework)
- requests (HTTP)
- beautifulsoup4 (parsing)
- numpy (PageRank computation)

## License

MIT
