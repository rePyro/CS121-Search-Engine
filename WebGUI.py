from flask import Flask, render_template_string, request
import time
import index_API
import search

app = Flask(__name__)

# Number of results shown for the query
DEFAULT_K = 10

# Jinja page
PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ query + ' - ' if query else '' }}Index Search</title>
  <style>
    body   { font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; color: #222; }
    h1     { margin-bottom: 16px; }
    form   { display: flex; gap: 8px; }
    input  { flex: 1; padding: 10px 14px; font-size: 16px; border: 1px solid #bbb; border-radius: 24px; }
    button { padding: 10px 20px; font-size: 16px; border: none; border-radius: 24px; background: #1a5fb4; color: #fff; cursor: pointer; }
    .stats { color: #666; font-size: 14px; margin: 16px 0; }
    .result { margin-bottom: 18px; }
    .result a { font-size: 17px; color: #1a0dab; text-decoration: none; word-break: break-all; }
    .result a:hover { text-decoration: underline; }
    .score { color: #666; font-size: 13px; }
  </style>
</head>
<body>
  <h1>ICS Search</h1>
  <form action="/" method="get">
    <input name="q" value="{{ query }}" placeholder="Search..." autofocus>
    <button type="submit">Search</button>
  </form>

  {% if query %}
    <p class="stats">{{ results|length }} result{{ '' if results|length == 1 else 's' }} in {{ '%.1f'|format(elapsed_ms) }} ms</p>
    {% for r in results %}
      <div class="result">
        <a href="{{ r.url }}" target="_blank" rel="noopener">{{ r.url }}</a>
        <div class="score">score {{ '%.3f'|format(r.score) }}</div>
      </div>
    {% else %}
      <p>No pages contain all of those words.</p>
    {% endfor %}
  {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    """Show the search box and the results if a search query was given"""
    query = request.args.get("q", "").strip()
    results = []
    elapsed_ms = 0.0

    if query:
        start = time.perf_counter()
        results = search.search(query, k=DEFAULT_K)
        elapsed_ms = (time.perf_counter() - start) * 1000

    return render_template_string(PAGE, query=query, results=results, elapsed_ms=elapsed_ms)


if __name__ == "__main__":
    print("Loading index...")
    index_API.load_index()
    # use_reloader=False because the reloader would make a second process
    # that would load the index twice
    app.run(debug=True, use_reloader=False)
