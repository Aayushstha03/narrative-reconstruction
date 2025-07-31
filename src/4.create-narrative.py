import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import os

# Path to the grouped events file
GROUPED_EVENTS_PATH = os.path.join(
    os.path.dirname(__file__), "data", "grouped_events_by_date.json"
)

output_schema = event_extraction_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "new_event": {
                "type": "string",
                "description": "Concise and merged title summarizing the event(s)",
            },
            "new_details": {
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
        "required": ["new_event", "new_details", "actors", "source_event_indices"],
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
    print(extracted)
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
        You are given a list of news events that may contain duplicates or near-duplicates. Each event has a title, summary, list of actors, and a unique index.
        Your task is to:
        1. Group events that refer to the same real-world incident.
        2. Merge each group into a single clean event
        
        {json.dumps(input_data, ensure_ascii=False, indent=2)}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
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


if __name__ == "__main__":
    # Load the original grouped events structure
    with open(GROUPED_EVENTS_PATH, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    output_path = os.path.join(
        os.path.dirname(__file__), "data", "narrative_output_by_date.json"
    )
    # Use extract_event_fields_by_date to filter fields for Gemini
    filtered_data = extract_event_fields_by_date(GROUPED_EVENTS_PATH)
    # Accumulate results for each date
    narrative_results = {}
    for date, events in original_data.items():
        print(f"Processing date: {date}")
        # For each date, send only the list of filtered events (not a dict with date as key)
        filtered_events = filtered_data.get(date, [])
        print(filtered_events)
        gemini_result = prompt_gemini_with_events(filtered_events)
        # Add/update the result for this date
        narrative_results[date] = gemini_result

        # Write the updated structure to a file after each date
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative_results, f, ensure_ascii=False, indent=2)
        print(f"Saved progress for {date} to {output_path}")
    print(f"Narrative output written to {output_path}")
