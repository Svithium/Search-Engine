"""
Database module with normalized schema for better performance and scalability.
Schema:
  - documents: stores page metadata and content
  - inverted_index: term frequencies for each document
"""

import sqlite3
import logging
from config import DATABASE_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database with normalized schema."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Documents table: normalized structure with PageRank
        c.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            content TEXT,
            doc_length INTEGER DEFAULT 0,
            pagerank REAL DEFAULT 0.0
        )''')
        
        # Inverted index: word -> doc_id with term frequency
        c.execute('''CREATE TABLE IF NOT EXISTS inverted_index (
            word TEXT NOT NULL,
            doc_id INTEGER NOT NULL,
            tf REAL NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(id),
            PRIMARY KEY (word, doc_id)
        )''')
        
        # Create indexes for faster queries
        c.execute('CREATE INDEX IF NOT EXISTS idx_word ON inverted_index(word)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_doc_id ON inverted_index(doc_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_url ON documents(url)')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()


def save_pages(page_content):
    """
    Save crawled pages to documents table.
    
    Args:
        page_content: dict mapping URL to content text
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        saved_count = 0
        for url, content in page_content.items():
            # Extract title from URL or content
            title = url.split('/wiki/')[-1].replace('_', ' ') if '/wiki/' in url else url
            
            c.execute('''INSERT OR REPLACE INTO documents (url, title, content) 
                         VALUES (?, ?, ?)''', (url, title, content))
            saved_count += 1
        
        conn.commit()
        logger.info(f"Saved {saved_count} pages to database")
        
    except sqlite3.Error as e:
        logger.error(f"Error saving pages: {e}")
        raise
    finally:
        conn.close()


def save_index(word_doc_tf):
    """
    Save inverted index with term frequencies.
    
    Args:
        word_doc_tf: dict of {word: [(doc_id, tf), ...]}
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Clear existing index
        c.execute('DELETE FROM inverted_index')
        
        # Batch insert for better performance
        batch = []
        for word, doc_tfs in word_doc_tf.items():
            for doc_id, tf in doc_tfs:
                batch.append((word, doc_id, tf))
        
        c.executemany('INSERT INTO inverted_index (word, doc_id, tf) VALUES (?, ?, ?)', 
                      batch)
        
        conn.commit()
        logger.info(f"Saved inverted index with {len(word_doc_tf)} unique terms")
        
    except sqlite3.Error as e:
        logger.error(f"Error saving index: {e}")
        raise
    finally:
        conn.close()


def update_doc_lengths(doc_lengths):
    """
    Update document lengths in the database.
    
    Args:
        doc_lengths: dict mapping doc_id to document length
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        for doc_id, length in doc_lengths.items():
            c.execute('UPDATE documents SET doc_length = ? WHERE id = ?', 
                     (length, doc_id))
        
        conn.commit()
        logger.info(f"Updated document lengths for {len(doc_lengths)} documents")
        
    except sqlite3.Error as e:
        logger.error(f"Error updating document lengths: {e}")
        raise
    finally:
        conn.close()


def save_pagerank(ranks):
    """
    Save PageRank scores to documents table.
    
    Args:
        ranks: dict mapping URL to PageRank score
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        count = 0
        for url, score in ranks.items():
            c.execute('UPDATE documents SET pagerank = ? WHERE url = ?', 
                     (score, url))
            if c.rowcount > 0:
                count += 1
        
        conn.commit()
        logger.info(f"Saved PageRank scores for {count} documents")
        
    except sqlite3.Error as e:
        logger.error(f"Error saving PageRank: {e}")
        raise
    finally:
        conn.close()


def get_all_documents():
    """
    Retrieve all documents with metadata.
    
    Returns:
        List of tuples: (doc_id, url, title, content, doc_length, pagerank)
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('SELECT id, url, title, content, doc_length, pagerank FROM documents')
        docs = c.fetchall()
        
        return docs
        
    except sqlite3.Error as e:
        logger.error(f"Error loading documents: {e}")
        raise
    finally:
        conn.close()


def get_inverted_index():
    """
    Load the complete inverted index.
    
    Returns:
        dict: {word: [(doc_id, tf), ...]}
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('SELECT word, doc_id, tf FROM inverted_index')
        
        index = {}
        for word, doc_id, tf in c.fetchall():
            if word not in index:
                index[word] = []
            index[word].append((doc_id, tf))
        
        logger.info(f"Loaded inverted index with {len(index)} unique terms")
        return index
        
    except sqlite3.Error as e:
        logger.error(f"Error loading inverted index: {e}")
        raise
    finally:
        conn.close()


def get_document_by_id(doc_id):
    """
    Retrieve a single document by ID.
    
    Args:
        doc_id: Document ID
        
    Returns:
        tuple: (id, url, title, content, doc_length, pagerank) or None
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('''SELECT id, url, title, content, doc_length, pagerank 
                     FROM documents WHERE id = ?''', (doc_id,))
        doc = c.fetchone()
        
        return doc
        
    except sqlite3.Error as e:
        logger.error(f"Error loading document {doc_id}: {e}")
        return None
    finally:
        conn.close()


def get_avg_doc_length():
    """
    Calculate average document length across all documents.
    
    Returns:
        float: Average document length
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('SELECT AVG(doc_length) FROM documents WHERE doc_length > 0')
        result = c.fetchone()
        
        avg_length = result[0] if result and result[0] else 0
        return avg_length
        
    except sqlite3.Error as e:
        logger.error(f"Error calculating average document length: {e}")
        return 0
    finally:
        conn.close()


def get_document_count():
    """
    Get total number of documents in database.
    
    Returns:
        int: Number of documents
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM documents')
        count = c.fetchone()[0]
        
        return count
        
    except sqlite3.Error as e:
        logger.error(f"Error counting documents: {e}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    # Initialize database
    init_db()
    print("Database initialized successfully")
