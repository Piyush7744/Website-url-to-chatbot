# fetch_links.py

import sys
from bs4 import BeautifulSoup
import requests

def fetch_page_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': url
        }
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            return response.content
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def get_absolute_url(base_url, link):
    return requests.compat.urljoin(base_url, link)

def get_all_links(soup, base_url):
    all_links = []
    links = soup.find_all('a', href=True)
    for link in links:
        absolute_link = get_absolute_url(base_url, link['href'])
        all_links.append(absolute_link)
    return all_links

def find_nested_links(url, depth=2):
    if depth == 0:
        return []

    content = fetch_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    links = get_all_links(soup, url)
    
    all_links = []
    for link in links:
        if link not in all_links:
            all_links.append(link)
            nested_links = find_nested_links(link, depth - 1)
            all_links.extend(nested_links)
    
    return all_links

if __name__ == "__main__":
    url = sys.argv[1]
    depth = int(sys.argv[2])
    links = find_nested_links(url, depth)
    for link in links:
        print(link)
