# Website Audit Tool

An AI-powered internal tool that accepts a single URL, extracts factual page metrics via scraping, and uses Google Gemini to generate structured SEO/UX insights and prioritized recommendations.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally
- A Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
SECRET_KEY=django-insecure-your-key-here
DEBUG=True
DB_NAME=website_audit_tool_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=your-key-here
```

```bash
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`. The Vite proxy forwards all `/api` requests to the Django backend — no manual CORS configuration needed in development.

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| POST | `/api/audit/` | Run a new audit for a URL |
| GET | `/api/audits/` | List all past audit reports |
| GET | `/api/audits/<id>/` | Retrieve a single report by ID |

### Example Request

```bash
curl -X POST http://localhost:8000/api/audit/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## Architecture Overview

```
Browser (React + Vite)
        │
        │  POST /api/audit/
        ▼
Django REST Framework
        │
        ├── scraper.py ──► requests + BeautifulSoup4
        │                  Extracts: word count, headings, CTAs,
        │                  links, images, alt text, meta tags
        │
        ├── ai.py ───────► Google Gemini 2.5 Flash
        │                  Input: URL + metrics dict
        │                  Output: structured insights + recommendations
        │                  Side effect: saves prompt log to /prompt-logs/
        │
        └── models.py ───► PostgreSQL (AuditReport)
                           Stores all metrics + AI output + log filename
```

### Key Design Principles

**Separation of concerns.** The scraper (`scraper.py`) and AI layer (`ai.py`) are entirely independent modules. The scraper returns a plain Python dict — it knows nothing about Gemini, Django, or the database. The AI module knows nothing about HTTP or BeautifulSoup. The Django view orchestrates them: scrape → analyze → save → respond.

**Metrics as AI grounding.** Raw page metrics are extracted before any AI call is made, then passed explicitly into the prompt. This ensures Gemini's insights are anchored to real numbers rather than hallucinated estimates. The AI cannot claim "the page has no H1 tags" without that being verifiable against `h1_count` in the same response.

**Structured output by design.** The Gemini prompt instructs the model to return only valid JSON. The response is parsed and validated before being saved to the database. This makes the AI output reliable enough to render directly in the UI without any post-processing.

**Prompt observability.** Every audit automatically saves a full prompt log to `/prompt-logs/` containing the system prompt, user prompt, raw model output, and parsed result. This makes AI behavior fully auditable without needing a separate logging infrastructure.

---

## AI Design Decisions

### Model Choice: Gemini 2.5 Flash

Gemini 2.5 Flash was chosen for its speed and cost efficiency on structured generation tasks. An audit tool that users expect to return results in a few seconds benefits from a fast model. The task — analyzing a structured metrics dict and generating categorized text — does not require frontier reasoning capability.

### Prompt Structure

The AI layer uses a two-part prompt:

**System prompt** establishes the model's role as a senior SEO/UX analyst at a web agency. It instructs the model to ground every insight in the provided metrics, avoid generic advice, and return only a specific JSON schema with five insight categories and four prioritized recommendations.

**User prompt** injects the target URL and the full metrics dict, then asks the model to produce the analysis. Keeping factual data in the user prompt, rather than the system prompt, makes each call self-contained and easy to inspect in the logs.

### Structured Output Enforcement

The prompt explicitly specifies the expected JSON schema and instructs the model not to include any text outside the JSON object. The `ai.py` parser strips markdown fences if present before calling `json.loads()`. If parsing fails, the error is surfaced to the view rather than silently swallowed.

### Insight Categories

The five insight categories (SEO structure, messaging clarity, CTA usage, content depth, UX concerns) map directly to the evaluation criteria for marketing websites. Each maps to one or more extractable metrics, so the model always has data to reference rather than making subjective assessments in a vacuum.

---

## Trade-offs

**Single-page analysis only.** The tool audits one URL at a time with no crawling. This keeps the scope tight and response times fast, but means it cannot evaluate site-wide issues like internal linking structure, duplicate content across pages, or sitemap coverage.

**No JavaScript rendering.** The scraper uses `requests` + `BeautifulSoup4`, which fetches raw HTML. Pages that render their content client-side (React SPAs, lazy-loaded sections) will return incomplete metrics. A headless browser like Playwright would fix this at the cost of significantly higher latency and infrastructure complexity.

**AI output is one-shot.** There is no retry or fallback if Gemini returns malformed JSON. In practice, the structured prompt is reliable, but a production system should include retry logic with exponential backoff and a fallback response.

**No authentication.** The API is open. In an internal agency tool this is acceptable, but any external deployment would need at minimum API key authentication on the Django endpoints.

**Prompt logs are local files.** Logs are written to `/prompt-logs/` on the server filesystem. This works for development and evaluation but does not scale — a production deployment should write logs to object storage (S3, GCS) or a structured log sink.

---

## What I Would Improve With More Time

**JavaScript rendering.** Replace `requests` with Playwright for a headless Chromium pass, so SPAs and lazy-loaded content are captured accurately. This is the single highest-impact improvement for real-world accuracy.

**Audit history UI.** The backend already exposes `GET /api/audits/` and `GET /api/audits/<id>/`. A history view in the frontend would let users browse past reports without re-running audits.

**Confidence indicators.** Surface a simple signal next to each AI insight showing which metric it is grounded in. This makes the AI output more trustworthy and easier to act on for non-technical stakeholders.

**Retry and fallback logic.** Wrap the Gemini call in retry logic with exponential backoff. If structured JSON parsing fails after retries, return a degraded response with metrics only rather than a 500 error.

**Streaming insights.** Gemini supports streaming. Returning metrics immediately and streaming AI insights as they generate would make the UI feel significantly faster for end users.

**Diff view for re-audits.** If a URL has been audited before, show a delta between the previous and current metrics. This would make the tool useful for tracking improvements over time, not just one-off evaluations.

**Prompt versioning.** Store the system prompt hash alongside each audit record. As prompts are iterated, this makes it possible to compare outputs across prompt versions for the same URL.

---

## Prompt Logs

Every audit generates a log file saved to `/prompt-logs/audit_<timestamp>.json`. The filename is stored on the `AuditReport` model and returned in the API response as `prompt_log_file`.

Each log contains:

```json
{
  "timestamp": "2025-01-01T00:00:00",
  "url": "https://example.com",
  "system_prompt": "...",
  "user_prompt": "...",
  "raw_model_output": "...",
  "parsed_output": {
    "insights": {},
    "recommendations": []
  }
}
```

These logs are the primary artifact for evaluating AI design decisions. They show exactly what was sent to the model, what came back, and how it was interpreted — with no black box.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Django 6 + Django REST Framework |
| Database | PostgreSQL |
| AI | Google Gemini 2.5 Flash |
| Scraping | requests + BeautifulSoup4 |
