# How to Run MathSearch — Complete Guide

A step-by-step guide to get MathSearch up and running on your computer.

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [System Requirements](#system-requirements)
3. [Detailed Installation](#detailed-installation)
4. [Running the Project](#running-the-project)
5. [Troubleshooting](#troubleshooting)
6. [Project Structure](#project-structure)

---

## Quick Start

If you have Python 3.8+ already installed:

```bash
# 1. Get the code
git clone <repository-url>
cd Search-Engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py

# 4. Open browser → http://localhost:5000
```

On first run, you will be prompted to initialize the database. Type **Y** and press Enter. Setup takes ~2–3 minutes, then the web server starts automatically.

---

## System Requirements

| Item | Minimum | Recommended |
|---|---|---|
| OS | Windows, macOS, Linux | Any |
| Python | 3.8 | 3.10+ |
| RAM | 512 MB | 1 GB |
| Disk | 50 MB | 200 MB |
| Internet | Required (first run only) | — |

### Check your Python version

```bash
python --version
# Should output: Python 3.8.x or higher
```

If Python is not installed:

- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`

---

## Detailed Installation

### Step 1: Get the Code

```bash
git clone <repository-url>
cd Search-Engine
```

Or download as a ZIP from GitHub and extract it.

### Step 2: (Optional) Create a Virtual Environment

Isolates this project's packages from your system Python:

```bash
# Create
python -m venv venv

# Activate — macOS/Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs four packages:

| Package | Purpose |
|---|---|
| Flask | Web framework |
| requests | HTTP client for the crawler |
| beautifulsoup4 | HTML parsing |
| numpy | PageRank matrix computation |

Installation typically takes under a minute.

### Step 4: Verify Installation

```bash
python -c "import flask, requests, bs4, numpy; print('All packages installed!')"
```

---

## Running the Project

### Option A: Full Setup (Recommended for First Time)

Just run the application — it will prompt you to set up automatically:

```bash
python main.py
```

You will see:

```
⚠️  Database not found!

First-time setup required.
Initialize database now? (Y/n): Y

============================================================
MathSearch Setup
============================================================

Initializing database...

Crawling Wikipedia...
This will take a few minutes...
INFO: Crawling from https://en.wikipedia.org/wiki/Mathematics (max 100 pages)...
INFO: Crawled 10/100 pages
...
INFO: Crawl complete: 100 pages

Building search index...

============================================================
Setup Complete!
Documents: 100
Terms: 45231
============================================================

============================================================
MathSearch - Starting Web Server
============================================================
Documents indexed: 100
Terms indexed: 45231

Open your browser to: http://localhost:5000
Press Ctrl+C to stop
============================================================
```

### Option B: Manual Setup Then Run

```bash
# Initialize database only
python main.py setup

# Then start the server separately
python main.py
```

### Option C: One-Click Start Scripts

```bash
# Linux / macOS
bash start.sh

# Windows
start.bat
```

These scripts install dependencies and start the app in one step.

### Step: Open in Browser

Visit **http://localhost:5000**

You will see the MathSearch home page with a search box.

### Step: Try a Search

- `calculus` — basic math search
- `differential equations` — multi-word query
- `linear algebra` — finds matrix-related topics
- `derivative` — auto-expands to include "differentiation"

### Step: Stop the Server

Press **Ctrl+C** in the terminal.

---

## Available Commands

```bash
# Start web server (default)
python main.py

# Initialize or reset the database
python main.py setup

# Search from the command line
python main.py search "calculus derivatives"

# Show database statistics
python main.py stats
```

### Command-Line Search Output

```
Searching for: calculus derivatives

Found 5 results:

1. Calculus
   Score: 12.453
   https://en.wikipedia.org/wiki/Calculus

2. Derivative
   Score: 10.871
   https://en.wikipedia.org/wiki/Derivative
```

---

## Understanding Results

Each result in the web interface shows:

```
[Page Title]  ← clickable link
https://en.wikipedia.org/wiki/...

Relevant excerpt with highlighted terms...

Score: 12.453
```

**Score** is the combined ranking: `BM25 × (1 + PageRank × 10)`. Higher is better.

The footer of the page shows total documents and terms indexed.

---

## Configuration

All settings are in `search_engine.py` near the top of the file:

```python
DB_PATH        = "search_engine.db"   # Database file location
BM25_K1        = 1.5                  # Term frequency saturation (1.2–2.0)
BM25_B         = 0.75                 # Length normalization (0–1)
SNIPPET_LENGTH = 200                  # Characters shown in each snippet
```

### To crawl more pages for better coverage:

Edit `main.py` in the `setup_database()` function:

```python
link_graph, page_content = crawl(seed, max_pages=500)  # change 100 → 500
```

More pages = better results, but longer setup time (~1 minute per 30 pages).

### To add synonyms:

Edit `MATH_SYNONYMS` in `search_engine.py`:

```python
MATH_SYNONYMS = {
    "calc":  ["calculus"],
    "stats": ["statistics", "probability"],
    # Add your own...
}
```

---

## Project Structure After Running

```
Search-Engine/
├── main.py              — Entry point and web server
├── search_engine.py     — All core search logic
├── requirements.txt     — 4 dependencies
├── search_engine.db     ✓ Created after first run
├── start.sh             — One-click start (Linux/macOS)
├── start.bat            — One-click start (Windows)
├── README.md            — Project overview
├── README.txt           — Plain-text quick reference
├── HOW_TO_RUN.md        — This file
├── DOCUMENTATION.md     — Full technical documentation
└── LICENSE              — MIT License
```

---

## Troubleshooting

### "Python not found"

Try `python3` instead of `python`. On Windows, ensure Python is added to PATH (check during installation or search "Edit environment variables").

### "ModuleNotFoundError: No module named 'flask'"

The virtual environment may not be active, or dependencies were not installed:

```bash
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### "Address already in use" (port 5000)

Another process is using port 5000. Kill it or change the port in `main.py`:

```python
app.run(debug=False, host='0.0.0.0', port=8080)
```

Then visit `http://localhost:8080`.

### "Database not found" or no results

Re-initialize the database:

```bash
python main.py setup
```

### Search returns no results

Make sure setup completed successfully, then try simpler queries. The default crawl covers 100 pages starting from the Wikipedia Mathematics article, so highly obscure topics may not be indexed.

### Crawling is slow

The default 100-page crawl takes ~2–3 minutes. If it is much slower, your internet connection may be throttled by Wikipedia. Try:

```bash
# Crawl fewer pages
# Edit max_pages=50 in main.py setup_database(), then:
python main.py setup
```

### Out of memory

This should not occur with the default setup (~50 MB RAM). If it does, reduce the number of crawled pages.

---

## Getting Help

1. Read the error message carefully — it usually says exactly what is wrong
2. Check **DOCUMENTATION.md** for full technical details
3. Check **README.md** for a project overview
4. Refer to the PDF guides included in the repository

---

## Summary: The 3-Step Setup

```bash
pip install -r requirements.txt
python main.py          # type Y when prompted
# Open http://localhost:5000
```

That's all it takes. Enjoy MathSearch! 🔢🔍
