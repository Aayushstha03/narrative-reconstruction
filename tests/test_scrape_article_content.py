import pytest
from src.scrape_article_content import extract_title_and_content


@pytest.mark.parametrize(
    'html,expected_title,expected_date,expected_content',
    [
        (
            """
        <html>
            <body>
                <h1 class="entry-title">Test Title</h1>
                <div class="ok-news-post-hour"><span>2025-08-06</span></div>
                <div class="ok18-single-post-content-wrap">Main content here.</div>
            </body>
        </html>
        """,
            'Test Title',
            '2025-08-06',
            'Main content here.',
        ),
        (
            """
        <html>
            <body>
                <h1 class="entry-title">Another Title</h1>
                <p>Fallback content paragraph 1.</p>
                <p>Fallback content paragraph 2.</p>
            </body>
        </html>
        """,
            'Another Title',
            '',
            'Fallback content paragraph 1.\nFallback content paragraph 2.',
        ),
    ],
)
def test_extract_title_and_content(
    html, expected_title, expected_date, expected_content
):
    title, date, content = extract_title_and_content(html)
    assert title == expected_title
    assert date == expected_date
    assert content == expected_content
