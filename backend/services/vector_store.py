import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(
    path="backend/data/chroma_db"
)

# Create collection
collection = chroma_client.get_or_create_collection(
    name="banking_documents"
)


def create_embedding(text):

    embedding = embedding_model.encode(text)

    return embedding.tolist()


def store_chunks(chunks, filename):

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.add(
            ids=[f"{filename}_{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": filename}]
        )


def retrieve_relevant_chunks(query, top_k=3):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results["documents"][0]