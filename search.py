"""
Search engine with BM25 ranking and optional hybrid semantic re-ranking.
Two-stage retrieval:
  Stage 1: BM25 retrieves top-K candidates
  Stage 2: Sentence transformer re-ranks candidates
"""

import math
import logging
import numpy as np
from database import (
    get_inverted_index, get_all_documents, 
    get_avg_doc_length, get_document_count, get_document_by_id
)
from query_expansion import expand_query
from snippets import extract_snippet
from config import (
    BM25_K1, BM25_B, ENABLE_HYBRID, HYBRID_LAMBDA, 
    TOP_K_CANDIDATES, DEFAULT_TOP_K, SENTENCE_TRANSFORMER_MODEL
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy load sentence transformer
_sentence_model = None


def get_sentence_model():
    """Load sentence transformer model (cached)."""
    global _sentence_model
    if _sentence_model is None and ENABLE_HYBRID:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading sentence transformer: {SENTENCE_TRANSFORMER_MODEL}")
            _sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
            logger.info("Sentence transformer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            logger.warning("Falling back to BM25-only search")
    return _sentence_model


def compute_bm25_score(doc_id, query_terms, inverted_index, doc_lengths, 
                       avg_doc_length, total_docs, k1=BM25_K1, b=BM25_B):
    """
    Compute BM25 score for a document given query terms.
    
    BM25 formula:
    score = Σ IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))
    
    Args:
        doc_id: Document ID
        query_terms: Set of query terms
        inverted_index: Inverted index {word: [(doc_id, tf), ...]}
        doc_lengths: Dict of document lengths
        avg_doc_length: Average document length
        total_docs: Total number of documents
        k1: BM25 k1 parameter (term frequency saturation)
        b: BM25 b parameter (length normalization)
        
    Returns:
        BM25 score (float)
    """
    score = 0.0
    doc_length = doc_lengths.get(doc_id, avg_doc_length)
    
    for term in query_terms:
        if term not in inverted_index:
            continue
        
        # Get term frequency in this document
        tf = 0
        for d_id, freq in inverted_index[term]:
            if d_id == doc_id:
                tf = freq
                break
        
        if tf == 0:
            continue
        
        # Calculate IDF: log((N - df + 0.5) / (df + 0.5) + 1)
        df = len(inverted_index[term])  # Document frequency
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        
        # BM25 term score
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
        
        score += idf * (numerator / denominator)
    
    return score


def bm25_search(query_terms, inverted_index, doc_lengths, pagerank_scores,
                avg_doc_length, total_docs, top_k=TOP_K_CANDIDATES):
    """
    Stage 1: BM25 retrieval to get candidate documents.
    
    Args:
        query_terms: Set of query terms
        inverted_index: Inverted index
        doc_lengths: Document lengths
        pagerank_scores: PageRank scores
        avg_doc_length: Average document length
        total_docs: Total number of documents
        top_k: Number of candidates to retrieve
        
    Returns:
        List of (doc_id, bm25_score, pagerank) tuples
    """
    # Find candidate documents (documents containing at least one query term)
    candidates = set()
    for term in query_terms:
        if term in inverted_index:
            for doc_id, _ in inverted_index[term]:
                candidates.add(doc_id)
    
    if not candidates:
        return []
    
    # Score each candidate with BM25
    scored_docs = []
    for doc_id in candidates:
        bm25_score = compute_bm25_score(
            doc_id, query_terms, inverted_index, doc_lengths,
            avg_doc_length, total_docs
        )
        
        # Get PageRank score
        pr_score = pagerank_scores.get(doc_id, 0.0)
        
        scored_docs.append((doc_id, bm25_score, pr_score))
    
    # Sort by BM25 score and return top-K
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    return scored_docs[:top_k]


def hybrid_rerank(query, candidates, doc_contents, lam=HYBRID_LAMBDA):
    """
    Stage 2: Re-rank candidates using sentence transformer embeddings.
    
    Final score = BM25 score + λ * cosine_similarity
    
    Args:
        query: Original query string
        candidates: List of (doc_id, bm25_score, pagerank) tuples
        doc_contents: Dict mapping doc_id to content text
        lam: Lambda weight for cosine similarity
        
    Returns:
        List of (doc_id, final_score, bm25_score, pagerank) tuples
    """
    model = get_sentence_model()
    
    if model is None:
        # Fallback: return BM25 scores only
        logger.warning("Sentence model not available, using BM25 only")
        return [(doc_id, bm25 * (1 + pr), bm25, pr) 
                for doc_id, bm25, pr in candidates]
    
    try:
        # Encode query
        query_embedding = model.encode([query])[0]
        
        # Encode candidate documents
        doc_ids = [doc_id for doc_id, _, _ in candidates]
        doc_texts = [doc_contents.get(doc_id, "") for doc_id in doc_ids]
        
        # Limit document text length for embedding
        doc_texts = [text[:1000] for text in doc_texts]
        
        doc_embeddings = model.encode(doc_texts)
        
        # Compute cosine similarities
        from numpy.linalg import norm
        
        reranked = []
        for i, (doc_id, bm25_score, pr_score) in enumerate(candidates):
            # Cosine similarity
            cos_sim = np.dot(query_embedding, doc_embeddings[i]) / (
                norm(query_embedding) * norm(doc_embeddings[i]) + 1e-10
            )
            
            # Combine scores: BM25 + λ * cosine_similarity, then multiply by PageRank
            hybrid_score = (bm25_score + lam * cos_sim) * (1 + pr_score)
            
            reranked.append((doc_id, hybrid_score, bm25_score, pr_score))
        
        # Sort by hybrid score
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        return reranked
        
    except Exception as e:
        logger.error(f"Hybrid re-ranking failed: {e}")
        # Fallback to BM25 * PageRank
        return [(doc_id, bm25 * (1 + pr), bm25, pr) 
                for doc_id, bm25, pr in candidates]


def search(query, top_k=DEFAULT_TOP_K):
    """
    Main search function with query expansion and hybrid retrieval.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        List of result dictionaries with url, title, snippet, score
    """
    logger.info(f"Search query: '{query}'")
    
    # Load index and documents
    inverted_index = get_inverted_index()
    all_docs = get_all_documents()
    
    # Build lookup structures
    doc_lengths = {doc[0]: doc[4] for doc in all_docs}
    pagerank_scores = {doc[0]: doc[5] for doc in all_docs}
    doc_contents = {doc[0]: doc[3] for doc in all_docs}
    url_mapping = {doc[0]: (doc[1], doc[2]) for doc in all_docs}  # doc_id -> (url, title)
    
    avg_doc_length = get_avg_doc_length()
    total_docs = get_document_count()
    
    # Query expansion
    expanded_terms = expand_query(query)
    logger.info(f"Expanded terms: {expanded_terms}")
    
    # Stage 1: BM25 retrieval
    candidates = bm25_search(
        expanded_terms, inverted_index, doc_lengths, pagerank_scores,
        avg_doc_length, total_docs, top_k=TOP_K_CANDIDATES
    )
    
    if not candidates:
        logger.info("No results found")
        return []
    
    logger.info(f"Stage 1: Retrieved {len(candidates)} candidates")
    
    # Stage 2: Hybrid re-ranking (if enabled)
    if ENABLE_HYBRID:
        logger.info("Stage 2: Hybrid re-ranking...")
        results = hybrid_rerank(query, candidates, doc_contents)
    else:
        # Just use BM25 * PageRank
        results = [(doc_id, bm25 * (1 + pr), bm25, pr) 
                   for doc_id, bm25, pr in candidates]
        results.sort(key=lambda x: x[1], reverse=True)
    
    # Format results
    formatted_results = []
    for doc_id, final_score, bm25_score, pr_score in results[:top_k]:
        url, title = url_mapping.get(doc_id, ("", "Unknown"))
        content = doc_contents.get(doc_id, "")
        
        # Extract snippet
        snippet = extract_snippet(content, expanded_terms)
        
        formatted_results.append({
            'url': url,
            'title': title,
            'snippet': snippet,
            'score': final_score,
            'bm25_score': bm25_score,
            'pagerank': pr_score
        })
    
    logger.info(f"Returning {len(formatted_results)} results")
    return formatted_results


if __name__ == "__main__":
    # Interactive search
    print("Search Engine (type 'quit' to exit)")
    print("=" * 60)
    
    while True:
        query = input("\nSearch: ").strip()
        
        if query.lower() == 'quit':
            break
        
        if not query:
            continue
        
        results = search(query, top_k=10)
        
        if results:
            print(f"\nFound {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Score: {result['score']:.4f} "
                      f"(BM25: {result['bm25_score']:.4f}, "
                      f"PageRank: {result['pagerank']:.6f})")
                print(f"   {result['snippet']}")
                print()
        else:
            print("No results found.")
