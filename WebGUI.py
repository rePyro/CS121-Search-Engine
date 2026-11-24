from flask import Flask, jsonify, render_template_string, request
import asyncio
import time
import index_API
import search
import AI

app = Flask(__name__)

# Number of results shown for the query
DEFAULT_K = 10

# Uses Jinja
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
        <div class="summary" data-url="{{ r.url }}">Generating summary... Please be patient; this usually takes ~20 seconds.</div>
      </div>
    {% else %}
      <p>No pages contain all of those words.</p>
    {% endfor %}
  {% endif %}

  <script>
    window.onload = () => {
      const summary_elements = document.querySelectorAll('.summary');
      if (summary_elements.length === 0) return;
      fetch("/summaries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          results_urls: Array.from(summary_elements, e => e.dataset.url)
        })
      })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(summaries => {
        for (let i = 0; i < summaries.length; i++) {
          const summary = summaries[i];
          summary_elements[i].textContent = summaries[i];
        }
      })
      .catch(err => {
        console.error(err);
        summary_elements.forEach(ele => { ele.textContent = "Could not load AI summary." });
      });
    };
  </script>
</body>
</html>
"""


@app.route("/")
def home():
    """Show the search box and the results if a search query was given"""
    query = request.args.get("q", "").strip()
    elapsed_ms = 0.0
    results=[]

    if query:
        start = time.perf_counter()
        results = search.search(query, k=DEFAULT_K)
        elapsed_ms = (time.perf_counter() - start) * 1000

    return render_template_string(PAGE, query=query, results=results, elapsed_ms=elapsed_ms)


@app.post("/summaries")
def get_summaries():
    """Generate and return summaries for each of the results. To be called client-side to improve loading speed"""
    # The URLs to generate summaries for should be passed in
    # These are the URLs of the results returned by the search
    data = request.get_json()
    urls = data["results_urls"]
    if not urls:
        return jsonify({"Error": "Missing 'results_urls' from request body"}), 400

    summaries = asyncio.run(AI.get_AI_summaries(page_urls=[url for url in urls]))
    return jsonify(summaries)


if __name__ == "__main__":
    print("Loading index...")
    index_API.load_index()
    # use_reloader=False because the reloader would make a second process
    # that would load the index twice
    app.run(debug=True, use_reloader=False)
