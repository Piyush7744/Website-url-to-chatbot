# backend/scraper.py
import sys
from backend import find_useful_links, save_links_to_file, read_links_from_file, download_webpages, extract_text_from_html_files, generate_token

if __name__ == "__main__":
    url = sys.argv[1]
    keywords = ["application", "tutorial"]
    depth = 2

    # Step 1: Fetch Links
    navbar_links, information_links = find_useful_links(url, keywords, depth)
    
    domain = url.split("//")[-1].split("/")[0]
    output_file = f"{domain}_links.txt"
    save_links_to_file(navbar_links, information_links, output_file)

    # Step 2: Download Webpages
    download_folder = f"{domain}_webpages"
    links = read_links_from_file(output_file)
    download_webpages(links, download_folder)

    # Step 3: Extract Text
    input_directory = download_folder
    output_file_path = f"{domain}_cleaned_text.txt"
    extract_text_from_html_files(input_directory, output_file_path)

    token = generate_token()
    api_url = f"http://localhost:8000/api/{token}"

    # Generate HTML snippet with only query field
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Query Interface</title>
        <script>
            async function runQuery() {{
                const query = document.getElementById('query').value;
                const url = '{url}';
                const token = '{token}';

                if (query) {{
                    try {{
                        const domain = new URL(url).hostname;
                        const filePath = `{domain}_cleaned_text.txt`; // Placeholder for actual file path

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
                    document.getElementById('output').innerText = 'Please enter a query';
                }}
            }}
        </script>
    </head>
    <body>
        <h1>Query Interface</h1>
        <div>
            <label for="query">Enter Query:</label>
            <input type="text" id="query" name="query">
        </div>
        <button onclick="runQuery()">Run Query</button>
        <pre id="output"></pre>
    </body>
    </html>
    """
    print(html_code)
