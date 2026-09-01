"""
Streamlit UI frontend for the AI Travel Assistant application.
Provides interactive interfaces for users to upload travel guide PDF documents and submit questions.
Communicates with the FastAPI backend server to display generated travel itineraries and answers.
"""
import requests  
import streamlit as st

FASTAPI_URL = "http://localhost:8000"

st.title("AI Travel Itinerary Assistant ")
st.markdown("Ask about any travel destination and get a personalized itinerary!")

#sidebar for file upload
with st.sidebar:
    st.subheader("Upload your travel preferences")
    uploaded_file = st.file_uploader("Choose a file", type="pdf")
    if uploaded_file:
        if st.button("Process Guide"):
            with st.spinner("Processing travel guide..."):
                try:
                    files = {"file": uploaded_file}
                    response = requests.post(f"{FASTAPI_URL}/upload", files=files)
                    if response.status_code == 201:
                        st.success(response.json().get("message", "File processed successfully"))
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
#Main content
st.subheader("❓ Ask Your Question")
query = st.text_input("Enter your travel question :")

if st.button("Ask"):
    if query.strip():
        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{FASTAPI_URL}/ask", json={"query": query})
                if response.status_code == 200:
                    answer = response.json()["response"]
                    st.success("Here’s your travel plan:")
                    st.write(answer)
                else:
                    st.error(response.json().get("detail", "Server error! Try again later."))
            except Exception as e:
                st.error(f"Could not reach the FastAPI server: {e}")
    else:
        st.warning("Please enter a query.")
