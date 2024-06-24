import streamlit as st
import os
import random
import string
from backend import find_useful_links, save_links_to_file, read_links_from_file, download_webpages, extract_text_from_html_files

def generate_token(length=16):
    """Generate a random token."""
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token

def main():
    st.title("Web Scraper and Indexer")

    # Initialize session state variables
    if 'scraping_done' not in st.session_state:
        st.session_state.scraping_done = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'api_url' not in st.session_state:
        st.session_state.api_url = None
    if 'html_snippet' not in st.session_state:
        st.session_state.html_snippet = None

    url = st.text_input("Enter Website URL", "")
    keywords = ["application", "tutorial"]
    depth = 2

    if not st.session_state.scraping_done:
        if st.button("Run Scraper and Indexer"):
            if url:
                try:
                    # Step 1: Fetch Links
                    navbar_links, information_links = find_useful_links(url, keywords, depth)
                    
                    domain = url.split("//")[-1].split("/")[0]
                    output_file = f"{domain}_links.txt"
                    save_links_to_file(navbar_links, information_links, output_file)
                    st.write(f"Links saved to {output_file}")

                    # Step 2: Download Webpages
                    download_folder = f"{domain}_webpages"
                    links = read_links_from_file(output_file)
                    download_webpages(links, download_folder)
                    st.write(f"Webpages downloaded to {download_folder}")

                    # Step 3: Extract Text
                    input_directory = download_folder
                    output_file_path = f"{domain}_cleaned_text.txt"
                    extract_text_from_html_files(input_directory, output_file_path)
                    st.write(f"Extracted text saved to {output_file_path}")

                    st.session_state.scraping_done = True
                    st.session_state.token = generate_token()
                    st.session_state.api_url = f"http://localhost:8000/api/{st.session_state.token}"
                    
                    # Save token to file (for demonstration purposes)
                    token_file = "token.txt"
                    with open(token_file, "w") as f:
                        f.write(st.session_state.token)

                    # Generate HTML snippet
                    html_code = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Query Interface</title>
                        <script>
                            async function runQuery() {{
                                const url = document.getElementById('url').value;
                                const query = document.getElementById('query').value;
                                const inputToken = document.getElementById('token').value;
    
                                // Load the token from a file (simulated here for demonstration)
                                const storedToken = '6Yk1IxWyu0bfl7PW'; // Replace this with the actual token loading mechanism
    
                                if (url && query && inputToken) {{
                                    if (inputToken === storedToken) {{
                                        try {{
                                            const domain = new URL(url).hostname;
                                            const filePath = `${{domain}}_cleaned_text.txt`; // This is just a placeholder for the actual file path
    
                                            const response = await fetch('http://127.0.0.1:8000/api/run-vector-index', {{
                                                method: 'POST',
                                                headers: {{
                                                    'Content-Type': 'application/json'
                                                }},
                                                body: JSON.stringify({{
                                                    file_path: filePath,
                                                    query: query
                                                }})
                                            }});
    
                                            if (!response.ok) {{
                                                throw new Error('Network response was not ok ' + response.statusText);
                                            }}
    
                                            const data = await response.json();
    
                                            // Display the response
                                            document.getElementById('output').innerText = JSON.stringify(data.response, null, 2);
                                        }} catch (error) {{
                                            console.error('An error occurred:', error);
                                            document.getElementById('output').innerText = 'An error occurred: ' + error.message;
                                        }}
                                    }} else {{
                                        document.getElementById('output').innerText = 'Invalid token';
                                    }}
                                }} else {{
                                    document.getElementById('output').innerText = 'Please enter website URL, query, and token';
                                }}
                            }}
                        </script>
                    </head>
                    <body>
                        <h1>Query Interface</h1>
                        <div>
                            <label for="url">Enter Website URL:</label>
                            <input type="text" id="url" name="url">
                        </div>
                        <div>
                            <label for="query">Enter Query:</label>
                            <input type="text" id="query" name="query">
                        </div>
                        <div>
                            <label for="token">Enter your access token:</label>
                            <input type="password" id="token" name="token">
                        </div>
                        <button onclick="runQuery()">Run Query</button>
                        <pre id="output"></pre>
                    </body>
                    </html>
                    """
                    st.session_state.html_snippet = html_code
                    st.success("All steps completed successfully! You can now copy the HTML snippet.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please enter a URL")
    
    if st.session_state.html_snippet is not None:
        st.code(st.session_state.html_snippet, language='html')

if __name__ == "__main__":
    main()
