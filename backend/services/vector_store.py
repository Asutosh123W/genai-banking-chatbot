import chromadb
from sentence_transformers import SentenceTransformer

# Embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# Chroma Client
chroma_client = chromadb.PersistentClient(
    path="backend/data/chroma_db"
)


def get_collection(collection_name="general"):

    collection_map = {
        "hr": "human_resources",
        "finance": "finance_documents",
        "legal": "legal_documents",
        "research": "research_documents",
        "general": "general_documents"
    }

    collection_name = collection_map.get(
        collection_name,
        "general_documents"
    )

    return chroma_client.get_or_create_collection(
        name=collection_name
    )


def create_embedding(text):

    embedding = embedding_model.encode(text)

    return embedding.tolist()


def store_chunks(
    chunks,
    filename,
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.add(
            ids=[f"{filename}_{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[
                {
                    "source": filename,
                    "chunk_id": index,
                    "user_id": user_id
                }
            ]
        )

    print(
        f"Stored {len(chunks)} chunks in collection: {collection_name}"
    )


def retrieve_relevant_chunks(
    query,
    user_id,
    collection_name="general",
    top_k=3
):

    collection = get_collection(
        collection_name
    )

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "user_id": user_id
        }
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    print("QUERY:", query)
    print("USER ID:", user_id)

    return documents, metadatas


def get_documents(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    sources = set()

    for metadata in data.get(
        "metadatas",
        []
    ):

        if (
            metadata
            and metadata.get("user_id")
            == user_id
        ):

            sources.add(
                metadata["source"]
            )

    return list(sources)


def delete_document(
    filename,
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    ids_to_delete = []

    for index, metadata in enumerate(
        data["metadatas"]
    ):

        if (
            metadata
            and metadata.get("source")
            == filename
            and metadata.get("user_id")
            == user_id
        ):

            ids_to_delete.append(
                data["ids"][index]
            )

    if ids_to_delete:

        collection.delete(
            ids=ids_to_delete
        )

    return len(ids_to_delete)


def get_collection_stats(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    total_chunks = 0

    documents = set()

    for metadata in data.get(
        "metadatas",
        []
    ):

        if (
            metadata
            and metadata.get("user_id")
            == user_id
        ):

            total_chunks += 1

            documents.add(
                metadata["source"]
            )

    return {
        "total_documents":
            len(documents),
        "total_chunks":
            total_chunks
    }