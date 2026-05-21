#!/usr/bin/env python
"""
MathSearch - Simple Entry Point
Run with: python main.py
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, render_template_string

# Import search engine
from search_engine import (
    init_db, crawl, save_to_db, search, get_stats, DB_PATH
)

# ============================================================================
# WEB APPLICATION
# ============================================================================

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MathSearch</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding-top: 40px;
        }
        .header h1 { font-size: 3em; margin-bottom: 10px; font-weight: 300; }
        .header .subtitle { font-size: 1.1em; opacity: 0.9; }
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
        }
        .search-box button:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        .results-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .result {
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }
        .result:last-child { border-bottom: none; }
        .result-title {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        .result-title a {
            color: #1a0dab;
            text-decoration: none;
        }
        .result-title a:hover { text-decoration: underline; }
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
            font-size: 0.85em;
            color: #888;
        }
        .score-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 12px;
        }
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }
        .stats {
            text-align: center;
            color: white;
            margin-top: 20px;
            opacity: 0.8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔢 MathSearch</h1>
            <p class="subtitle">Mathematical Search Engine</p>
        </div>
        
        <form method="GET" action="/search">
            <div class="search-box">
                <input type="text" name="q" value="{{ query }}" 
                       placeholder="Search mathematics..." autofocus>
                <button type="submit">Search</button>
            </div>
        </form>
        
        {% if results %}
        <div class="results-container">
            <div style="color: #70757a; margin-bottom: 20px;">
                Found {{ results|length }} results
            </div>
            
            {% for result in results %}
            <div class="result">
                <div class="result-title">
                    <a href="{{ result.url }}" target="_blank">{{ result.title }}</a>
                </div>
                <div class="result-url">{{ result.url }}</div>
                <div class="result-snippet">{{ result.snippet|safe }}</div>
                <div class="result-meta">
                    <span class="score-badge">Score: {{ "%.3f"|format(result.score) }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="results-container">
            <div class="no-results">
                <h2>No results found</h2>
                <p>Try different keywords</p>
            </div>
        </div>
        {% endif %}
        
        <div class="stats">
            {{ stats.documents }} documents • {{ stats.terms }} terms indexed
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    stats = get_stats()
    return render_template_string(HTML, query='', results=[], stats=stats)

@app.route('/search')
def search_page():
    query = request.args.get('q', '').strip()
    stats = get_stats()
    
    if not query:
        return render_template_string(HTML, query='', results=[], stats=stats)
    
    try:
        results = search(query, top_k=20)
        return render_template_string(HTML, query=query, results=results, stats=stats)
    except Exception as e:
        print(f"Search error: {e}")
        return render_template_string(HTML, query=query, results=[], stats=stats)


# ============================================================================
# INITIALIZATION
# ============================================================================

def setup_database():
    """Setup database with sample data."""
    print("\n" + "="*60)
    print("MathSearch Setup")
    print("="*60)
    
    if Path(DB_PATH).exists():
        response = input("\nDatabase exists. Re-initialize? (y/N): ")
        if response.lower() != 'y':
            print("Using existing database.")
            return
        os.remove(DB_PATH)
    
    print("\nInitializing database...")
    init_db()
    
    print("\nCrawling Wikipedia...")
    print("This will take a few minutes...")
    
    seed = "https://en.wikipedia.org/wiki/Mathematics"
    link_graph, page_content = crawl(seed, max_pages=100)
    
    print("\nBuilding search index...")
    save_to_db(page_content, link_graph)
    
    stats = get_stats()
    print("\n" + "="*60)
    print("Setup Complete!")
    print(f"Documents: {stats['documents']}")
    print(f"Terms: {stats['terms']}")
    print("="*60)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    
    # Check if database exists
    if not Path(DB_PATH).exists():
        print("\n⚠️  Database not found!")
        print("\nFirst-time setup required.")
        response = input("Initialize database now? (Y/n): ")
        if response.lower() != 'n':
            setup_database()
        else:
            print("\nRun 'python main.py setup' to initialize later.")
            return
    
    # Check for commands
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            setup_database()
        
        elif command == 'search':
            if len(sys.argv) < 3:
                print("Usage: python main.py search <query>")
                return
            
            query = ' '.join(sys.argv[2:])
            print(f"\nSearching for: {query}")
            results = search(query)
            
            if results:
                print(f"\nFound {len(results)} results:\n")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['title']}")
                    print(f"   Score: {r['score']:.3f}")
                    print(f"   {r['url']}\n")
            else:
                print("No results found.")
        
        elif command == 'stats':
            stats = get_stats()
            print("\nDatabase Statistics:")
            print(f"Documents: {stats['documents']}")
            print(f"Terms: {stats['terms']}")
        
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  python main.py          - Start web server")
            print("  python main.py setup    - Initialize database")
            print("  python main.py search <query>  - Search from CLI")
            print("  python main.py stats    - Show statistics")
        
        return
    
    # Start web server
    print("\n" + "="*60)
    print("MathSearch - Starting Web Server")
    print("="*60)
    
    stats = get_stats()
    print(f"Documents indexed: {stats['documents']}")
    print(f"Terms indexed: {stats['terms']}")
    print("\nOpen your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
