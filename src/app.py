#frontend

#implement frontend for the application

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
                st.success("files uploaded successfully!")
#Main content
st.subheader("Ask about your travel destination")
query = st.text_input("Enter your question here")
if st.button("Ask"):
    if query.strip():
        with st.spinner("Thinking... "):
            st.success("logic will done ")
    else:
        st.warning("Please ask a question ")