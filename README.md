# OpenSource Buddy

A small web app that helps beginners understand a GitHub issue and plan their first open-source contribution.

## The problem

Many newcomers want to contribute but get stuck at the first step: reading an issue and working out what it means, which skills it needs, and where to start. OpenSource Buddy turns an issue's title and description into a plain-language explanation, a skills list, a difficulty estimate, a step-by-step roadmap, questions to investigate and a testing checklist.

> All output is **generated guidance, not verified fact**. The app never reads the repository or fetches anything from GitHub. The only facts shown are the text you typed.

## Features

- Paste an issue title, description and optional GitHub issue URL (the URL is only format-checked, never fetched).
- Six result sections: simple explanation, skills, difficulty estimate, roadmap, questions, testing checklist.
- Three built-in example issues (mobile menu, empty-form crash, Python validation).
- Optional AI analysis through a local [Ollama](https://ollama.com) server.
- Deterministic **demo mode** that works with no AI at all, clearly labelled as such.
- Save, reopen and delete analyses in your browser (localStorage).
- Responsive layout, loading state, form validation and friendly errors.

### Screenshots

No screenshots are included yet. To add them: run the app, take screenshots of the main page and a result, save them in a `docs/` folder (e.g. `docs/main.png`) and reference them here with `![Main page](docs/main.png)`.

## Technology stack

- Python 3 + Flask (the only dependency)
- HTML, CSS, vanilla JavaScript
- Browser localStorage for saved issues
- Optional: Ollama (called with Python's standard library, no extra packages)

## Setup (Windows PowerShell)

Requires Python 3.9+ installed and on your PATH.

```powershell
cd opensource-buddy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If script execution is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` first.

## Run

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. Stop the server with `Ctrl+C`.

## How demo mode works

Demo mode uses keyword matching to pick one of a few canned guidance templates (frontend layout, crash on bad input, Python validation) or a generic template. It is deterministic and involves no AI. It is used when:

- you tick "Use demo mode only", or
- Ollama is unreachable, the model fails, or its answer is unusable. The app then shows a notice saying why.

Demo results are labelled "Demo guidance" in the UI and in saved items.

## Optional Ollama integration

By default the app calls the model `gemma4:31b-cloud` on `http://localhost:11434`. Configure with environment variables before starting:

```powershell
$env:OLLAMA_MODEL = "gemma4:31b-cloud"   # any model you already have in Ollama
$env:OLLAMA_URL = "http://localhost:11434"
$env:OLLAMA_TIMEOUT = "120"              # seconds
python app.py
```

The app does not download models and needs no API keys. No credentials are stored in the code.

## Known limitations

- The AI has not seen the repository, so it can be wrong; the difficulty is only an estimate.
- Demo mode is keyword-based and coarse.
- Local models can be slow or produce malformed answers (the app falls back to demo guidance).
- Saved issues live in one browser only, capped at 50.
- No GitHub fetching, login or database by design (first version).
- Uses Flask's development server, intended for local use only.
- No automated test suite yet; the UI has only been checked by hand.

## Contributing

Contributions are welcome.

1. Fork this repository and create a branch.
2. Make a small, focused change and test it by hand (and add tests if you can).
3. Open a pull request describing what and why.

Good first ideas: more demo templates, a test suite, accessibility improvements, a copy-to-clipboard button.

## License

MIT. See [LICENSE](LICENSE).
