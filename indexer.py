"""
Indexer with BM25 support. Builds inverted index with term frequencies.
Removed all TF-IDF code - now only stores term frequencies and document lengths.
"""

import re
import logging
from collections import defaultdict
from database import (
    init_db, save_pages, save_index, update_doc_lengths, 
    get_all_documents, get_document_count
)
from crawler import load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tokenize(text):
    """
    Tokenize text into words.
    
    Args:
        text: Input text
        
    Returns:
        List of lowercase words (length >= 2)
    """
    # Extract words (2+ characters, alphabetic)
    words = re.findall(r'\b[a-z]{2,}\b', text.lower())
    return words


def build_index(page_content):
    """
    Build inverted index with term frequencies for BM25.
    No TF-IDF computation - just raw term frequencies.
    
    Args:
        page_content: dict mapping URL to content text
        
    Returns:
        tuple: (inverted_index, doc_lengths)
            - inverted_index: {word: [(doc_id, tf), ...]}
            - doc_lengths: {doc_id: total_word_count}
    """
    logger.info(f"Building index for {len(page_content)} documents...")
    
    # Get all documents from database to get doc_ids
    docs = get_all_documents()
    url_to_docid = {url: doc_id for doc_id, url, _, _, _, _ in docs}
    
    inverted_index = defaultdict(list)
    doc_lengths = {}
    
    for url, content in page_content.items():
        if url not in url_to_docid:
            logger.warning(f"URL {url} not found in database, skipping")
            continue
        
        doc_id = url_to_docid[url]
        
        # Tokenize
        words = tokenize(content)
        
        if not words:
            logger.warning(f"No words found for doc_id {doc_id}")
            continue
        
        # Count word frequencies
        word_count = defaultdict(int)
        for word in words:
            word_count[word] += 1
        
        # Store document length (total words)
        doc_lengths[doc_id] = len(words)
        
        # Build inverted index with term frequencies
        for word, count in word_count.items():
            # Store raw term frequency (count)
            inverted_index[word].append((doc_id, count))
    
    logger.info(f"Index built: {len(inverted_index)} unique terms, "
                f"{len(doc_lengths)} documents")
    
    return dict(inverted_index), doc_lengths


def rebuild_index():
    """
    Complete index rebuilding process:
    1. Load crawled data
    2. Save pages to database
    3. Build inverted index
    4. Save index and document lengths
    """
    logger.info("Starting index rebuild process...")
    
    # Step 1: Initialize database
    init_db()
    
    # Step 2: Load crawled data
    logger.info("Loading crawled data...")
    try:
        _, page_content = load_data()
    except FileNotFoundError:
        logger.error("Crawled data not found. Run crawler.py first!")
        return
    
    # Step 3: Save pages to database
    logger.info("Saving pages to database...")
    save_pages(page_content)
    
    # Step 4: Build index
    logger.info("Building inverted index...")
    inverted_index, doc_lengths = build_index(page_content)
    
    # Step 5: Save index to database
    logger.info("Saving index to database...")
    save_index(inverted_index)
    
    # Step 6: Update document lengths
    logger.info("Updating document lengths...")
    update_doc_lengths(doc_lengths)
    
    logger.info("Index rebuild complete!")
    
    # Print statistics
    num_docs = get_document_count()
    num_terms = len(inverted_index)
    avg_doc_len = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 0
    
    print("\n" + "="*60)
    print("INDEX STATISTICS")
    print("="*60)
    print(f"Total documents: {num_docs}")
    print(f"Total unique terms: {num_terms}")
    print(f"Average document length: {avg_doc_len:.1f} words")
    print("="*60 + "\n")


if __name__ == "__main__":
    rebuild_index()
