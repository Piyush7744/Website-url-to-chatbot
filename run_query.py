import sys
import json

def run_query(file_path, query):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    results = []
    for line in text.split('\n'):
        if query.lower() in line.lower():
            results.append(line)

    return results

if __name__ == "__main__":
    file_path = sys.argv[1]
    query = sys.argv[2]
    results = run_query(file_path, query)
    print(json.dumps(results))
