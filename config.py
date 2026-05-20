"""
Configuration file for the search engine.
All tunable parameters are centralized here.
"""

# BM25 Parameters
BM25_K1 = 1.5  # Term frequency saturation parameter (typical range: 1.2-2.0)
BM25_B = 0.75  # Length normalization parameter (typical: 0.75)

# Hybrid Search Parameters
ENABLE_HYBRID = True  # Enable/disable semantic re-ranking
HYBRID_LAMBDA = 0.5  # Weight for cosine similarity in hybrid scoring
TOP_K_CANDIDATES = 100  # Number of candidates from BM25 stage for re-ranking
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model

# Query Expansion Parameters
ENABLE_SPELL_CORRECTION = True
ENABLE_SYNONYM_EXPANSION = True
ENABLE_LLM_EXPANSION = False  # Set to True when LLM is configured

# Snippet Parameters
SNIPPET_LENGTH = 150  # Characters around the best match
SNIPPET_CONTEXT_SENTENCES = 2  # Number of sentences to include in snippet

# Search Parameters
DEFAULT_TOP_K = 10  # Default number of results to return

# Database
DATABASE_PATH = "search_engine.db"

# Math Synonyms Dictionary
MATH_SYNONYMS = {
    "calc": ["calculus"],
    "calculus": ["calc", "integration", "differentiation"],
    "diff eq": ["differential equation", "ode"],
    "differential equation": ["diff eq", "ode", "pde"],
    "ode": ["ordinary differential equation", "diff eq"],
    "pde": ["partial differential equation"],
    "integral": ["integration", "antiderivative"],
    "integration": ["integral", "antiderivative"],
    "derivative": ["differentiation", "diff"],
    "differentiation": ["derivative"],
    "matrix": ["matrices", "linear algebra"],
    "matrices": ["matrix", "linear algebra"],
    "vector": ["vectors", "linear algebra"],
    "trig": ["trigonometry"],
    "trigonometry": ["trig", "sine", "cosine"],
    "alg": ["algebra"],
    "algebra": ["alg"],
    "geom": ["geometry"],
    "geometry": ["geom"],
    "prob": ["probability"],
    "probability": ["prob", "statistics"],
    "stats": ["statistics", "probability"],
    "statistics": ["stats", "probability"],
    "topology": ["topological"],
    "graph": ["graph theory", "network"],
    "number theory": ["arithmetic", "primes"],
    "complex": ["complex numbers", "imaginary"],
    "real": ["real numbers"],
    "function": ["mapping", "map"],
    "theorem": ["lemma", "proposition"],
    "proof": ["demonstration"],
    "set": ["set theory"],
    "logic": ["mathematical logic"],
    "analysis": ["real analysis", "mathematical analysis"],
}

# Logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
