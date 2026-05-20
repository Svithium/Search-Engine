"""
Flask web application for the search engine.
Displays search results with snippets and relevance scores.
"""

from flask import Flask, request, render_template_string
import logging
from search import search
from config import ENABLE_HYBRID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template with modern styling
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MathSearch - Advanced Search Engine</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding-top: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .header .features {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 10px;
        }
        
        .search-box {
            background: white;
            border-radius: 50px;
            padding: 8px 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .search-box input {
            border: none;
            outline: none;
            font-size: 18px;
            flex: 1;
            padding: 12px;
        }
        
        .search-box button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .search-box button:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .results-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .result-header {
            color: #70757a;
            margin-bottom: 20px;
            font-size: 0.95em;
        }
        
        .result {
            border-bottom: 1px solid #eee;
            padding: 20px 0;
            transition: all 0.3s;
        }
        
        .result:last-child {
            border-bottom: none;
        }
        
        .result:hover {
            background: #f8f9ff;
            padding-left: 15px;
            margin-left: -15px;
            margin-right: -15px;
            padding-right: 15px;
            border-radius: 8px;
        }
        
        .result-title {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        
        .result-title a {
            color: #1a0dab;
            text-decoration: none;
            font-weight: 500;
        }
        
        .result-title a:hover {
            text-decoration: underline;
        }
        
        .result-url {
            color: #006621;
            font-size: 0.9em;
            margin-bottom: 8px;
            word-break: break-all;
        }
        
        .result-snippet {
            color: #545454;
            line-height: 1.6;
            margin-bottom: 8px;
        }
        
        .result-snippet mark {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .result-meta {
            display: flex;
            gap: 15px;
            font-size: 0.85em;
            color: #888;
        }
        
        .result-meta span {
            display: inline-block;
        }
        
        .score-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 500;
        }
        
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }
        
        .no-results h2 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: #666;
        }
        
        .mode-indicator {
            background: {% if hybrid_mode %}#e3f2fd{% else %}#fff3e0{% endif %};
            color: {% if hybrid_mode %}#1565c0{% else %}#e65100{% endif %};
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .search-box {
                flex-direction: column;
                border-radius: 15px;
                padding: 15px;
            }
            
            .search-box input {
                margin-bottom: 10px;
            }
            
            .search-box button {
                width: 100%;
            }
            
            .result-meta {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔢 MathSearch</h1>
            <p class="subtitle">Advanced Mathematical Search Engine</p>
            <p class="features">BM25 Ranking • Query Expansion • {% if hybrid_mode %}Semantic Re-ranking{% else %}PageRank{% endif %}</p>
        </div>
        
        <form method="GET" action="/search">
            <div class="search-box">
                <input type="text" 
                       name="q" 
                       value="{{ query }}" 
                       placeholder="Search mathematics topics..."
                       autofocus>
                <button type="submit">Search</button>
            </div>
        </form>
        
        {% if results %}
        <div class="results-container">
            <div class="mode-indicator">
                {% if hybrid_mode %}
                    🤖 Hybrid Search Mode: Using BM25 + Semantic Re-ranking + PageRank
                {% else %}
                    📊 BM25 Mode: Using BM25 + PageRank
                {% endif %}
            </div>
            
            <div class="result-header">
                Found {{ results|length }} results for "<strong>{{ query }}</strong>"
            </div>
            
            {% for result in results %}
            <div class="result">
                <div class="result-title">
                    <a href="{{ result.url }}" target="_blank">{{ result.title }}</a>
                </div>
                <div class="result-url">{{ result.url }}</div>
                <div class="result-snippet">{{ result.snippet|safe }}</div>
                <div class="result-meta">
                    <span class="score-badge">Score: {{ "%.4f"|format(result.score) }}</span>
                    <span>BM25: {{ "%.4f"|format(result.bm25_score) }}</span>
                    <span>PageRank: {{ "%.6f"|format(result.pagerank) }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="results-container">
            <div class="no-results">
                <h2>No results found</h2>
                <p>Try different keywords or check your spelling</p>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''


@app.route('/')
def home():
    """Home page with search box."""
    return render_template_string(HTML, query='', results=[], hybrid_mode=ENABLE_HYBRID)


@app.route('/search')
def search_page():
    """Search results page."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template_string(HTML, query='', results=[], hybrid_mode=ENABLE_HYBRID)
    
    try:
        # Perform search
        results = search(query, top_k=20)
        
        logger.info(f"Query: '{query}' - Found {len(results)} results")
        
        return render_template_string(
            HTML, 
            query=query, 
            results=results,
            hybrid_mode=ENABLE_HYBRID
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return render_template_string(
            HTML, 
            query=query, 
            results=[],
            hybrid_mode=ENABLE_HYBRID,
            error=str(e)
        )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MathSearch - Starting Flask Application")
    print("="*60)
    print(f"Hybrid Mode: {'ENABLED' if ENABLE_HYBRID else 'DISABLED'}")
    print("Open your browser to: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
