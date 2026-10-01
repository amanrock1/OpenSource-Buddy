# OpenSource Buddy

**Understand any GitHub issue and plan your first open-source contribution, in under a minute.**

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-3776AB.svg) ![Flask](https://img.shields.io/badge/flask-3.x-000000.svg) ![Hackertoberfest](https://img.shields.io/badge/built%20for-Hackertoberfest-ff5a1f.svg)

## The problem

Many newcomers want to contribute to open source but get stuck at step one: reading an issue and working out what it means, which skills it needs, and where to start. Maintainers tag issues "good first issue", but beginners still don't know *how* to approach them.

OpenSource Buddy turns an issue's title and description into:

1. A plain-language **explanation**
2. The **skills** required
3. A **difficulty estimate** (beginner / intermediate / advanced)
4. A numbered **contribution roadmap**
5. **Questions to investigate** in the repository
6. A **testing checklist** for verifying a fix

> **Honesty by design:** all output is *generated guidance, not verified fact*. The app never reads the repository and never fetches anything from GitHub. The only facts shown are the text you typed, and the UI labels everything else as a generated suggestion.

## Features

- Paste an issue title, description and optional GitHub issue URL (the URL is format-checked only, never fetched).
- Optional AI analysis through a local [Ollama](https://ollama.com) server.
- Deterministic **demo mode** that works with no AI at all, clearly labelled as demo guidance.
- Three built-in sample issues: broken mobile menu, empty-form crash, missing Python validation.
- Save, reopen and delete analyses in your browser (localStorage), tolerant of corrupted data.
- Copy the roadmap as Markdown to paste into a pull request or notes.
- Responsive layout, automatic dark mode, loading state, form validation and friendly errors.
- User text is always rendered as plain text, never as HTML, and the app never executes code from an issue.

## Architecture

```mermaid
flowchart LR
    subgraph Browser
        UI["index.html + style.css"]
        JS["script.js<br/>form, validation, rendering"]
        LS[("localStorage<br/>saved issues")]
        UI --- JS
        JS <--> LS
    end

    subgraph Flask["Flask server (app.py)"]
        API["/api/analyze<br/>/api/samples<br/>/api/status"]
        VAL["Backend input validation"]
        AN["analyzer.py"]
        API --> VAL --> AN
    end

    OLL["Ollama server<br/>gemma4:31b-cloud (optional)"]
    DEMO["Demo mode<br/>rule-based templates"]

    JS -- "JSON over HTTP" --> API
    AN -- "1. try AI, with timeout" --> OLL
    AN -- "2. fallback if unavailable<br/>or answer unusable" --> DEMO
```

### Request flow

```mermaid
sequenceDiagram
    actor User
    participant B as Browser (script.js)
    participant F as Flask (app.py)
    participant A as analyzer.py
    participant O as Ollama

    User->>B: Paste issue, click Analyze
    B->>B: Validate form
    B->>F: POST /api/analyze
    F->>F: Validate title, description, URL, size
    alt AI mode and Ollama reachable
        F->>A: analyze_with_ollama()
        A->>O: /api/chat (timeout)
        O-->>A: JSON answer
        A-->>F: Checked and normalized result (source: ai)
    else demo mode, or Ollama failed
        F->>A: analyze_demo()
        A-->>F: Deterministic result (source: demo) + notice
    end
    F-->>B: JSON result
    B->>B: Render with textContent (no raw HTML)
    User->>B: Save
    B->>B: Store in localStorage
```

### Project structure

```
opensource-buddy/
├── app.py            # Flask routes, input validation, sample issues
├── analyzer.py       # Ollama client, response checking, demo-mode fallback
├── templates/
│   └── index.html    # Single-page UI
├── static/
│   ├── style.css     # Responsive styles + dark mode
│   └── script.js     # Form, rendering, localStorage, copy-to-clipboard
├── requirements.txt  # Flask only
├── LICENSE           # MIT
└── README.md
```

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask (the only dependency) |
| Frontend | HTML5, CSS3 (custom properties, grid, dark mode), vanilla JavaScript |
| Storage | Browser localStorage |
| Optional AI | Ollama with `gemma4:31b-cloud`, called via Python's standard library (`urllib`) |
| Fallback | Deterministic keyword-based demo templates |
| Docs | Mermaid diagrams |

## Setup (Windows PowerShell)

Requires Python 3.9+ on your PATH.

```powershell
git clone https://github.com/amanrock1/OpenSource-Buddy.git
cd OpenSource-Buddy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If script execution is blocked, run `Set-ExecutionPolicy -Scope Process RemoteSigned` first.

## Run

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. Stop the server with `Ctrl+C`.

## How demo mode works

Demo mode matches keywords in the issue against a few templates (frontend layout, crash on bad input, Python validation) and otherwise uses a generic template. It is deterministic and involves no AI. It is used when:

- you tick **Use demo mode only**, or
- Ollama is unreachable, times out, or returns an unusable answer. The app then shows a notice saying why.

Demo results are labelled "Demo guidance" in the UI, in the banner, and in saved items.

## Optional Ollama integration

By default the app calls `gemma4:31b-cloud` at `http://localhost:11434`. Configure with environment variables before starting:

```powershell
$env:OLLAMA_MODEL = "gemma4:31b-cloud"   # any model you already have in Ollama
$env:OLLAMA_URL = "http://localhost:11434"
$env:OLLAMA_TIMEOUT = "120"              # seconds
python app.py
```

The app does not download models and needs no API keys. Model output is validated and normalized before display, and the issue text is passed to the model as untrusted data.

## Security notes

- Backend validates length, type and URL format and caps request size at 64 KB.
- All user and model text is inserted with `textContent`, never `innerHTML`.
- No credentials in the code or frontend, and `.env` files are git-ignored.
- Code in an issue is never executed.

## Known limitations

- The AI has not seen the repository, so it can be wrong. Difficulty is only an estimate.
- Demo mode is keyword-based and coarse.
- Local models can be slow or return malformed answers (the app then falls back to demo guidance).
- Saved issues live in one browser only, capped at 50.
- No GitHub fetching, login or database by design in this first version.
- Uses Flask's development server, so it is intended for local use.
- No automated test suite yet.

## Screenshots

**Main page**: paste an issue or load an example.

![OpenSource Buddy main page](1.png)

**AI analysis result**: explanation, skills, difficulty estimate and a numbered roadmap, with generated content clearly separated from your input.

![OpenSource Buddy analysis result](2.png)

## Roadmap ideas

- Fetch issue text from a GitHub URL (read-only)
- Test suite and CI
- More demo templates and languages
- Export saved issues

## Contributing

Contributions are welcome.

1. Fork the repository and create a branch.
2. Make a small, focused change and test it by hand (add tests if you can).
3. Open a pull request describing what and why.

Good first ideas: more demo templates, a pytest suite, accessibility improvements, UI polish.

## License

MIT. See [LICENSE](LICENSE).
