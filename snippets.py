"""
Intelligent snippet extraction that finds the most relevant context for query terms.
"""

import re
import logging
from config import SNIPPET_LENGTH, SNIPPET_CONTEXT_SENTENCES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text):
    """
    Clean text by removing excessive whitespace and newlines.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_into_sentences(text):
    """
    Split text into sentences using simple heuristics.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitter (can be improved with NLTK)
    sentences = re.split(r'[.!?]+\s+', text)
    # Filter out very short "sentences"
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences


def score_sentence(sentence, query_terms):
    """
    Score a sentence based on query term presence and proximity.
    
    Args:
        sentence: Sentence text
        query_terms: Set of query terms
        
    Returns:
        Score (higher is better)
    """
    sentence_lower = sentence.lower()
    score = 0
    
    # Count matching terms
    matches = sum(1 for term in query_terms if term in sentence_lower)
    score += matches * 10
    
    # Bonus for multiple matches close together
    if matches > 1:
        score += 5
    
    # Penalty for very long sentences
    if len(sentence) > 300:
        score -= 2
    
    return score


def extract_snippet(content, query_terms, max_length=SNIPPET_LENGTH):
    """
    Extract the most relevant snippet from content based on query terms.
    Finds sentences containing query terms and returns context around them.
    
    Args:
        content: Full document content
        query_terms: Set of query terms to search for
        max_length: Maximum snippet length in characters
        
    Returns:
        Snippet string with ellipses if truncated
    """
    if not content:
        return "No preview available."
    
    # Clean the content
    content = clean_text(content)
    
    if not content:
        return "No preview available."
    
    # Split into sentences
    sentences = split_into_sentences(content)
    
    if not sentences:
        # Fallback: return beginning of content
        snippet = content[:max_length]
        return snippet + "..." if len(content) > max_length else snippet
    
    # Score each sentence
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = score_sentence(sentence, query_terms)
        if score > 0:
            sentence_scores.append((score, i, sentence))
    
    # If no sentences match, return first sentence
    if not sentence_scores:
        snippet = sentences[0][:max_length]
        return snippet + "..." if len(sentences[0]) > max_length else snippet
    
    # Sort by score and get best sentence
    sentence_scores.sort(reverse=True)
    best_score, best_idx, best_sentence = sentence_scores[0]
    
    # Get context: include neighboring sentences
    start_idx = max(0, best_idx - SNIPPET_CONTEXT_SENTENCES // 2)
    end_idx = min(len(sentences), best_idx + SNIPPET_CONTEXT_SENTENCES // 2 + 1)
    
    # Combine context sentences
    context_sentences = sentences[start_idx:end_idx]
    snippet = ' '.join(context_sentences)
    
    # Truncate if too long
    if len(snippet) > max_length * 2:
        # Center around the best sentence
        best_pos = snippet.lower().find(best_sentence.lower())
        if best_pos != -1:
            start = max(0, best_pos - max_length // 2)
            end = min(len(snippet), best_pos + max_length // 2)
            snippet = snippet[start:end]
            
            # Add ellipses
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(snippet) else ""
            snippet = prefix + snippet.strip() + suffix
        else:
            # Fallback: truncate from start
            snippet = snippet[:max_length * 2] + "..."
    elif len(snippet) > max_length:
        # Add ellipses at boundaries if we included context
        prefix = "..." if start_idx > 0 else ""
        suffix = "..." if end_idx < len(sentences) else ""
        snippet = prefix + snippet.strip() + suffix
    
    return snippet


def extract_snippet_simple(content, query_terms, max_length=SNIPPET_LENGTH):
    """
    Simple snippet extraction: find first occurrence of any query term.
    Fallback method when sentence-based extraction is too slow.
    
    Args:
        content: Full document content
        query_terms: Set of query terms
        max_length: Maximum snippet length
        
    Returns:
        Snippet string
    """
    content = clean_text(content)
    
    if not content:
        return "No preview available."
    
    content_lower = content.lower()
    
    # Find first occurrence of any query term
    best_pos = len(content)
    for term in query_terms:
        pos = content_lower.find(term)
        if pos != -1 and pos < best_pos:
            best_pos = pos
    
    # If no match found, return beginning
    if best_pos == len(content):
        snippet = content[:max_length]
        return snippet + "..." if len(content) > max_length else snippet
    
    # Extract snippet centered on the match
    start = max(0, best_pos - max_length // 3)
    end = min(len(content), start + max_length)
    
    snippet = content[start:end].strip()
    
    # Add ellipses
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""
    
    return prefix + snippet + suffix


def highlight_terms(snippet, query_terms):
    """
    Highlight query terms in snippet (for HTML display).
    
    Args:
        snippet: Snippet text
        query_terms: Set of query terms to highlight
        
    Returns:
        Snippet with HTML <mark> tags around query terms
    """
    highlighted = snippet
    
    for term in query_terms:
        # Case-insensitive replacement with HTML mark tag
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f'<mark>{m.group(0)}</mark>', highlighted)
    
    return highlighted


if __name__ == "__main__":
    # Test snippet extraction
    sample_text = """
    Calculus is the mathematical study of continuous change. It has two major branches: 
    differential calculus and integral calculus. Differential calculus concerns instantaneous 
    rates of change and slopes of curves. Integral calculus concerns accumulation of quantities 
    and areas under curves. These two branches are related to each other by the fundamental 
    theorem of calculus. Both branches make use of the fundamental notions of convergence of 
    infinite sequences and infinite series to a well-defined limit.
    """
    
    query_terms = {"calculus", "differential", "integral"}
    
    snippet = extract_snippet(sample_text, query_terms)
    print("Extracted snippet:")
    print(snippet)
    
    print("\n\nHighlighted snippet:")
    highlighted = highlight_terms(snippet, query_terms)
    print(highlighted)
