# MathSearch - Advanced Mathematical Search Engine

A sophisticated search engine optimized for mathematical content with BM25 ranking, semantic re-ranking, and intelligent query expansion.

## Features

- **BM25 Ranking**: Industry-standard information retrieval ranking algorithm
- **Hybrid Semantic Re-ranking**: Optional two-stage retrieval using sentence transformers for semantic similarity
- **Query Expansion**: Spell correction, synonym expansion, and optional LLM-based expansion
- **Intelligent Snippet Extraction**: Context-aware snippets with relevant sentences around matches
- **PageRank Scoring**: Link-based authority scoring integrated into results
- **Modern Web Interface**: Beautiful, responsive UI built with Flask
- **Mathematical Synonyms**: Domain-specific synonym expansion for math terminology

## Architecture

The search engine consists of several modular components:

### Core Components

- **app.py**: Flask web application with UI and search endpoints
- **search.py**: Two-stage BM25 and semantic search implementation
- **database.py**: SQLite database management with normalized schema
- **config.py**: Centralized configuration for all tunable parameters

### Data Processing

- **crawler.py**: Web crawler for Wikipedia math pages
- **indexer.py**: Inverted index builder with BM25 support
- **pagerank.py**: PageRank computation for link graph authority scoring
- **snippets.py**: Intelligent snippet extraction from documents

### Query Processing

- **query_expansion.py**: Spell correction and synonym expansion

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Search-Engine
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Initialize the Search Engine

```python
from indexer import rebuild_index
rebuild_index()
```

This will:
1. Initialize the SQLite database
2. Crawl Wikipedia pages (starting from a seed URL)
3. Build the inverted index with BM25 support
4. Compute PageRank scores
5. Save all data to the database

### Run the Web Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Perform Searches Programmatically

```python
from search import search

# Perform a search
results = search("calculus derivatives", top_k=10)

# Results include:
# - title: Page title
# - url: Page URL
# - snippet: Extracted relevant snippet
# - score: Combined BM25 + semantic score
# - pagerank: PageRank score
```

## Configuration

All tunable parameters are centralized in `config.py`:

### BM25 Parameters
- `BM25_K1`: Term frequency saturation (default: 1.5)
- `BM25_B`: Length normalization (default: 0.75)

### Hybrid Search
- `ENABLE_HYBRID`: Enable semantic re-ranking (default: True)
- `HYBRID_LAMBDA`: Weight for semantic similarity (default: 0.5)
- `TOP_K_CANDIDATES`: Candidates for re-ranking (default: 100)
- `SENTENCE_TRANSFORMER_MODEL`: Model name (default: "all-MiniLM-L6-v2")

### Query Expansion
- `ENABLE_SPELL_CORRECTION`: Enable spell checker (default: True)
- `ENABLE_SYNONYM_EXPANSION`: Enable synonyms (default: True)
- `ENABLE_LLM_EXPANSION`: Enable LLM expansion (default: False)

### Snippet Extraction
- `SNIPPET_LENGTH`: Character context around matches (default: 150)
- `SNIPPET_CONTEXT_SENTENCES`: Surrounding sentences (default: 2)

## Database Schema

### documents table
- `id`: Auto-increment document ID
- `url`: Unique page URL
- `title`: Page title
- `content`: Full text content
- `doc_length`: Total word count
- `pagerank`: Computed PageRank score

### inverted_index table
- `word`: Index term
- `doc_id`: Document ID (foreign key)
- `tf`: Term frequency in document

## Algorithm Details

### BM25 Scoring

The BM25 (Best Matching 25) algorithm provides relevance scores:

```
score = Σ IDF(term) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (|D| / avgdl)))
```

Where:
- `IDF(term)` = log((N - df + 0.5) / (df + 0.5) + 1)
- `tf` = term frequency in document
- `|D|` = document length
- `avgdl` = average document length
- `k1`, `b` = tuning parameters

### Hybrid Search

When enabled, BM25 results are re-ranked using semantic similarity:

```
hybrid_score = (1 - λ) * bm25_score + λ * cosine_similarity
```

Using sentence-transformers for semantic embeddings.

### PageRank Computation

PageRank is computed using the standard iterative algorithm:

```
PR(A) = (1 - d) + d * Σ(PR(Ti) / C(Ti))
```

Where:
- `d` = damping factor (0.85)
- `Ti` = pages linking to A
- `C(Ti)` = outbound link count from Ti

## Development

### Project Structure

```
Search-Engine/
├── app.py                    # Flask web application
├── config.py                 # Configuration parameters
├── search.py                 # BM25 and hybrid search
├── database.py               # SQLite database management
├── crawler.py                # Web crawler
├── indexer.py                # Index builder
├── pagerank.py               # PageRank computation
├── query_expansion.py        # Query processing
├── snippets.py               # Snippet extraction
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Running Tests

```bash
python -m pytest
```

## Performance Tips

1. **Indexing**: The initial crawl and indexing can take time. Use smaller `max_pages` for testing.
2. **Semantic Re-ranking**: First load of sentence transformer downloads the model (~60MB).
3. **Database**: Ensure sufficient disk space for SQLite database.
4. **Tuning**: Adjust BM25 parameters in `config.py` based on your domain.

## Troubleshooting

### Import Errors
Ensure all files are in the same directory and virtual environment is activated.

### Database Errors
Delete `search_engine.db` and rebuild the index:
```bash
python -c "from indexer import rebuild_index; rebuild_index()"
```

### Memory Issues with Sentence Transformers
Disable hybrid search in config.py:
```python
ENABLE_HYBRID = False
```

### Slow Searches
Reduce `TOP_K_CANDIDATES` in config.py for faster semantic re-ranking.

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library
- **BeautifulSoup4**: HTML parsing
- **numpy**: Numerical computing
- **pyspellchecker**: Spell correction
- **sentence-transformers**: Semantic embeddings
- **torch**: Deep learning (required by sentence-transformers)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

For questions or issues, please open a GitHub issue.

---

**Note**: This search engine is optimized for mathematical content but can be adapted for any domain by adjusting the synonyms dictionary and crawl sources.
