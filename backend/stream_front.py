import streamlit as st
import requests

# Streamlit UI
st.title("Chatbot")

# Input fields for the website and query
website = st.text_input("Enter the website URL:")
query = st.text_area("Enter your query:")

# Button to submit the form
if st.button("Submit"):
    if website and query:
        # Send a POST request to the Flask server
        api_url = "http://localhost:5000/query"  # Ensure this is the correct URL for your Flask server
        payload = {
            "website": website,
            "query": query,
            "keywords": ['tutorial', 'guide', 'documentation']  # Default keywords
        }
        try:
            with st.spinner('Processing...'):
                response = requests.post(api_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        st.success("Query Result:")
                        st.write(data['result'])
                    else:
                        st.error("Error: " + data.get('error', 'Unknown error occurred'))
                else:
                    st.error(f"Request failed with status code {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter both the website URL and your query.")
