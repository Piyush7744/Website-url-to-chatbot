from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import shutil
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.pprint_utils import pprint_response
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins


# Load environment variables
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Function to get navbar links
def get_navbar_links(soup):
    navbar_links = []
    navbars = soup.find_all('nav')
    for navbar in navbars:
        links = navbar.find_all('a', href=True)
        for link in links:
            navbar_links.append(link['href'])
    return navbar_links

# Function to get information links based on keywords
def get_information_links(soup, keywords):
    information_links = []
    links = soup.find_all('a', href=True)
    for link in links:
        if any(keyword in link.get_text().lower() for keyword in keywords):
            information_links.append(link['href'])
    return information_links

# Function to find useful links on a webpage
def find_useful_links(url, keywords):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        navbar_links = get_navbar_links(soup)
        information_links = get_information_links(soup, keywords)
        return navbar_links, information_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return [], []

# Function to save links to a file
def save_links_to_file(navbar_links, information_links, filename):
    with open(filename, 'w') as file:
        file.write("Navbar Links:\n")
        for link in navbar_links:
            file.write(f"{link}\n")
        file.write("\nInformation Links:\n")
        for link in information_links:
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
    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)
    os.makedirs(download_folder)
    for link in links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            filename = os.path.join(download_folder, link.replace('https://', '').replace('/', '_') + '.html')
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {link}: {e}")

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

# Function to load data from a text file
def load_data_from_txt(file_path, encodings=('utf-8', 'cp1252')):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            return [Document(text=content)]
        except UnicodeDecodeError:
            continue
    raise Exception("Unable to decode the file using specified encodings")

# Initialize the model
file_path = "cleaned_text_output.txt"
documents = load_data_from_txt(file_path)
index = VectorStoreIndex.from_documents(documents, show_progress=True)
retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
postprocessor = SimilarityPostprocessor(similarity_cutoff=0.75)
query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])

@app.route("/")
def home():
    return send_from_directory('', 'index.html')
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query = data.get("query")
    website = data.get("website")
    keywords = data.get("keywords", ['tutorial', 'guide', 'documentation'])  # Default keywords

    try:
        # Step 1: Find useful links
        navbar_links, information_links = find_useful_links(website, keywords)
        save_links_to_file(navbar_links, information_links, 'output.txt')

        # Step 2: Download webpages
        links = read_links_from_file('output.txt')
        download_webpages(links, 'downloaded_webpages')

        # Step 3: Extract text from downloaded webpages
        extract_text_from_html_files('downloaded_webpages', 'cleaned_text_output.txt')

        # Step 4: Query the model (check for empty file before querying)
        if os.path.getsize('cleaned_text_output.txt') > 0:
            response = query_engine.query(query)
            result = response.response  # Get the response text
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Failed to extract text from downloaded webpages."})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal server error."})

if __name__ == "__main__":
    app.run(debug=True)
