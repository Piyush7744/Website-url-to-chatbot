import sys
import requests
import os
from urllib.parse import urlparse, urljoin

def download_webpages(links):
    downloaded_files = []
    for link in links:
        try:
            # Sanitize the URL
            parsed_url = urlparse(link)
            if not parsed_url.scheme:
                link = 'https://' + link
            link = urljoin('https://www.quicsolv.com/', link.strip())

            response = requests.get(link)
            if response.status_code == 200:
                file_name = os.path.basename(parsed_url.path)
                if not file_name:
                    file_name = f"{len(downloaded_files)}.html"
                elif not file_name.endswith('.html'):
                    file_name += '.html'
                file_path = os.path.join('downloaded_webpages', file_name)
                os.makedirs('downloaded_webpages', exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                downloaded_files.append(file_path)
        except requests.RequestException as e:
            print(f"Failed to download {link}: {e}", file=sys.stderr)
        except OSError as e:
            print(f"Error saving file for {link}: {e}", file=sys.stderr)
    return downloaded_files

if __name__ == "__main__":
    links = sys.argv[1:]
    downloaded_files = download_webpages(links)
    print('\n'.join(downloaded_files))