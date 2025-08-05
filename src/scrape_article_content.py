import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def extract_title_and_content(html):
    soup = BeautifulSoup(html, 'lxml')
    # Get title from <h1 class="entry-title">
    title_tag = soup.find('h1', class_='entry-title')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Get published date from <div class="ok-news-post-hour"><span>...</span></div>
    date_tag = soup.find('div', class_='ok-news-post-hour')
    published_date = ''
    if date_tag:
        span = date_tag.find('span')
        if span:
            published_date = span.get_text(strip=True)

    # Get article content from <div class="ok18-single-post-content-wrap">
    content_div = soup.find('div', class_='ok18-single-post-content-wrap')
    content = ''
    if content_div:
        content = content_div.get_text(separator='\n', strip=True)
    else:
        # fallback: get all <p> tags
        paragraphs = soup.find_all('p')
        content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

    return title, published_date, content


def fetch_url_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Always decode as UTF-8 to avoid mojibake
        return response.content.decode('utf-8', errors='replace')
    except Exception as e:
        print(f'Failed to fetch {url}: {e}')
        return None


def main():
    df = pd.read_csv('src/data/articles.csv')
    results = []
    for url in df['url']:
        print(f'Fetching: {url}')
        html = fetch_url_content(url)
        if html:
            title, published_date, content = extract_title_and_content(html)
        else:
            title, published_date, content = '', '', ''
        results.append(
            {
                'url': url,
                'title': title,
                'published_date': published_date,
                'content': content,
            }
        )
   
    with open('src/data/article_contents.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(
        'Done. Saved to src/article_contents.csv and src/article_contents.json'
    )
    return results


if __name__ == '__main__':
    main()
