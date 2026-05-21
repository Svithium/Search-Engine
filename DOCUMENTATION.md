# MathSearch — Complete Documentation

A streamlined search engine optimized for mathematical content with BM25 ranking, PageRank authority scoring, and intelligent query expansion.

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
- **PageRank Scoring**: Link-based authority scoring integrated into results
- **Query Expansion**: Domain-specific synonym expansion for math terminology
- **Intelligent Snippet Extraction**: Context-aware snippets with highlighted matches
- **Modern Web Interface**: Responsive UI built with Flask
- **Lightweight**: No ML models — ~10 MB dependencies, ~50 MB RAM at runtime

---

## Architecture

### File Structure

```
Search-Engine/
├── main.py            — Flask web app, CLI, and auto-setup (~270 lines)
├── search_engine.py   — All core logic (~450 lines)
├── requirements.txt   — 4 dependencies
├── search_engine.db   — SQLite database (auto-created on first run)
├── start.sh           — One-click start for Linux/macOS
├── start.bat          — One-click start for Windows
├── README.md          — Project overview
├── README.txt         — Plain-text quick reference
├── HOW_TO_RUN.md      — Step-by-step setup guide
├── DOCUMENTATION.md   — This file
└── LICENSE            — MIT License
```

### Module Layout

```
main.py
├── Flask app (routes: / and /search)
├── setup_database()      — Interactive first-run setup
└── main()                — Entry point; CLI command dispatcher

search_engine.py
├── Configuration         — DB_PATH, BM25_K1, BM25_B, SNIPPET_LENGTH, MATH_SYNONYMS
├── Database              — init_db(), save_to_db()
├── Crawler               — crawl(), is_valid_wiki_url()
├── PageRank              — compute_pagerank()
├── Tokenization          — tokenize(), expand_query()
├── Search                — search(), compute_bm25()
├── Snippets              — extract_snippet()
└── Utilities             — get_stats()
```

### Data Flow

```
Stage 1 — Crawl
  crawl(seed_url, max_pages)
  → Downloads Wikipedia pages via requests + BeautifulSoup
  → Builds link_graph {url: [linked_urls]} and page_content {url: text}

Stage 2 — Index & PageRank
  save_to_db(page_content, link_graph)
  → Tokenizes text, counts term frequencies
  → Writes documents and inverted_index tables
  → Calls compute_pagerank() → updates pagerank column

Stage 3 — Search
  search(query, top_k)
  → expand_query() adds synonyms
  → Inverted index lookup → candidate doc set
  → compute_bm25() for each candidate
  → Final Score = BM25 × (1 + PageRank × 10)
  → extract_snippet() for top results
  → Returns list of result dicts
```

### Database Schema

#### `documents` Table

```sql
CREATE TABLE documents (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    url        TEXT UNIQUE NOT NULL,
    title      TEXT,
    content    TEXT,
    doc_length INTEGER DEFAULT 0,
    pagerank   REAL    DEFAULT 0.0
)
```

| Column | Description |
|---|---|
| `id` | Auto-increment primary key |
| `url` | Wikipedia page URL (unique) |
| `title` | Page title derived from URL |
| `content` | Full plain-text page content |
| `doc_length` | Word count — used in BM25 length normalization |
| `pagerank` | Computed authority score |

#### `inverted_index` Table

```sql
CREATE TABLE inverted_index (
    word   TEXT    NOT NULL,
    doc_id INTEGER NOT NULL,
    tf     REAL    NOT NULL,
    PRIMARY KEY (word, doc_id),
    FOREIGN KEY (doc_id) REFERENCES documents(id)
)
```

| Column | Description |
|---|---|
| `word` | Indexed term (lowercase, 2+ characters) |
| `doc_id` | Document containing the term |
| `tf` | Raw term frequency count |

**Indexes:** `idx_word` on `word`; `idx_doc_id` on `doc_id`.

### BM25 Ranking Algorithm

```
score = Σ IDF(t) × (tf × (k1 + 1)) / (tf + k1 × (1 − b + b × |D| / avgdl))

IDF(t) = log((N − df + 0.5) / (df + 0.5) + 1)
```

| Symbol | Meaning | Default |
|---|---|---|
| `tf` | Term frequency in document | — |
| `|D|` | Document length (words) | — |
| `avgdl` | Average document length | — |
| `N` | Total number of documents | — |
| `df` | Documents containing the term | — |
| `k1` | Term frequency saturation | 1.5 |
| `b` | Length normalization | 0.75 |

### Final Scoring

```
Final Score = BM25(query, doc) × (1 + PageRank × 10)
```

PageRank acts as a multiplicative boost — authoritative pages score higher for the same keyword relevance.

### PageRank Algorithm

Uses the standard iterative power-method:

```
M = d × A + (1 − d) / n × ones(n, n)
ranks = M @ ranks   (repeat until convergence, max 50 iterations)
```

where `A` is the column-normalized adjacency matrix, `d = 0.85`, and convergence threshold is `1e-6`.

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### Quick Setup

```bash
git clone <repository-url>
cd Search-Engine
pip install -r requirements.txt
python main.py
```

Type **Y** when prompted on first run. Setup takes ~2–3 minutes for 100 pages.

### One-Click Scripts

```bash
bash start.sh      # Linux / macOS
start.bat          # Windows
```

### Dependencies

```
Flask>=2.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0
numpy>=1.24.0
```

---

## Development Guide

### Code Style

- **Formatting**: `black` with line length 100
- **Linting**: `flake8 --max-line-length=100`
- **Type hints**: use where practical; checked with `mypy`

```bash
pip install black flake8 mypy
black main.py search_engine.py --line-length=100
flake8 main.py search_engine.py --max-line-length=100
```

### Commit Messages

- Start with a verb: `Add`, `Fix`, `Update`, `Refactor`
- Keep the first line under 50 characters
- Reference issues when applicable: `Fixes #42`

### Pull Request Process

```bash
git checkout -b feature/your-feature-name
# make changes
git add .
git commit -m "Add: descriptive message"
git push origin feature/your-feature-name
# open Pull Request on GitHub
```

### Adding Features

All search logic lives in `search_engine.py`. The key extension points are:

- **More synonyms**: extend `MATH_SYNONYMS` dict
- **Different crawl source**: modify `crawl()` and `is_valid_wiki_url()`
- **Scoring tweak**: adjust the final score formula in `search()`
- **BM25 parameters**: change `BM25_K1` and `BM25_B` constants

---

## API & Usage

### Start the Web Application

```bash
python main.py
# Visit http://localhost:5000
```

### CLI Commands

```bash
python main.py                          # start web server
python main.py setup                    # initialize/reset database
python main.py search "linear algebra"  # search from terminal
python main.py stats                    # show document/term counts
```

### Programmatic Search

```python
from search_engine import search, get_stats

# Search
results = search("calculus derivatives", top_k=10)
for r in results:
    print(r['title'])        # page title
    print(r['url'])          # Wikipedia URL
    print(r['snippet'])      # HTML snippet with <mark> highlights
    print(r['score'])        # final combined score
    print(r['bm25_score'])   # raw BM25 component
    print(r['pagerank'])     # PageRank component

# Database statistics
stats = get_stats()
print(stats['documents'])    # number of indexed pages
print(stats['terms'])        # number of unique terms
```

### Run a Custom Crawl

```python
from search_engine import init_db, crawl, save_to_db

init_db()
link_graph, page_content = crawl(
    seed_url="https://en.wikipedia.org/wiki/Algebra",
    max_pages=500
)
save_to_db(page_content, link_graph)
```

---

## FAQ

### Installation

**Q: ModuleNotFoundError when running the app**

Install dependencies (activate your virtual environment first if using one):

```bash
pip install -r requirements.txt
```

**Q: How do I install for development?**

```bash
pip install -r requirements.txt
pip install black flake8 mypy pytest
```

### Database

**Q: Where is the database file?**

`search_engine.db` in the project root, set by `DB_PATH` in `search_engine.py`.

**Q: How do I reset the database?**

```bash
python main.py setup
# or manually:
rm search_engine.db
python main.py
```

**Q: How do I index more pages?**

Edit `max_pages` in the `setup_database()` function in `main.py`:

```python
link_graph, page_content = crawl(seed, max_pages=500)
```

**Q: Can I use existing data?**

Yes. Copy your `search_engine.db` into the project directory and run `python main.py` — it will detect the existing database and skip setup.

### Search

**Q: How do I run the web app?**

```bash
python main.py
# Opens at http://localhost:5000
```

**Q: Why does my query return no results?**

The default 100-page crawl covers core Wikipedia mathematics topics. Try simpler queries (`"calculus"`, `"algebra"`) or reinitialize with more pages.

**Q: How does query expansion work?**

Before searching, `expand_query()` splits the query into words and adds any known synonyms from `MATH_SYNONYMS`. For example, `"derivative"` also searches for `"differentiation"`.

---

## Contributing

Contributions are welcome. Please be respectful and constructive in all interactions.

### Areas for Contribution

- Additional mathematical synonyms
- Performance optimizations (caching, index compression)
- UI/UX improvements
- Crawl sources beyond Wikipedia
- Bug reports and fixes
- Documentation and examples

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test locally
4. Run linting: `flake8 main.py search_engine.py`
5. Format code: `black main.py search_engine.py --line-length=100`
6. Commit with a clear message
7. Open a Pull Request

---

## Changelog

### [1.0.0] — 2024-05-21

#### Added

- Initial release of MathSearch
- BM25 ranking algorithm
- PageRank authority scoring
- Synonym-based query expansion
- Intelligent snippet extraction with term highlighting
- Flask web application with responsive UI
- SQLite database with normalized two-table schema
- Wikipedia web crawler
- CLI interface (`setup`, `search`, `stats` commands)
- One-click startup scripts (`start.sh`, `start.bat`)
- Auto-setup on first run

#### Architecture

Consolidated from a 10-file prototype into two core files:

- `search_engine.py` — merges former `database.py`, `crawler.py`, `indexer.py`, `pagerank.py`, `query_expansion.py`, `snippets.py`, `search.py`, `config.py`
- `main.py` — merges former `app.py` and `init.py`

#### Dependencies Reduced

Removed `sentence-transformers`, `torch`, and `pyspellchecker`. Kept only `Flask`, `requests`, `beautifulsoup4`, `numpy`.

### [Unreleased]

#### Planned

- Optional semantic re-ranking (pluggable, off by default)
- Search result caching
- Configurable crawl depth
- Additional domain synonym sets
- Multi-language support
