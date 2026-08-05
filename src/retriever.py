#logic to retrieve data according to user's query 

from src.embeddings import get_embeddings
from src.config import COLLECTION_NAME
from src.vectorstores import get_qdrant_client

def retrieve_docs(query: str, top_k=5):  # top_k is the number of matching docs to fetch
    # get qdrant client
    client = get_qdrant_client()
    query_vector = get_embeddings([query])[0]  # generate query embedding

    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    print("Retriever module loaded successfully.")
    return [point.payload["text"] for point in search_result.points if point.payload and "text" in point.payload]