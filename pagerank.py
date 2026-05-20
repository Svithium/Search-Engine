"""
PageRank computation module.
Updated to save PageRank scores to the new documents table.
"""

import numpy as np
import logging
from database import save_pagerank, get_all_documents
from crawler import load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_pagerank(link_graph, damping=0.85, max_iterations=100, tolerance=1e-6):
    """
    Compute PageRank scores for all pages in the link graph.
    
    PageRank formula:
    PR(A) = (1-d) + d * Σ(PR(Ti) / C(Ti))
    
    where:
    - d is the damping factor
    - Ti are pages that link to page A
    - C(Ti) is the number of outbound links from page Ti
    
    Args:
        link_graph: dict mapping page URL to list of linked URLs
        damping: Damping factor (typically 0.85)
        max_iterations: Maximum number of iterations
        tolerance: Convergence threshold
        
    Returns:
        dict: Mapping of page URL to PageRank score
    """
    logger.info("Computing PageRank...")
    
    pages = list(link_graph.keys())
    n = len(pages)
    
    if n == 0:
        logger.warning("Empty link graph")
        return {}
    
    page_index = {page: i for i, page in enumerate(pages)}
    
    # Build adjacency matrix
    adjacency = np.zeros((n, n))
    
    for page, links in link_graph.items():
        i = page_index[page]
        
        # Filter for valid links (links that exist in our page set)
        valid_links = [l for l in links if l in page_index]
        
        if valid_links:
            # Distribute PageRank equally among outbound links
            for link in valid_links:
                j = page_index[link]
                adjacency[j][i] = 1.0 / len(valid_links)
        else:
            # Dangling node: distribute to all pages
            adjacency[:, i] = 1.0 / n
    
    # PageRank transition matrix with damping
    pagerank_matrix = damping * adjacency + (1 - damping) / n * np.ones((n, n))
    
    # Initialize PageRank scores uniformly
    ranks = np.ones(n) / n
    
    # Power iteration
    for iteration in range(max_iterations):
        new_ranks = pagerank_matrix @ ranks
        
        # Check convergence
        diff = np.linalg.norm(new_ranks - ranks)
        if diff < tolerance:
            logger.info(f"PageRank converged after {iteration + 1} iterations")
            break
        
        ranks = new_ranks
    else:
        logger.warning(f"PageRank did not converge after {max_iterations} iterations")
    
    # Convert to dictionary
    pagerank_scores = {pages[i]: float(ranks[i]) for i in range(n)}
    
    return pagerank_scores


def compute_and_save_pagerank():
    """
    Complete PageRank computation pipeline:
    1. Load link graph
    2. Compute PageRank
    3. Save to database
    """
    logger.info("Starting PageRank computation pipeline...")
    
    # Load link graph from crawled data
    try:
        link_graph, _ = load_data()
    except FileNotFoundError:
        logger.error("Crawled data not found. Run crawler.py first!")
        return
    
    if not link_graph:
        logger.error("Empty link graph!")
        return
    
    # Compute PageRank
    ranks = compute_pagerank(link_graph)
    
    # Save to database
    logger.info("Saving PageRank scores to database...")
    save_pagerank(ranks)
    
    # Display top pages
    top_pages = sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:20]
    
    print("\n" + "=" * 80)
    print("TOP 20 PAGES BY PAGERANK")
    print("=" * 80)
    
    for i, (url, score) in enumerate(top_pages, 1):
        page_name = url.split('/wiki/')[-1].replace('_', ' ') if '/wiki/' in url else url
        print(f"{i:2d}. {score:.8f} - {page_name}")
    
    print("=" * 80)
    
    logger.info("PageRank computation complete!")


if __name__ == "__main__":
    compute_and_save_pagerank()
