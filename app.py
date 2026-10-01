"""OpenSource Buddy - Flask app. Run with: python app.py"""
import re

from flask import Flask, jsonify, render_template, request

import analyzer

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # reject oversized requests

GITHUB_ISSUE_RE = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+/(issues|pull)/\d+/?$")

SAMPLES = [
    {
        "id": "mobile-nav",
        "label": "Broken mobile menu",
        "title": "Navigation menu does not open on mobile",
        "description": "On screens narrower than 600px, tapping the hamburger button in the top navigation does nothing. The menu stays hidden. On desktop the navigation links display correctly.\n\nSteps to reproduce:\n1. Open the site on a phone or resize the browser to 400px wide.\n2. Tap the hamburger icon.\n3. Nothing happens.\n\nExpected: the menu slides open.\nBrowsers: Chrome and Safari on mobile.",
    },
    {
        "id": "empty-form",
        "label": "Crash on empty form",
        "title": "App crashes when submitting an empty form",
        "description": "If I click Submit on the contact form without typing anything, the server returns a 500 error and the page shows a traceback. The error is: TypeError: 'NoneType' object has no attribute 'strip'.\n\nExpected: a friendly message such as 'Please fill in all fields' instead of a crash.",
    },
    {
        "id": "py-validation",
        "label": "Missing Python validation",
        "title": "calculate_discount() accepts negative percentages",
        "description": "The Python function calculate_discount(price, percent) does not validate its arguments. Passing a negative percent or a percent above 100 returns a nonsense price instead of raising an error.\n\nExample: calculate_discount(50, 150) returns -25.0.\n\nProposal: raise ValueError when percent is outside the range 0-100 and add unit tests.",
    },
]


def error(message, status=400):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/samples")
def samples():
    return jsonify(SAMPLES)


@app.get("/api/status")
def status():
    ok, message = analyzer.ollama_status()
    return jsonify({"ollama_available": ok, "message": message, "model": analyzer.OLLAMA_MODEL})


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Send a JSON body with title and description.")
    title = data.get("title", "")
    description = data.get("description", "")
    url = data.get("url", "") or ""
    mode = data.get("mode", "auto")
    if not all(isinstance(v, str) for v in (title, description, url, mode)):
        return error("All fields must be text.")
    title, description, url = title.strip(), description.strip(), url.strip()

    if not 3 <= len(title) <= 200:
        return error("Title must be between 3 and 200 characters.")
    if not 10 <= len(description) <= 8000:
        return error("Description must be between 10 and 8000 characters.")
    if url and not GITHUB_ISSUE_RE.match(url):
        return error("The URL must look like https://github.com/owner/repo/issues/123 (or leave it empty).")
    if mode not in ("auto", "demo"):
        return error("Mode must be 'auto' or 'demo'.")

    notice = None
    result = None
    source = "demo"
    if mode == "auto":
        try:
            result = analyzer.analyze_with_ollama(title, description, url)
            source = "ai"
        except RuntimeError as e:
            notice = f"AI analysis unavailable: {e} Showing demo guidance instead."
    if result is None:
        result = analyzer.analyze_demo(title, description)
        if mode == "demo":
            notice = "Demo mode: this is rule-based guidance, not AI analysis."

    return jsonify({
        "source": source,
        "model": analyzer.OLLAMA_MODEL if source == "ai" else None,
        "notice": notice,
        "input": {"title": title, "description": description, "url": url},
        "analysis": result,
    })


@app.errorhandler(413)
def too_large(_):
    return error("Request is too large.", 413)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
