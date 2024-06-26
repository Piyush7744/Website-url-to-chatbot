import sys
import os
from bs4 import BeautifulSoup

def extract_text(input_directory, output_file_path):
    all_text = []
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.html'):
            file_path = os.path.join(input_directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                all_text.append(soup.get_text())

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("\n\n".join(all_text))

if __name__ == "__main__":
    input_directory = sys.argv[1]
    output_file_path = sys.argv[2]
    extract_text(input_directory, output_file_path)
    print(f"Text extracted to {output_file_path}")
