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

    url = st.text_input("Enter Website URL", "")
    keywords = ["internet of things", "iot", "tutorial", "guide", "documentation"]
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
                    token_file = "token.txt"
                    with open(token_file, "w") as f:
                        f.write(st.session_state.token)
                    st.success("All steps completed successfully! Your access token is: " + st.session_state.token)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please enter a URL")
    else:
        st.write("Scraping and indexing have already been completed. You can now run queries.")

if __name__ == "__main__":
    main()
