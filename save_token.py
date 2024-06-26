import sys

def save_token(token):
    token_file_path = 'token.txt'
    with open(token_file_path, 'w', encoding='utf-8') as token_file:
        token_file.write(token)
    return token_file_path

if __name__ == "__main__":
    token = sys.argv[1]
    token_file_path = save_token(token)
    print(f"Token saved to {token_file_path}")
