# MathSearch - Mathematical Search Engine

A streamlined search engine optimized for mathematical content with BM25 ranking, PageRank authority scoring, and intelligent query expansion.

## Features

- **BM25 Ranking**: Industry-standard information retrieval ranking algorithm
- **PageRank Scoring**: Link-based authority scoring integrated into results
- **Query Expansion**: Automatic synonym expansion for math terminology
- **Intelligent Snippet Extraction**: Context-aware snippets with highlighted matches
- **Modern Web Interface**: Beautiful, responsive UI built with Flask
- **Lightweight & Fast**: No heavy ML dependencies — runs on ~10 MB, ~50 MB RAM

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Search-Engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

On first run you will be prompted to initialize the database. Say **Y** and it will:

1. Crawl ~100 Wikipedia mathematics pages (~2–3 minutes)
2. Build the inverted index
3. Compute PageRank scores
4. Start the web server at **http://localhost:5000**

Subsequent runs go straight to the web server.

### One-Click Start

```bash
# Linux / macOS
bash start.sh

# Windows
start.bat
```

---

## Commands

```bash
# Start web server (default)
python main.py

# Initialize / reset database
python main.py setup

# Search from the command line
python main.py search "calculus derivatives"

# Show database statistics
python main.py stats
```

---

## Architecture

The entire project is **two Python files**:

| File | Lines | Purpose |
|---|---|---|
| `main.py` | ~270 | Flask web app, CLI entry point, auto-setup |
| `search_engine.py` | ~450 | All core logic: crawler, indexer, PageRank, BM25, snippets, query expansion |

### How It Works

```
Stage 1 — Crawl      Wikipedia pages downloaded via requests + BeautifulSoup
Stage 2 — Index      Words tokenized; inverted index built with term frequencies
Stage 3 — PageRank   Authority scores computed from the link graph (NumPy)
Stage 4 — Search     Query expanded with synonyms → BM25 scored → PageRank boosted
Stage 5 — Snippets   Relevant excerpt extracted and query terms highlighted
Stage 6 — Display    Results rendered in Flask web UI
```

### Scoring Formula

```
Final Score = BM25(query, doc) × (1 + PageRank × 10)
```

BM25 formula:

```
score = Σ IDF(t) × (tf × (k1 + 1)) / (tf + k1 × (1 − b + b × |D| / avgdl))
```

---

## Configuration

All tunable parameters live at the top of `search_engine.py`:

```python
DB_PATH        = "search_engine.db"  # SQLite database path
BM25_K1        = 1.5                 # Term frequency saturation (range: 1.2–2.0)
BM25_B         = 0.75                # Length normalization (range: 0–1)
SNIPPET_LENGTH = 200                 # Characters around the best match
```

### Mathematical Synonyms

```python
MATH_SYNONYMS = {
    "calc":        ["calculus"],
    "calculus":    ["calc", "integration", "differentiation"],
    "diff eq":     ["differential equation", "ode"],
    "integral":    ["integration"],
    "derivative":  ["differentiation"],
    "matrix":      ["matrices"],
    "trig":        ["trigonometry"],
    "algebra":     ["alg"],
    "geometry":    ["geom"],
    "probability": ["prob", "statistics"],
}
```

Add your own terms to extend query expansion.

---

## Database Schema

SQLite database (`search_engine.db`) with two tables:

### `documents`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment document ID |
| `url` | TEXT UNIQUE | Wikipedia page URL |
| `title` | TEXT | Page title |
| `content` | TEXT | Full page text |
| `doc_length` | INTEGER | Word count (for BM25 normalization) |
| `pagerank` | REAL | Authority score |

### `inverted_index`

| Column | Type | Description |
|---|---|---|
| `word` | TEXT PK | Indexed term (lowercase) |
| `doc_id` | INTEGER PK | Document containing the term |
| `tf` | REAL | Term frequency in that document |

---

## File Structure

```
Search-Engine/
├── main.py            — Entry point and web server
├── search_engine.py   — Core search engine logic
├── requirements.txt   — Python dependencies (4 packages)
├── search_engine.db   — SQLite database (auto-created)
├── start.sh           — One-click start (Linux/macOS)
├── start.bat          — One-click start (Windows)
├── README.md          — This file
├── README.txt         — Plain-text quick reference
├── HOW_TO_RUN.md      — Detailed setup guide
├── DOCUMENTATION.md   — Full technical documentation
└── LICENSE            — MIT License
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Flask | ≥2.3.0 | Web framework |
| requests | ≥2.31.0 | HTTP client for crawler |
| beautifulsoup4 | ≥4.12.0 | HTML parsing |
| numpy | ≥1.24.0 | PageRank matrix computation |

---

## Programmatic Usage

```python
from search_engine import search, get_stats

# Search
results = search("calculus derivatives", top_k=10)
for r in results:
    print(r['title'], r['score'])

# Stats
stats = get_stats()
print(f"{stats['documents']} documents, {stats['terms']} terms")
```

---

## Troubleshooting

**ModuleNotFoundError** — run `pip install -r requirements.txt`

**Database not found** — run `python main.py setup`

**Port 5000 in use** — kill the other process or edit `main.py` to use a different port

**No results** — ensure the database is initialized and try simpler queries like `"calculus"`

---

## Performance Notes

- Search speed: < 100 ms for typical queries
- Memory usage: ~50 MB (no ML models loaded)
- Disk space: ~5 MB database for 100 pages
- Setup time: ~2–3 minutes for default 100-page crawl

---

## License

MIT License — see `LICENSE` for details.

## Contributing

Contributions welcome! Please fork the repo, create a feature branch, and open a Pull Request. See `DOCUMENTATION.md` for development guidelines.
