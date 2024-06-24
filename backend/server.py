from flask import Flask, request, jsonify
import os
import requests
import shutil
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask_cors import CORS
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

def fetch_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': url
    }
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        return response.content
    return None

def get_information_links(soup, keywords):
    information_links = []
    links = soup.find_all('a', href=True)
    for link in links:
        if any(keyword in link.get_text().lower() for keyword in keywords):
            information_links.append(link['href'])
    return information_links

def find_nested_links(url, keywords, depth=2):
    if depth == 0:
        return []

    content = fetch_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    links = get_information_links(soup, keywords)
    
    all_links = []
    for link in links:
        absolute_link = requests.compat.urljoin(url, link)
        all_links.append(absolute_link)
        time.sleep(1)
        nested_links = find_nested_links(absolute_link, keywords, depth - 1)
        all_links.extend(nested_links)
    
    return all_links

def find_useful_links(url, keywords, depth=2):
    content = fetch_page_content(url)
    if content is None:
        return [], []

    soup = BeautifulSoup(content, 'html.parser')
    
    information_links = get_information_links(soup, keywords)
    
    all_information_links = []
    for link in information_links:
        absolute_link = requests.compat.urljoin(url, link)
        all_information_links.append(absolute_link)
        time.sleep(1)
        nested_links = find_nested_links(absolute_link, keywords, depth - 1)
        all_information_links.extend(nested_links)
    
    return all_information_links

def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

def extract_text_from_html_files(input_directory, output_file_path):
    html_files = [f for f in os.listdir(input_directory) if f.endswith('.html')]
    all_text = ""
    for html_file in html_files:
        input_file_path = os.path.join(input_directory, html_file)
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        for style in soup.find_all('style'):
            style.decompose()
        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        useful_text = "\n".join(lines)
        all_text += useful_text + "\n\n"
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(all_text)

def load_data_from_txt(file_path, encodings=('utf-8', 'cp1252')):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            return [Document(text=content)]
        except UnicodeDecodeError:
            continue
    raise Exception("Unable to decode the file using specified encodings")

def run_vector_index(file_path):
    documents = load_data_from_txt(file_path)
    if not documents or all(not doc.text.strip() for doc in documents):
        raise ValueError("Cannot build index from nodes with no content. Please ensure all nodes have content.")
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.75)
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[postprocessor],
    )
    return query_engine

def download_webpages(links, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for link in links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            parsed_url = urlparse(link)
            file_name = os.path.join(download_folder, f"{parsed_url.netloc}_{parsed_url.path.replace('/', '_')}.html")
            with open(file_name, 'wb') as file:
                file.write(response.content)
            time.sleep(1)
        except Exception as e:
            print(f"Failed to download {link}: {e}")

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    keywords = data.get('keywords', [])
    depth = data.get('depth', 2)
    if not url:
        return jsonify({"error": "URL is required"}), 400
    links = find_useful_links(url, keywords, depth)
    download_folder = 'downloads'
    download_webpages(links, download_folder)
    output_file_path = 'extracted_text.txt'
    extract_text_from_html_files(download_folder, output_file_path)
    return jsonify({"message": "Scraping completed", "links": links, "output_file": output_file_path}), 200

if __name__ == '__main__':
    app.run(debug=True)
