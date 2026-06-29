import os
import json
import datetime
from pathlib import Path
from google import genai
from django.conf import settings

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_PROMPT = """You are an expert web analyst specializing in SEO, conversion optimization, 
content clarity, and UX for marketing websites. 

You will receive structured metrics extracted from a webpage along with a preview of its content.
Your job is to produce a grounded, specific analysis — not generic advice.
Every insight and recommendation MUST reference the actual numbers from the metrics provided.

You must respond ONLY with valid JSON in exactly this structure:
{
  "insights": {
    "seo_structure": "string",
    "messaging_clarity": "string",
    "cta_usage": "string",
    "content_depth": "string",
    "ux_concerns": "string"
  },
  "recommendations": [
    {
      "priority": 1,
      "title": "string",
      "reasoning": "string"
    }
  ]
}

Rules:
- insights: each field is 2-4 sentences, specific to the metrics
- recommendations: exactly 4 items, ordered by priority (1 = highest)
- reasoning in each recommendation must cite at least one metric value
- Do not include markdown, backticks, or any text outside the JSON"""


def build_user_prompt(url: str, metrics: dict) -> str:
    return f"""Analyze this webpage and return structured JSON insights.

URL: {url}

EXTRACTED METRICS:
- Word count: {metrics['word_count']}
- H1 tags: {metrics['h1_count']}
- H2 tags: {metrics['h2_count']}
- H3 tags: {metrics['h3_count']}
- CTA count: {metrics['cta_count']}
- Internal links: {metrics['internal_links']}
- External links: {metrics['external_links']}
- Total images: {metrics['image_count']}
- Images missing alt text: {metrics['images_missing_alt']}
- Meta title: "{metrics['meta_title']}"
- Meta description: "{metrics['meta_description']}"

PAGE CONTENT PREVIEW (first 3000 words):
{metrics['page_text_preview']}

Return only the JSON object as specified."""


def run_ai_analysis(url: str, metrics: dict) -> dict:
    user_prompt = build_user_prompt(url, metrics)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
    )

    raw_output = response.text

    # --- Parse JSON from model output ---
    cleaned = raw_output.strip().strip("```json").strip("```").strip()
    parsed = json.loads(cleaned)

    # --- Save prompt log ---
    log = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "url": url,
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "raw_model_output": raw_output,
        "parsed_output": parsed,
    }

    log_dir = Path(settings.PROMPT_LOGS_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_filename = f"audit_{timestamp}.json"
    log_path = log_dir / log_filename

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    return {
        "insights": parsed["insights"],
        "recommendations": parsed["recommendations"],
        "prompt_log_file": log_filename,
    }