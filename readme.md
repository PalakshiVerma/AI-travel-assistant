AI Travel Assistant

An AI-powered travel assistant that uses Retrieval-Augmented Generation (RAG) to answer travel-related questions using information extracted from uploaded PDF travel guides.

The application combines FastAPI, Streamlit, SentenceTransformers, Qdrant, LangChain, and Large Language Models to build an end-to-end document-based question-answering system.

Running the Application

The application consists of two components:

FastAPI backend
Streamlit frontend

Both need to be running.

Start the FastAPI Backend

From the project root:

uvicorn src.main:app --reload

The API will be available at:

http://localhost:8000

FastAPI automatically provides interactive API documentation at:

http://localhost:8000/docs
Start the Streamlit Frontend

Open another terminal and activate the virtual environment.

Then run:

streamlit run src/app.py

The Streamlit interface will open in your browser.
