import os
import requests
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine

# Load environment variables
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Streamlit app setup
st.title("Webpage Information Extractor")

# Function to get all links on a webpage
def get_all_links(soup):
    all_links = []
    links = soup.find_all('a', href=True)
    for link in links:
        all_links.append(link['href'])
    return all_links

# Function to fetch page content
def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL {url}: {e}")
        return None

# Function to find nested links
def find_nested_links(url, depth=2):
    if depth == 0:
        return []

    content = fetch_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    links = get_all_links(soup)
    
    all_links = []
    for link in links:
        absolute_link = requests.compat.urljoin(url, link)
        all_links.append(absolute_link)
        time.sleep(1)  # To avoid overwhelming the server
        nested_links = find_nested_links(absolute_link, depth - 1)
        all_links.extend(nested_links)
    
    return all_links

# Function to find all links on a webpage and its nested links
def find_useful_links(url, depth=2):
    content = fetch_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    all_links = get_all_links(soup)
    
    all_nested_links = []
    for link in all_links:
        absolute_link = requests.compat.urljoin(url, link)
        all_nested_links.append(absolute_link)
        time.sleep(1)  # To avoid overwhelming the server
        nested_links = find_nested_links(absolute_link, depth - 1)
        all_nested_links.extend(nested_links)
    
    return all_nested_links

# Function to save links to a file
def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

# Function to read links from a file
def read_links_from_file(filename):
    links = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                links.append(line)
    return links

# Function to download webpages
def download_webpages(links, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    for link in links:
        filename = os.path.join(download_folder, link.replace('https://', '').replace('/', '_') + '.html')
        if not os.path.exists(filename):
            try:
                response = requests.get(link)
                response.raise_for_status()
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                st.write(f"Downloaded: {filename}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to download {link}: {e}")

# Function to extract text from HTML files
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

# Modified Function to Load Data from a Text File
def load_data_from_txt(file_path, encodings=('utf-8', 'cp1252')):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            if content.strip() == "":
                raise ValueError("File content is empty")
            return [Document(text=content)]
        except UnicodeDecodeError:
            continue
    raise Exception("Unable to decode the file using specified encodings")

# Initialize the model with additional debug prints and checks
file_path = "cleaned_text_output.txt"
try:
    documents = load_data_from_txt(file_path)
    if not documents:
        raise ValueError("No documents loaded")
    for doc in documents:
        if not doc.text.strip():
            raise ValueError("Document content is empty")
    st.write("Documents loaded successfully")

    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.75)
    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])
except Exception as e:
    st.error(f"Error initializing the model: {e}")

# Streamlit UI
website = st.text_input("Enter the website URL")
query = st.text_input("Enter your query")

if st.button("Fetch and Query"):
    if website and query:
        try:
            st.write("Processing...")

            # Step 1: Find useful links
            all_links = find_useful_links(website)
            save_links_to_file(all_links, 'output.txt')

            # Step 2: Download webpages
            links = read_links_from_file('output.txt')
            download_webpages(links, 'downloaded_webpages')

            # Step 3: Extract text from downloaded webpages
            extract_text_from_html_files('downloaded_webpages', 'cleaned_text_output.txt')

            # Step 4: Query the model (check for empty file before querying)
            if os.path.getsize('cleaned_text_output.txt') > 0:
                response = query_engine.query(query)
                result = response.response  # Get the response text
                st.write(f"Result: {result}")
            else:
                st.error("Failed to extract text from downloaded webpages.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter both website URL and query.")
