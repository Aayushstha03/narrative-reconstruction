import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import nepali_datetime


def fetch_url_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Always decode as UTF-8 to avoid mojibake
        return response.content.decode('utf-8', errors='replace')
    except Exception as e:
        print(f'Failed to fetch {url}: {e}')
        return None


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

    # Get article content from <div class="ok18-single-post-content-wrap">, only <p class="rich-para">
    content_div = soup.find('div', class_='ok18-single-post-content-wrap')
    content = ''
    if content_div:
        rich_paras = content_div.find_all('p')
        content = '\n'.join(p.get_text(strip=True) for p in rich_paras)
    else:
        # fallback: get all <p> tags
        paragraphs = soup.find_all('p')
        content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

    return title, published_date, content


def parse_nepali_date(date_str):
    """
    Parse a Nepali date string and return (nepali_datetime.date, gregorian_date, day_name) or (None, None, None) if parsing fails.
    """
    nepali_months = {
        'बैशाख': 1,
        'जेठ': 2,
        'असार': 3,
        'साउन': 4,
        'भदौ': 5,
        'आश्विन': 6,
        'कार्तिक': 7,
        'मंसिर': 8,
        'पुष': 9,
        'माघ': 10,
        'फागुन': 11,
        'चैत्र': 12,
        'Baisakh': 1,
        'Jestha': 2,
        'Ashar': 3,
        'Shrawan': 4,
        'Bhadra': 5,
        'Ashwin': 6,
        'Kartik': 7,
        'Mangsir': 8,
        'Poush': 9,
        'Magh': 10,
        'Falgun': 11,
        'Chaitra': 12,
    }
    import re

    date_part = date_str.split('गते')[0].strip()
    date_part = re.sub(r'[\d१२३४५६७८९०]{1,2}:\d{2}', '', date_part).strip()
    nepali_date_pattern = re.compile(
        r'([१२३४५६७८९०\d]{4})\s*([\w\u0900-\u097F]+)\s*([१२३४५६७८९०\d]{1,2})'
    )
    m = nepali_date_pattern.search(date_part)
    if m:

        def dev_to_ascii(s):
            dev_map = str.maketrans('०१२३४५६७८९', '0123456789')
            return s.translate(dev_map)

        year = int(dev_to_ascii(m.group(1)))
        month_raw = m.group(2).strip()
        day = int(dev_to_ascii(m.group(3)))
        month = nepali_months.get(month_raw, None)
        if month:
            try:
                ndt = nepali_datetime.date(year, month, day)
                gdt = ndt.to_datetime_date()
                nepali_days = [
                    'Sunday',
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                ]
                day_name = nepali_days[ndt.weekday()]
                return ndt, gdt, day_name
            except Exception as e:
                print(f'[DEBUG] Exception in nepali_datetime.date: {e}')
    return None, None, None


def parse_gregorian_date(date_str):
    for fmt in (
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%d %B %Y',
    ):
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return dt, dt.strftime('%A')
        except Exception:
            continue
    return None, ''


def get_gregorian_and_day(date_str):
    """
    Returns (gregorian_date, day_name) from a Nepali or Gregorian date string.
    """
    _, gdt, day_name = parse_nepali_date(date_str)
    if gdt:
        return gdt, day_name
    gdt, day_name = parse_gregorian_date(date_str)
    return gdt, day_name


def replace_dates_and_days_in_text(text):
    """
    Find Nepali month/day/year mentions in text, replace with Gregorian date and English weekday.
    Also replace Nepali weekday names with English.
    """
    import re

    # Nepali months and days
    nepali_months = {
        'बैशाख': 1,
        'जेठ': 2,
        'असार': 3,
        'साउन': 4,
        'भदौ': 5,
        'आश्विन': 6,
        'कार्तिक': 7,
        'मंसिर': 8,
        'पुष': 9,
        'माघ': 10,
        'फागुन': 11,
        'चैत्र': 12,
        'Baisakh': 1,
        'Jestha': 2,
        'Ashar': 3,
        'Shrawan': 4,
        'Bhadra': 5,
        'Ashwin': 6,
        'Kartik': 7,
        'Mangsir': 8,
        'Poush': 9,
        'Magh': 10,
        'Falgun': 11,
        'Chaitra': 12,
    }
    nepali_days = [
        'आइतबार',
        'सोमबार',
        'मंगलबार',
        'बुधबार',
        'बिहीबार',
        'शुक्रबार',
        'शनिबार',
    ]
    english_days = [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
    ]
    nepali_day_map = dict(zip(nepali_days, english_days))

    # Replace Nepali weekday names with English
    for np_day, en_day in nepali_day_map.items():
        # if re.search(np_day, text):
        # print(f"[DEBUG] Replacing Nepali weekday '{np_day}' with '{en_day}'")
        text = re.sub(np_day, en_day, text)

    # Regex for Nepali date: year month day, month day, or day month (Devanagari or ASCII digits)
    # Handles: YYYY month DD, month DD, DD month, with or without whitespace
    date_patterns = [
        re.compile(
            r'([१२३४५६७८९०\d]{4})\s*([\w\u0900-\u097F]+)\s*([१२३४५६७८९०\d]{1,2})\s*गते?'
        ),  # YYYY month DD
        re.compile(
            r'([\w\u0900-\u097F]+)\s*([१२३४५६७८९०\d]{1,2})'
        ),  # month DD
        re.compile(
            r'([१२३४५६७८९०\d]{1,2})\s*([\w\u0900-\u097F]+)'
        ),  # DD month
    ]

    def dev_to_ascii(s):
        dev_map = str.maketrans('०१२३४५६७८९', '0123456789')
        return s.translate(dev_map)

    def replace_date_match(m, order):
        try:
            # print(f"[DEBUG] Date match: {m.groups()} | order: {order}")
            if order == 'ymd':
                year = int(dev_to_ascii(m.group(1)))
                month_raw = m.group(2).strip()
                day = int(dev_to_ascii(m.group(3)))
            elif order == 'md':
                year = nepali_datetime.date.today().year
                month_raw = m.group(1).strip()
                day = int(dev_to_ascii(m.group(2)))
            elif order == 'dm':
                year = nepali_datetime.date.today().year
                day = int(dev_to_ascii(m.group(1)))
                month_raw = m.group(2).strip()
            else:
                return m.group(0)
            # print(f"[DEBUG] Parsed: year={year}, month_raw={month_raw}, day={day}")
            month = nepali_months.get(month_raw, None)
            # print(f"[DEBUG] Mapped month: {month}")
            if month:
                ndt = nepali_datetime.date(year, month, day)
                gdt = ndt.to_datetime_date()
                weekday = gdt.strftime('%A')
                # print(f"[DEBUG] Replacing Nepali date with: {gdt.strftime('%Y-%m-%d')} ({weekday})")
                return f'{gdt.strftime("%Y-%m-%d")} ({weekday})'
        except Exception as e:
            print(f'[DEBUG] Exception in replace_date_match: {e}')
        return m.group(0)

    # Replace all Nepali date mentions with Gregorian date and weekday
    # 1. YYYY month DD
    text = date_patterns[0].sub(lambda m: replace_date_match(m, 'ymd'), text)
    # 2. month DD
    text = date_patterns[1].sub(lambda m: replace_date_match(m, 'md'), text)
    # 3. DD month
    text = date_patterns[2].sub(lambda m: replace_date_match(m, 'dm'), text)

    return text


def replace_time_concepts(text):
    """
    Replace Nepali time-related words/phrases with English equivalents.
    Expandable for more words later.
    """
    replacements = {
        'गत': 'last',
        # Add more replacements here as needed
    }
    import re

    for np_word, en_word in replacements.items():
        text = re.sub(np_word, en_word, text)
    return text


def main():
    df = pd.read_csv('src/data/temp_data/articles.csv')
    results = []
    for url in df['url']:
        print(f'Fetching: {url}')
        html = fetch_url_content(url)
        if html:
            title, published_date_raw, content = extract_title_and_content(
                html
            )
        else:
            title, published_date_raw, content = '', '', ''
        gdt, day = get_gregorian_and_day(published_date_raw)
        published_date = f'{gdt.strftime("%Y-%m-%d")} ({day})' if gdt else ''
        # Replace Nepali dates, days, and time concepts in content
        content_replaced = replace_dates_and_days_in_text(content)
        content_replaced = replace_time_concepts(content_replaced)
        results.append(
            {
                'url': url,
                'title': title,
                'published_date': published_date,
                'content': content_replaced,
            }
        )
    # Save results to a JSON file
    import json

    with open(
        'src/data/temp_data/article_contents.json', 'w', encoding='utf-8'
    ) as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(
        'Done. Saved to src/temp_data/article_contents.csv and src/temp_data/article_contents.json'
    )


if __name__ == '__main__':
    main()
