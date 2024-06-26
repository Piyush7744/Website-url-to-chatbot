import streamlit as st
import os
from backend import run_vector_index

def load_token(file_path="token.txt"):
    """Load the token from a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return None

def main():
    st.title("Query Interface")

    token = load_token()

    url = st.text_input("Enter Website URL", "")
    query = st.text_input("Enter Query", "")
    input_token = st.text_input("Enter your access token", type="password")

    if st.button("Run Query"):
        if url and query and input_token:
            if input_token == token:
                try:
                    domain = url.split("//")[-1].split("/")[0]
                    file_path = f"{domain}_cleaned_text.txt"
                    
                    response, cost = run_vector_index(file_path, query)
                    st.write("Response:")
                    st.write(response)
                    st.write(f"Cost of the query: ${cost:.4f}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Invalid token")
        else:
            st.error("Please enter website URL, query, and token")

if __name__ == "__main__":
    main()
