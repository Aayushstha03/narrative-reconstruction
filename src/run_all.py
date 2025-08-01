import subprocess
import sys

scripts = [
    '1.scrape-preprocess-article-contents.py',
    '2.extract-events.py',
    '3.group-events-by-date.py',
    '4.create-narrative.py',
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
