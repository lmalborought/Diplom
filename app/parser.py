import re
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


async def fetch_page(session, url):
    """Запрос страницы"""
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=15)
        ) as response:
            return await response.text()
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None


async def parse_article(url: str):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            html = await fetch_page(session, url)
            if not html:
                return None

            soup = BeautifulSoup(html, "lxml")

            title_tag = soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else ""

            topics = []
            for t in soup.find_all("a", class_="tm-publication-hub__link"):
                span = t.find("span")
                if span:
                    topics.append(span.get_text(strip=True))

            text_tag = soup.find("div", class_="article-body")
            text = text_tag.get_text(" ", strip=True) if text_tag else ""

            links = []
            for a in soup.select("article a[href]"):
                href = a.get("href", "")
                if href.startswith("http"):
                    links.append(href)

            images = []
            for figure in soup.find_all("figure")[:5]:
                img_tag = figure.find("img")
                if img_tag:
                    src = img_tag.get("src")
                    if src:
                        images.append(src)

            return {
                "url": url,
                "title": title,
                "topics": topics,
                "full_text": text,
                "links": links,
                "images": images,
            }
        except Exception as e:
            print(f"Ошибка парсинга статьи {url}: {e}")
            return None


def extract_id(url: str) -> Optional[int]:
    match = re.search(r"(\d+)", url)
    if match:
        return int(match.group(1))
    return None


def data_cleaning(text: str) -> str:
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"http\S+", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\n", " ").replace("\r", " ")
    text = text.replace('"', " ")
    return text


def data_prep(text: str, topics: list, title: str) -> str:
    text = data_cleaning(text)
    topics_str = "".join(topics)
    return f"{title} [SEP] {topics_str} [SEP] {text}"
