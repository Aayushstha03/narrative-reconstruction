import subprocess
import sys

scripts = [
    'scripts/step1_scrape_and_preprocess_articles.py',
    'scripts/step2_extract_events.py',
    'scripts/step3_clean_extracted_events.py',
    'scripts/step4_create_narrative.py',
    'scripts/step5_insert_narratives_into_db.py',
]


def run_all():
    for script in scripts:
        print(f'\n=== Running {script} ===')
        result = subprocess.run(
            [sys.executable, script], capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if result.returncode != 0:
            print(f'Script {script} failed with exit code {result.returncode}')
            break


if __name__ == '__main__':
    run_all()
