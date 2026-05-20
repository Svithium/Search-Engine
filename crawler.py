"""
Web crawler for Wikipedia math pages.
Updated to work with the new normalized database schema.
"""

import requests
from bs4 import BeautifulSoup
from collections import deque
import urllib.parse
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl(seed_url, max_pages=500):
    """
    Crawl Wikipedia pages starting from seed URL.
    
    Args:
        seed_url: Starting URL for crawl
        max_pages: Maximum number of pages to crawl
        
    Returns:
        tuple: (link_graph, page_content)
            - link_graph: dict mapping URL to list of linked URLs
            - page_content: dict mapping URL to page text content
    """
    visited = set()
    queue = deque([seed_url])
    link_graph = {}  # page -> list of pages it links to
    page_content = {}  # page -> raw text

    logger.info(f"Starting crawl from {seed_url}, max_pages={max_pages}")

    while queue and len(visited) < max_pages:
        url = queue.popleft()

        if url in visited:
            continue

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text content
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            page_content[url] = soup.get_text(separator=' ', strip=True)

            # Extract links
            links = []
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                # Convert relative URLs to absolute
                full_url = urllib.parse.urljoin(url, href)
                
                # Filter for relevant Wikipedia pages
                if _is_valid_wikipedia_url(full_url):
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

    logger.info(f"Crawl complete. Total pages: {len(page_content)}")
    return link_graph, page_content


def _is_valid_wikipedia_url(url):
    """
    Check if URL is a valid Wikipedia page to crawl.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL should be crawled
    """
    # Must be Wikipedia
    if 'en.wikipedia.org/wiki' not in url:
        return False
    
    # Exclude special pages
    exclude_patterns = [
        'Wikipedia:', 'Help:', 'Portal:', 'Special:', 'Talk:',
        'File:', 'Category:', 'Template:', 'Wayback', 'Main_Page',
        'Wikisource', 'identifier)', '#'
    ]
    
    for pattern in exclude_patterns:
        if pattern in url:
            return False
    
    return True


def save_data(link_graph, page_content, 
              graph_file='link_graph.json', 
              content_file='page_content.json'):
    """
    Save crawled data to JSON files.
    
    Args:
        link_graph: Link graph dict
        page_content: Page content dict
        graph_file: Output file for link graph
        content_file: Output file for page content
    """
    try:
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(link_graph, f, indent=2, ensure_ascii=False)
        
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(page_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {graph_file} and {content_file}")
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise


def load_data(graph_file='link_graph.json', content_file='page_content.json'):
    """
    Load previously crawled data from JSON files.
    
    Args:
        graph_file: Input file for link graph
        content_file: Input file for page content
        
    Returns:
        tuple: (link_graph, page_content)
    """
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            link_graph = json.load(f)
        
        with open(content_file, 'r', encoding='utf-8') as f:
            page_content = json.load(f)
        
        logger.info(f"Loaded {len(page_content)} pages from disk")
        return link_graph, page_content
        
    except FileNotFoundError as e:
        logger.error(f"Data files not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


if __name__ == "__main__":
    # Crawl Wikipedia math pages
    seed = "https://en.wikipedia.org/wiki/Mathematics"
    
    print("=" * 60)
    print("Wikipedia Math Crawler")
    print("=" * 60)
    print(f"Seed URL: {seed}")
    print(f"Max pages: 3000")
    print("=" * 60)
    
    link_graph, page_content = crawl(seed, max_pages=3000)
    
    print("\n" + "=" * 60)
    print(f"Crawl complete!")
    print(f"Total pages crawled: {len(page_content)}")
    print(f"Total links discovered: {sum(len(links) for links in link_graph.values())}")
    print("=" * 60)
    
    save_data(link_graph, page_content)
    print("\nData saved successfully!")
