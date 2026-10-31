# 🎯 JobMatch AI

![tests](https://github.com/Orlixx003/jobmatch-ai/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**AI assistant for job seekers.** Upload your CV, paste a job offer, and JobMatch AI uses the Claude API to:

- give a **match score (0–100)** with a short verdict
- list **matched** and **missing** skills
- suggest **concrete edits** to your CV for this offer
- write a **cover letter** in Polish, English or Ukrainian

Built because I'm applying for junior AI/IT roles in Poland myself and wanted a faster way to tailor each application.

## How it works

```
CV (PDF/DOCX/TXT) ──► text extraction ──┐
                                        ├──► Claude API ──► forced tool call ──► typed MatchResult ──► UI / CLI / Markdown report
Job offer (text) ───────────────────────┘
```

The model must answer through a `report_match` tool with a strict JSON schema, so the output is always structured — no fragile parsing of free text.

## Tech stack

Python · Anthropic Claude API (tool use / structured output) · Streamlit · pypdf · python-docx · pytest · GitHub Actions

## Quick start

```bash
git clone https://github.com/Orlixx003/jobmatch-ai.git
cd jobmatch-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then put your API key in .env
```

Get an API key at [console.anthropic.com](https://console.anthropic.com).

### Web app

```bash
streamlit run app.py
```

### Command line

```bash
python cli.py --cv examples/cv_example.txt --job examples/job_example.txt --lang pl --out report.md
```

## Tests

Tests use a fake client, so they run without an API key:

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Project structure

```
jobmatch/
  analyzer.py    # prompt, JSON schema, Claude call, MatchResult
  cv_reader.py   # PDF / DOCX / TXT text extraction
app.py           # Streamlit UI
cli.py           # command-line interface
tests/           # pytest tests (no API key needed)
examples/        # sample CV and job offer
```

## Privacy

Your API key and CV are never stored. `.env` and files named `my_cv.*` are in `.gitignore`.

## Roadmap

- [ ] Paste a job URL instead of text
- [ ] Batch mode: rank several offers at once
- [ ] Export cover letter as PDF

## Author

**Mykhailo Ivanyshyn** — Programowanie student at WSB Merito, Warsaw · [GitHub](https://github.com/Orlixx003)
