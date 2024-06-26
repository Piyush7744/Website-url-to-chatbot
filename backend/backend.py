# backend.py

import os
import requests
import shutil
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.pprint_utils import pprint_response

# Load API keys from environment variables
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

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

def get_navbar_links(soup, base_url):
    navbar_links = []
    navbars = soup.find_all('nav')
    print(f"Found {len(navbars)} navbar elements.")
    for navbar in navbars:
        links = navbar.find_all('a', href=True)
        for link in links:
            absolute_link = get_absolute_url(base_url, link['href'])
            navbar_links.append(absolute_link)
    return navbar_links

def get_all_links(soup, base_url):
    all_links = []
    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} total links.")
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
            print(f"Fetching nested links from: {link}")
            time.sleep(1)  # To avoid overwhelming the server
            nested_links = find_nested_links(link, depth - 1)
            all_links.extend(nested_links)
    
    return all_links

def find_useful_links(url, keywords=[], depth=2):
    content = fetch_page_content(url)
    if content is None:
        return [], []

    soup = BeautifulSoup(content, 'html.parser')
    
    navbar_links = get_navbar_links(soup, url)
    all_links = get_all_links(soup, url)
    
    all_nested_links = []
    for link in all_links:
        if link not in all_nested_links:
            all_nested_links.append(link)
            print(f"Fetching nested links from: {link}")
            time.sleep(1)  # To avoid overwhelming the server
            nested_links = find_nested_links(link, depth - 1)
            all_nested_links.extend(nested_links)
    
    return navbar_links, all_nested_links

def save_links_to_file(navbar_links, all_links, filename):
    with open(filename, 'w') as file:
        file.write("Navbar Links:\n")
        for link in navbar_links:
            file.write(f"{link}\n")
        
        file.write("\nAll Links:\n")
        for link in all_links:
            file.write(f"{link}\n")

def read_links_from_file(filename):
    links = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                links.append(line)
    return links

def ensure_absolute_url(base_url, url):
    if not urlparse(url).scheme:
        return urljoin(base_url, url)
    return url

def download_webpages(links, download_folder):
    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)
    
    os.makedirs(download_folder)
    
    for link in links:
        try:
            content = fetch_page_content(link)
            if content is None:
                print(f"Failed to download {link}: Content type is not 'text/html'")
                continue
            
            filename = os.path.join(download_folder, link.replace('https://', '').replace('/', '_') + '.html')
            
            with open(filename, 'wb') as file:
                file.write(content)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {link}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error occurred while downloading {link}: {e}")
            continue

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

def calculate_query_cost(response, rate_per_token=0.0001):
    """
    Calculate the cost of the query based on the number of tokens in the response.
    :param response: The response from the query engine.
    :param rate_per_token: The cost rate per token.
    :return: The cost of the query.
    """
    num_tokens = len(response.split())
    cost = num_tokens * rate_per_token
    return cost

def run_vector_index(file_path, query):
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

    response = query_engine.query(query)
    cost = calculate_query_cost(response.response)
    
    return response.response, cost
