import pytest
import os
import requests
from .. import step1_scrape_and_preprocess_articles as spa


@pytest.mark.filecheck
def test_websites_csv_exists():
    # Check if websites.csv exists in expected location
    csv_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'temp_data', 'articles.csv'
    )
    assert os.path.isfile(csv_path), f'{csv_path} does not exist'


@pytest.mark.apicheck
def test_scraping_api_is_up():
    # Use a known working URL for a simple GET request
    url = 'https://www.google.com'
    try:
        response = requests.get(url, timeout=5)
        assert response.status_code == 200
    except Exception as e:
        pytest.fail(f'API service not available: {e}')


@pytest.mark.contentextract
def test_extract_title_and_content_full_html():
    html = """
    <html>
      <body>
        <h1 class="entry-title">Test Title</h1>
        <div class="ok-news-post-hour"><span>2024-06-01</span></div>
        <div class="ok18-single-post-content-wrap">
          <p class="rich-para">Paragraph 1</p>
          <p class="rich-para">Paragraph 2</p>
        </div>
      </body>
    </html>
    """
    title, published_date, content = spa.extract_title_and_content(html)
    assert title == 'Test Title'
    assert published_date == '2024-06-01'
    assert 'Paragraph 1' in content
    assert 'Paragraph 2' in content


@pytest.mark.contentextract
def test_extract_title_and_content_missing_title():
    html = """
    <html>
      <body>
        <div class="ok-news-post-hour"><span>2024-06-01</span></div>
        <div class="ok18-single-post-content-wrap">
          <p>Paragraph 1</p>
        </div>
      </body>
    </html>
    """
    title, published_date, content = spa.extract_title_and_content(html)
    assert title == ''
    assert published_date == '2024-06-01'
    assert 'Paragraph 1' in content


@pytest.mark.contentextract
def test_extract_title_and_content_missing_date():
    html = """
    <html>
      <body>
        <h1 class="entry-title">Test Title</h1>
        <div class="ok18-single-post-content-wrap">
          <p>Paragraph 1</p>
        </div>
      </body>
    </html>
    """
    title, published_date, content = spa.extract_title_and_content(html)
    assert title == 'Test Title'
    assert published_date == ''
    assert 'Paragraph 1' in content


@pytest.mark.contentextract
def test_extract_title_and_content_missing_content_div():
    html = """
    <html>
      <body>
        <h1 class="entry-title">Test Title</h1>
        <div class="ok-news-post-hour"><span>2024-06-01</span></div>
        <p>Fallback Paragraph 1</p>
        <p>Fallback Paragraph 2</p>
      </body>
    </html>
    """
    title, published_date, content = spa.extract_title_and_content(html)
    assert title == 'Test Title'
    assert published_date == '2024-06-01'
    assert 'Fallback Paragraph 1' in content
    assert 'Fallback Paragraph 2' in content


@pytest.mark.contentextract
def test_extract_title_and_content_empty_html():
    html = ''
    title, published_date, content = spa.extract_title_and_content(html)
    assert title == ''
    assert published_date == ''
    assert content == ''
