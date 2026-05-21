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
        :root {
            --color-dark: #0b0315;
            --color-green: #bdcd8a;
            --color-lavender: #d0c3e4;
            --color-purple: #8f77aa;
            --color-dark-purple: #2a0948;
            --color-text: #2d2d2d;
            --color-text-light: #666666;
            --color-border: #e8e6eb;
        }

        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }

        html { scroll-behavior: smooth; }

        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: linear-gradient(135deg, var(--color-dark) 0%, var(--color-dark-purple) 50%, #1a0630 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--color-text);
        }

        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
        }

        /* Background decorative elements */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(189, 205, 138, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(208, 195, 228, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .container { position: relative; z-index: 1; }

        /* Header Section */
        .header {
            text-align: center;
            margin-bottom: 50px;
            padding-top: 30px;
            animation: fadeInDown 0.8s ease-out;
        }

        .header h1 { 
            font-size: 3.5em; 
            font-weight: 700;
            margin-bottom: 12px;
            background: linear-gradient(135deg, var(--color-green) 0%, var(--color-lavender) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }

        .header .subtitle { 
            font-size: 1.2em; 
            color: var(--color-lavender);
            opacity: 0.9;
            font-weight: 300;
            letter-spacing: 0.5px;
        }

        /* Search Box Section */
        .search-form {
            margin-bottom: 50px;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }

        .search-box {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 6px 20px;
            box-shadow: 0 20px 60px rgba(11, 3, 21, 0.3), 0 0 1px rgba(189, 205, 138, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(189, 205, 138, 0.15);
            transition: all 0.3s ease;
        }

        .search-box:focus-within {
            box-shadow: 0 20px 60px rgba(11, 3, 21, 0.4), 0 0 20px rgba(189, 205, 138, 0.3);
            border-color: rgba(189, 205, 138, 0.4);
        }

        .search-icon {
            color: var(--color-purple);
            font-size: 20px;
        }

        .search-box input {
            border: none;
            outline: none;
            font-size: 18px;
            flex: 1;
            padding: 16px 0;
            background: transparent;
            color: var(--color-text);
            font-weight: 500;
        }

        .search-box input::placeholder {
            color: rgba(102, 102, 102, 0.5);
        }

        .search-box button {
            background: linear-gradient(135deg, var(--color-green) 0%, var(--color-purple) 100%);
            color: var(--color-dark);
            border: none;
            padding: 14px 36px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            box-shadow: 0 8px 20px rgba(189, 205, 138, 0.3);
        }

        .search-box button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(189, 205, 138, 0.4);
        }

        .search-box button:active {
            transform: translateY(-1px);
        }

        /* Results Section */
        .results-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(11, 3, 21, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid var(--color-border);
            animation: fadeIn 0.6s ease-out;
        }

        .results-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--color-border);
        }

        .result-count {
            font-size: 18px;
            font-weight: 600;
            color: var(--color-dark-purple);
        }

        .result-count-num {
            color: var(--color-green);
            font-weight: 700;
        }

        .result {
            padding: 24px 0;
            border-bottom: 1px solid var(--color-border);
            transition: all 0.3s ease;
            animation: slideInLeft 0.5s ease-out;
        }

        .result:hover {
            padding-left: 12px;
            padding-right: 12px;
            background: rgba(189, 205, 138, 0.04);
            border-radius: 8px;
        }

        .result:last-child { 
            border-bottom: none; 
        }

        .result-title {
            font-size: 1.4em;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .result-title a {
            color: var(--color-dark-purple);
            text-decoration: none;
            transition: all 0.2s ease;
            background: linear-gradient(120deg, var(--color-dark-purple) 0%, var(--color-purple) 100%);
            background-size: 0 100%;
            background-repeat: no-repeat;
            background-position: 0 100%;
            padding-bottom: 2px;
        }

        .result-title a:hover {
            background-size: 100% 100%;
            color: var(--color-green);
        }

        .result-url {
            color: var(--color-purple);
            font-size: 0.95em;
            margin-bottom: 12px;
            word-break: break-all;
            font-weight: 500;
            opacity: 0.8;
            transition: opacity 0.3s;
        }

        .result:hover .result-url {
            opacity: 1;
        }

        .result-snippet {
            color: var(--color-text-light);
            line-height: 1.7;
            margin-bottom: 12px;
            font-size: 0.95em;
        }

        .result-snippet mark {
            background: linear-gradient(120deg, rgba(189, 205, 138, 0.3) 0%, rgba(208, 195, 228, 0.2) 100%);
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
            color: var(--color-dark-purple);
        }

        .result-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.85em;
        }

        .score-badge {
            background: linear-gradient(135deg, rgba(189, 205, 138, 0.2) 0%, rgba(208, 195, 228, 0.1) 100%);
            color: var(--color-dark-purple);
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            border: 1px solid rgba(189, 205, 138, 0.3);
            transition: all 0.3s ease;
        }

        .result:hover .score-badge {
            background: linear-gradient(135deg, rgba(189, 205, 138, 0.4) 0%, rgba(208, 195, 228, 0.2) 100%);
            transform: scale(1.05);
        }

        /* Empty State */
        .no-results {
            text-align: center;
            padding: 80px 40px;
        }

        .no-results h2 {
            font-size: 2em;
            margin-bottom: 12px;
            color: var(--color-dark-purple);
            font-weight: 600;
        }

        .no-results p {
            color: var(--color-text-light);
            font-size: 1.1em;
        }

        /* Stats Footer */
        .stats {
            text-align: center;
            margin-top: 40px;
            padding: 24px;
            color: var(--color-lavender);
            font-size: 0.95em;
            font-weight: 500;
            animation: fadeIn 0.8s ease-out 0.4s both;
        }

        .stats-divider {
            color: var(--color-green);
            margin: 0 8px;
            font-weight: 700;
        }

        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5em;
            }

            .header .subtitle {
                font-size: 1em;
            }

            .search-box {
                flex-direction: column;
                align-items: stretch;
                gap: 0;
            }

            .search-icon {
                display: none;
            }

            .search-box input {
                padding: 14px 16px;
                text-align: center;
            }

            .search-box button {
                padding: 12px 20px;
                border-radius: 8px;
            }

            .results-container {
                padding: 24px;
            }

            .result-title {
                font-size: 1.2em;
            }

            .result-snippet {
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>∫ MathSearch</h1>
            <p class="subtitle">Discover Mathematical Knowledge</p>
        </div>
        
        <form method="GET" action="/search" class="search-form">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" name="q" value="{{ query }}" 
                       placeholder="Explore calculus, algebra, geometry..." autofocus>
                <button type="submit">Search</button>
            </div>
        </form>
        
        {% if results %}
        <div class="results-container">
            <div class="results-header">
                <span class="result-count">Found <span class="result-count-num">{{ results|length }}</span> result{{ "s" if results|length != 1 else "" }}</span>
            </div>
            
            {% for result in results %}
            <div class="result">
                <div class="result-title">
                    <a href="{{ result.url }}" target="_blank">{{ result.title }}</a>
                </div>
                <div class="result-url">{{ result.url }}</div>
                <div class="result-snippet">{{ result.snippet|safe }}</div>
                <div class="result-meta">
                    <span class="score-badge">Relevance: {{ "%.1f"|format(result.score * 100) }}%</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="results-container">
            <div class="no-results">
                <h2>No results found</h2>
                <p>Try searching with different keywords</p>
            </div>
        </div>
        {% endif %}
        
        <div class="stats">
            {{ stats.documents }} documents <span class="stats-divider">•</span> {{ stats.terms }} terms indexed
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
