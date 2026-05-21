"""
MathSearch - Consolidated Search Engine Module
Contains database, indexing, search, and utility functions.
"""

import sqlite3
import re
import math
import logging
from collections import defaultdict, deque
import requests
from bs4 import BeautifulSoup
import urllib.parse
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_PATH = "search_engine.db"
BM25_K1 = 1.5
BM25_B = 0.75
SNIPPET_LENGTH = 200

MATH_SYNONYMS = {
    "calc": ["calculus"],
    "calculus": ["calc", "integration", "differentiation"],
    "diff eq": ["differential equation", "ode"],
    "integral": ["integration"],
    "derivative": ["differentiation"],
    "matrix": ["matrices"],
    "trig": ["trigonometry"],
    "algebra": ["alg"],
    "geometry": ["geom"],
    "probability": ["prob", "statistics"],
}

# ============================================================================
# DATABASE
# ============================================================================

def init_db():
    """Initialize database schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        title TEXT,
        content TEXT,
        doc_length INTEGER DEFAULT 0,
        pagerank REAL DEFAULT 0.0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS inverted_index (
        word TEXT NOT NULL,
        doc_id INTEGER NOT NULL,
        tf REAL NOT NULL,
        PRIMARY KEY (word, doc_id)
    )''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_word ON inverted_index(word)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_doc_id ON inverted_index(doc_id)')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")


def save_to_db(page_content, link_graph):
    """Save crawled data and build index."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Save documents
    url_to_id = {}
    for url, content in page_content.items():
        title = url.split('/wiki/')[-1].replace('_', ' ') if '/wiki/' in url else url
        c.execute('INSERT OR REPLACE INTO documents (url, title, content) VALUES (?, ?, ?)',
                  (url, title, content))
        c.execute('SELECT id FROM documents WHERE url = ?', (url,))
        url_to_id[url] = c.fetchone()[0]
    
    # Build index
    inverted_index = defaultdict(list)
    doc_lengths = {}
    
    for url, content in page_content.items():
        doc_id = url_to_id[url]
        words = tokenize(content)
        
        if words:
            word_count = defaultdict(int)
            for word in words:
                word_count[word] += 1
            
            doc_lengths[doc_id] = len(words)
            
            for word, count in word_count.items():
                inverted_index[word].append((doc_id, count))
    
    # Save index
    c.execute('DELETE FROM inverted_index')
    batch = [(word, doc_id, tf) for word, docs in inverted_index.items() 
             for doc_id, tf in docs]
    c.executemany('INSERT INTO inverted_index (word, doc_id, tf) VALUES (?, ?, ?)', batch)
    
    # Update document lengths
    for doc_id, length in doc_lengths.items():
        c.execute('UPDATE documents SET doc_length = ? WHERE id = ?', (length, doc_id))
    
    # Calculate and save PageRank
    pagerank_scores = compute_pagerank(link_graph, url_to_id)
    for url, score in pagerank_scores.items():
        if url in url_to_id:
            c.execute('UPDATE documents SET pagerank = ? WHERE id = ?', 
                     (score, url_to_id[url]))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(page_content)} documents and built index")


# ============================================================================
# WEB CRAWLER
# ============================================================================

def crawl(seed_url, max_pages=100):
    """Crawl Wikipedia pages."""
    visited = set()
    queue = deque([seed_url])
    link_graph = {}
    page_content = {}

    logger.info(f"Crawling from {seed_url} (max {max_pages} pages)...")

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            page_content[url] = soup.get_text(separator=' ', strip=True)
            
            # Extract links
            links = []
            for tag in soup.find_all('a', href=True):
                full_url = urllib.parse.urljoin(url, tag['href'])
                if is_valid_wiki_url(full_url):
                    links.append(full_url)
                    if full_url not in visited:
                        queue.append(full_url)
            
            link_graph[url] = links
            visited.add(url)
            
            if len(visited) % 10 == 0:
                logger.info(f"Crawled {len(visited)}/{max_pages} pages")
                
        except Exception as e:
            logger.warning(f"Error crawling {url}: {e}")
            continue

    logger.info(f"Crawl complete: {len(page_content)} pages")
    return link_graph, page_content


def is_valid_wiki_url(url):
    """Check if URL is a valid Wikipedia page."""
    if 'en.wikipedia.org/wiki' not in url:
        return False
    
    exclude = ['Wikipedia:', 'Help:', 'Portal:', 'Special:', 'Talk:',
               'File:', 'Category:', 'Template:', '#']
    
    return not any(pattern in url for pattern in exclude)


# ============================================================================
# PAGERANK
# ============================================================================

def compute_pagerank(link_graph, url_to_id, damping=0.85, max_iter=50):
    """Compute PageRank scores."""
    pages = list(link_graph.keys())
    n = len(pages)
    
    if n == 0:
        return {}
    
    page_index = {page: i for i, page in enumerate(pages)}
    adjacency = np.zeros((n, n))
    
    for page, links in link_graph.items():
        i = page_index[page]
        valid_links = [l for l in links if l in page_index]
        
        if valid_links:
            for link in valid_links:
                j = page_index[link]
                adjacency[j][i] = 1.0 / len(valid_links)
        else:
            adjacency[:, i] = 1.0 / n
    
    pagerank_matrix = damping * adjacency + (1 - damping) / n * np.ones((n, n))
    ranks = np.ones(n) / n
    
    for _ in range(max_iter):
        new_ranks = pagerank_matrix @ ranks
        if np.linalg.norm(new_ranks - ranks) < 1e-6:
            break
        ranks = new_ranks
    
    return {pages[i]: float(ranks[i]) for i in range(n)}


# ============================================================================
# TOKENIZATION & QUERY PROCESSING
# ============================================================================

def tokenize(text):
    """Tokenize text into words."""
    return re.findall(r'\b[a-z]{2,}\b', text.lower())


def expand_query(query):
    """Expand query with synonyms."""
    words = set(query.lower().split())
    
    for word in list(words):
        if word in MATH_SYNONYMS:
            words.update(MATH_SYNONYMS[word])
    
    return words


# ============================================================================
# SEARCH ENGINE
# ============================================================================

def search(query, top_k=10):
    """Search with BM25 ranking."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all documents
    c.execute('SELECT id, url, title, content, doc_length, pagerank FROM documents')
    docs = c.fetchall()
    
    if not docs:
        conn.close()
        return []
    
    doc_map = {d[0]: d for d in docs}
    
    # Get inverted index
    c.execute('SELECT word, doc_id, tf FROM inverted_index')
    inverted_index = defaultdict(list)
    for word, doc_id, tf in c.fetchall():
        inverted_index[word].append((doc_id, tf))
    
    conn.close()
    
    # Calculate average document length
    avg_doc_length = sum(d[4] for d in docs) / len(docs)
    total_docs = len(docs)
    
    # Expand query
    query_terms = expand_query(query)
    
    # Find candidate documents
    candidates = set()
    for term in query_terms:
        if term in inverted_index:
            candidates.update(doc_id for doc_id, _ in inverted_index[term])
    
    if not candidates:
        return []
    
    # Score with BM25
    scored_docs = []
    for doc_id in candidates:
        bm25_score = compute_bm25(doc_id, query_terms, inverted_index, 
                                  doc_map[doc_id][4], avg_doc_length, total_docs)
        pagerank = doc_map[doc_id][5]
        final_score = bm25_score * (1 + pagerank * 10)
        scored_docs.append((doc_id, final_score, bm25_score, pagerank))
    
    # Sort and format results
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    for doc_id, score, bm25, pr in scored_docs[:top_k]:
        doc = doc_map[doc_id]
        snippet = extract_snippet(doc[3], query_terms)
        
        results.append({
            'url': doc[1],
            'title': doc[2],
            'snippet': snippet,
            'score': score,
            'bm25_score': bm25,
            'pagerank': pr
        })
    
    return results


def compute_bm25(doc_id, query_terms, inverted_index, doc_length, avg_doc_length, total_docs):
    """Compute BM25 score."""
    score = 0.0
    
    for term in query_terms:
        if term not in inverted_index:
            continue
        
        # Get term frequency
        tf = 0
        for d_id, freq in inverted_index[term]:
            if d_id == doc_id:
                tf = freq
                break
        
        if tf == 0:
            continue
        
        # IDF
        df = len(inverted_index[term])
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        
        # BM25
        numerator = tf * (BM25_K1 + 1)
        denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / avg_doc_length))
        
        score += idf * (numerator / denominator)
    
    return score


# ============================================================================
# SNIPPET EXTRACTION
# ============================================================================

def extract_snippet(content, query_terms, max_length=SNIPPET_LENGTH):
    """Extract relevant snippet from content."""
    if not content:
        return "No preview available."
    
    content = re.sub(r'\s+', ' ', content).strip()
    content_lower = content.lower()
    
    # Find first occurrence of any query term
    best_pos = len(content)
    for term in query_terms:
        pos = content_lower.find(term)
        if pos != -1 and pos < best_pos:
            best_pos = pos
    
    # If no match, return beginning
    if best_pos == len(content):
        snippet = content[:max_length]
        return snippet + "..." if len(content) > max_length else snippet
    
    # Extract snippet centered on match
    start = max(0, best_pos - max_length // 3)
    end = min(len(content), start + max_length)
    snippet = content[start:end].strip()
    
    # Add ellipses
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""
    
    # Highlight query terms
    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        snippet = pattern.sub(lambda m: f'<mark>{m.group(0)}</mark>', snippet)
    
    return prefix + snippet + suffix


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_stats():
    """Get database statistics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM documents')
    num_docs = c.fetchone()[0]
    
    c.execute('SELECT COUNT(DISTINCT word) FROM inverted_index')
    num_terms = c.fetchone()[0]
    
    conn.close()
    
    return {'documents': num_docs, 'terms': num_terms}
