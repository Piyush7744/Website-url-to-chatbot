import os
from bs4 import BeautifulSoup

def extract_text_from_html_files(input_directory, output_file_path):
    # Get a list of all HTML files in the specified directory
    html_files = [f for f in os.listdir(input_directory) if f.endswith('.html')]
    
    all_text = ""
    
    for html_file in html_files:
        input_file_path = os.path.join(input_directory, html_file)
        
        # Open and read the content of each HTML file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove all CSS <style> tags
        for style in soup.find_all('style'):
            style.decompose()
        
        # Get text by removing all HTML tags
        text = soup.get_text(separator='\n')
        
        # Process the text to remove extra whitespace and blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        useful_text = "\n".join(lines)
        
        # Append the cleaned text to the cumulative text
        all_text += useful_text + "\n\n"  # Adding new lines for separation
    
    # Write the cumulative cleaned text to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(all_text)

# Specify the directory containing the downloaded HTML files and the desired output text file
input_directory = 'downloaded_webpages'
output_file_path = 'cleaned_text_output.txt'

# Extract and store useful information from all HTML files in the directory into the output file
extract_text_from_html_files(input_directory, output_file_path)

print(f"Extracted text has been saved to {output_file_path}")
