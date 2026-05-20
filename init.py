#!/usr/bin/env python
"""
Initialization script for MathSearch.
This script sets up the database and builds the search index.

Usage:
    python init.py              # Build index with default settings
    python init.py --max-pages 1000  # Customize max pages to crawl
"""

import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Initialize MathSearch database and build index"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Maximum number of pages to crawl (default: 500)"
    )
    parser.add_argument(
        "--seed-url",
        default="https://en.wikipedia.org/wiki/Mathematics",
        help="Starting URL for crawl (default: Wikipedia Mathematics page)"
    )
    parser.add_argument(
        "--no-crawl",
        action="store_true",
        help="Skip crawling and only rebuild from existing data"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("=" * 60)
        logger.info("MathSearch Initialization")
        logger.info("=" * 60)
        
        if not args.no_crawl:
            logger.info(f"\nStep 1: Crawling from {args.seed_url}")
            logger.info(f"Max pages to crawl: {args.max_pages}")
            
            from crawler import crawl
            from indexer import build_index
            from database import init_db, save_pages, save_index, save_pagerank
            from pagerank import compute_pagerank
            
            # Initialize database
            logger.info("\nInitializing database...")
            init_db()
            
            # Crawl pages
            logger.info(f"\nCrawling pages (max: {args.max_pages})...")
            link_graph, page_content = crawl(args.seed_url, max_pages=args.max_pages)
            logger.info(f"Crawled {len(page_content)} pages")
            
            # Save pages to database
            logger.info("\nSaving pages to database...")
            save_pages([(url, page_content[url]) for url in page_content])
            
            # Build and save index
            logger.info("\nBuilding inverted index...")
            inverted_index, doc_lengths = build_index(page_content)
            save_index(inverted_index, doc_lengths)
            
            # Compute and save PageRank
            logger.info("\nComputing PageRank scores...")
            pagerank_scores = compute_pagerank(link_graph)
            save_pagerank(pagerank_scores)
            
        else:
            logger.info("Skipping crawl (--no-crawl flag set)")
            logger.info("Using existing data from database")
        
        logger.info("\n" + "=" * 60)
        logger.info("Initialization complete!")
        logger.info("=" * 60)
        logger.info("\nTo start the web application:")
        logger.info("  python app.py")
        logger.info("\nTo perform a search programmatically:")
        logger.info("  from search import search")
        logger.info("  results = search('your query')")
        
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed:")
        logger.error("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
