import os
import requests
import shutil

def read_links_from_file(filename):
    links = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                links.append(line)
    return links

def download_webpages(links, download_folder):
    # Clear the download folder if it exists
    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)
    
    # Create the download folder
    os.makedirs(download_folder)
    
    for link in links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            
            # Extract the filename from the URL or generate one
            filename = os.path.join(download_folder, link.replace('https://', '').replace('/', '_') + '.html')
            
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {link}: {e}")

# Main script
input_file = 'output.txt'
download_folder = 'downloaded_webpages'

# Read links from the file
links = read_links_from_file(input_file)

# Debug print to verify links
print(f"Total links read from file: {len(links)}")

# Download webpages
download_webpages(links, download_folder)

print(f"Webpages have been downloaded to {download_folder}")
