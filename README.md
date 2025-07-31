## Narrative Reconstruction Pipeline

This project extracts, processes, and reconstructs narratives from Nepali news articles using LLMs and structured data processing. The pipeline consists of four main scripts:

### 1. scrape-preprocess-article-contents.py
**Purpose:**
- Scrapes news articles from URLs (from a CSV), extracts the title, published date, and main content.
- Converts Nepali dates to Gregorian and replaces Nepali weekday names with English.
- Cleans and normalizes article text.
- Saves the processed articles to `src/data/temp_data/article_contents.json`.

### 2. extract-events.py
**Purpose:**
- Uses Google Gemini LLM to extract structured event entities from each article.
- Extracted fields: event, actors, event_date, event_time, location, details.
- Each article's events are saved in `src/data/temp_data/article_entities.json`.

### 3. group-events-by-date.py
**Purpose:**
- Canonicalizes actor and location names using LLM-based unification.
- Groups all extracted events by their event date.
- Assigns a unique ID to each event per date.
- Saves grouped events to `src/data/temp_data/grouped_events_by_date.json`.

### 4. create-narrative.py
**Purpose:**
- Merges and summarizes grouped events for each date using the Gemini LLM.
- For each date, generates a narrative summary and merges related events.
- Enriches each narrative entry with a `sources` array (unique article info for each event).
- Removes the `source_event_indices` field from the final output.
- Saves the reconstructed narratives to `src/data/reconstructed_narrative.json`.

---


## Pipeline Flow
You can run the entire pipeline with a single command:

```bash
uv run .\src\run_all.py
```

This will execute all four scripts in order:
1. `1.scrape-preprocess-article-contents.py` — fetch and clean articles
2. `2.extract-events.py` — extract structured events from articles
3. `3.group-events-by-date.py` — canonicalize, group, and assign IDs to events
4. `4.create-narrative.py` — merge, summarize, and enrich events into final narratives

You can also run each script individually if needed.

## Data Files
- `articles.csv`: List of article URLs to process.
- `article_contents.json`: Cleaned article data.
- `article_entities.json`: Extracted event entities per article.
- `grouped_events_by_date.json`: Events grouped and indexed by date.
- `reconstructed_narrative.json`: Final narrative output with sources.

## Requirements
- Python 3.8+
- pandas, requests, beautifulsoup4, lxml, nepali-datetime, google-genai, python-dotenv

## Notes
- LLM API keys must be set in your `.env` file as `GEMINI_API_KEY`.
- The pipeline is robust to missing or malformed data and will print debug info as needed.
