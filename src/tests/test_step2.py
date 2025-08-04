import os
import pytest


# you need to create .env and supply the gemini API key as GEMINI_API_KEY
def test_env_file_exists():
    assert os.path.isfile('.env'), (
        "'.env' file does not exist in the project root."
    )


@pytest.mark.skipif(
    not os.path.isfile('.env'),
    reason="'.env' file not found, skipping GEMINI_API_KEY check.",
)
def test_gemini_api_key_in_env():
    with open('.env') as f:
        env_content = f.read()
    assert 'GEMINI_API_KEY' in env_content, (
        'GEMINI_API_KEY entry not found in .env file.'
    )
