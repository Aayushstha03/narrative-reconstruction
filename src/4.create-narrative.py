import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import os
from time import sleep

# Path to the grouped events file
GROUPED_EVENTS_PATH = os.path.join(
    os.path.dirname(__file__), "data", "temp_data", "grouped_events_by_date.json"
)

output_schema = event_extraction_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "event": {
                "type": "string",
                "description": "Concise and merged title summarizing the event(s)",
            },
            "details": {
                "type": "string",
                "description": "Clean, merged or original summary of the event",
            },
            "actors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of involved actors with duplicates removed",
            },
            "source_event_indices": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of original event indices used to create this merged event",
            },
        },
        "required": ["event", "details", "actors", "source_event_indices"],
    },
}


def extract_event_fields_by_date(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    extracted = {}
    for date, events in data.items():
        extracted[date] = []
        for event in events:
            extracted[date].append(
                {
                    "id": event.get("id"),
                    "event": event.get("event"),
                    "details": event.get("details"),
                    "actors": event.get("actors"),
                }
            )
    # print(extracted)
    return extracted


def prompt_gemini_with_events(events_by_date):
    # Load environment variables and get API key
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    # Prepare the input for Gemini
    input_data = {"Events": events_by_date}
    # Compose the full prompt
    full_prompt = f"""
        You are an assistant that processes structured news event data.
        
        The input may be either:
        A single event object, or
        A list of multiple event objects

        Your tasks are:
        1. If only one event is provided, return it as-is in the specified output format (as a one-element list).
        2. If multiple events are provided:
            Group events that refer to the same real-world incident, even if their titles or details differ, then return in specified output format.
        3. Events that are not grouped should be included as-is, using their original title, details, and a single-element source_event_indices list

        {json.dumps(input_data, ensure_ascii=False, indent=2)}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=output_schema,
                temperature=0.0,
            ),
            contents=full_prompt,
        )
        # Try to parse JSON output from Gemini
        try:
            output_json = json.loads(response.text)
        except Exception:
            output_json = response.text
        return output_json
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None


def enrich_narrative_with_source_articles(grouped_events_path, narrative_output_path):
    with open(grouped_events_path, "r", encoding="utf-8") as f:
        grouped_data = json.load(f)
    with open(narrative_output_path, "r", encoding="utf-8") as f:
        narrative_data = json.load(f)

    for date, entries in narrative_data.items():
        # Build a lookup for id -> event for this date
        events_by_id = {str(e["id"]): e for e in grouped_data.get(date, [])}
        for entry in entries:
            unique_articles = []
            seen = set()
            for idx in entry.get("source_event_indices", []):
                event = events_by_id.get(str(idx))
                if event:
                    art_tuple = (
                        event.get("title"),
                        event.get("article_url"),
                        event.get("published_date"),
                    )
                    if art_tuple not in seen:
                        seen.add(art_tuple)
                        unique_articles.append(
                            {
                                "title": event.get("title"),
                                "article_url": event.get("article_url"),
                                "published_date": event.get("published_date"),
                            }
                        )
            entry["sources"] = unique_articles
            if "source_event_indices" in entry:
                del entry["source_event_indices"]

    with open(narrative_output_path, "w", encoding="utf-8") as f:
        json.dump(narrative_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Load the original grouped events structure
    with open(GROUPED_EVENTS_PATH, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    output_path = os.path.join(
        os.path.dirname(__file__), "data", "reconstructed_narrative.json"
    )
    # Use extract_event_fields_by_date to filter fields for Gemini
    filtered_data = extract_event_fields_by_date(GROUPED_EVENTS_PATH)
    # Accumulate results for each date
    narrative_results = {}
    for date, events in original_data.items():
        print(f"Processing date: {date}")
        # For each date, send only the list of filtered events (not a dict with date as key)
        filtered_events = filtered_data.get(date, [])
        # print(filtered_events)
        gemini_result = prompt_gemini_with_events(filtered_events)
        sleep(2)
        # Add/update the result for this date
        narrative_results[date] = gemini_result

        # Write the updated structure to a file after each date
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative_results, f, ensure_ascii=False, indent=2)
        print(f"Saved progress for {date} to {output_path}")
    print(f"Narrative output written to {output_path}")

    # Enrich the narrative output with source article info
    enrich_narrative_with_source_articles(GROUPED_EVENTS_PATH, output_path)
    print(f"Narrative output enriched with source articles and saved to {output_path}")
