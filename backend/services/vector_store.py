import chromadb

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

# Embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# Reranker model
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Chroma Client
chroma_client = chromadb.PersistentClient(
    path="backend/data/chroma_db"
)


def get_collection(
    collection_name="general"
):

    collection_map = {
        "hr":
            "human_resources",

        "finance":
            "finance_documents",

        "legal":
            "legal_documents",

        "research":
            "research_documents",

        "general":
            "general_documents"
    }

    collection_name = collection_map.get(
        collection_name,
        "general_documents"
    )

    return (
        chroma_client
        .get_or_create_collection(
            name=collection_name
        )
    )


def create_embedding(text):

    embedding = (
        embedding_model.encode(text)
    )

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

    for index, chunk in enumerate(
        chunks
    ):

        embedding = (
            create_embedding(chunk)
        )

        collection.add(
            ids=[
                f"{filename}_{index}"
            ],

            embeddings=[
                embedding
            ],

            documents=[
                chunk
            ],

            metadatas=[
                {
                    "source":
                        filename,

                    "chunk_id":
                        index,

                    "user_id":
                        user_id
                }
            ]
        )

    print(
        f"Stored {len(chunks)} chunks "
        f"in collection: {collection_name}"
    )


def retrieve_relevant_chunks(
    query,
    user_id,
    collection_name="general",
    top_k=2
):

    collection = get_collection(
        collection_name
    )

    # =========================
    # VECTOR SEARCH
    # =========================

    query_embedding = (
        create_embedding(query)
    )

    vector_results = (
        collection.query(
            query_embeddings=[
                query_embedding
            ],

            n_results=top_k,

            where={
                "user_id":
                    user_id
            },

            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )
    )

    print(
        "VECTOR DISTANCES:"
    )

    print(
        vector_results["distances"]
    )

    vector_documents = (
        vector_results["documents"][0]
    )

    vector_metadatas = (
        vector_results["metadatas"][0]
    )

    # =========================
    # KEYWORD SEARCH
    # =========================

    all_data = collection.get()

    query_words = set(
        query.lower().split()
    )

    keyword_matches = []

    for index, document in enumerate(

        all_data.get(
            "documents",
            []
        )

    ):

        metadata = (
            all_data["metadatas"][
                index
            ]
        )

        if (
            metadata.get(
                "user_id"
            )
            != user_id
        ):

            continue

        document_words = set(
            document.lower().split()
        )

        keyword_score = len(

            query_words.intersection(
                document_words
            )

        )

        if keyword_score > 0:

            keyword_matches.append(
                (
                    keyword_score,
                    document,
                    metadata
                )
            )

    keyword_matches.sort(
        reverse=True,
        key=lambda item:
            item[0]
    )

    keyword_documents = [

        item[1]

        for item in
        keyword_matches[:top_k]

    ]

    keyword_metadatas = [

        item[2]

        for item in
        keyword_matches[:top_k]

    ]

    # =========================
    # HYBRID MERGE
    # =========================

    final_documents = []

    final_metadatas = []

    seen_documents = set()

    # Vector Results First

    for document, metadata in zip(

        vector_documents,
        vector_metadatas

    ):

        if (
            document
            not in seen_documents
        ):

            final_documents.append(
                document
            )

            final_metadatas.append(
                metadata
            )

            seen_documents.add(
                document
            )

    # Keyword Results Second

    for document, metadata in zip(

        keyword_documents,
        keyword_metadatas

    ):

        if (
            document
            not in seen_documents
        ):

            final_documents.append(
                document
            )

            final_metadatas.append(
                metadata
            )

            seen_documents.add(
                document
            )

    print("QUERY:", query)

    print(
    "VECTOR RESULTS:",
    len(vector_documents)
)

    print(
    "KEYWORD RESULTS:",
    len(keyword_documents)
)

    print(
    "FINAL RESULTS:",
    len(final_documents)
)

# =========================
# CROSS ENCODER RERANKING
# =========================

    pairs = []

    for document in final_documents:

        pairs.append(
        [query, document]
    )

    scores = reranker.predict(
    pairs
)

    ranked_results = sorted(
    zip(
        scores,
        final_documents,
        final_metadatas
    ),
    reverse=True
)

    top_results = ranked_results[:2]

    reranked_documents = [
    item[1]
    for item in top_results
]

    reranked_metadatas = [
    item[2]
    for item in top_results
]

    print(
    "RERANKED RESULTS:",
    len(reranked_documents)
)

    print(
    "RERANK SCORES:",
    [float(item[0]) for item in top_results]
)

    return (
    reranked_documents,
    reranked_metadatas
)

def retrieve_multi_query_chunks(
    queries,
    user_id,
    collection_name="general"
):

    all_documents = []
    all_metadatas = []

    for query in queries:

        try:

            documents, metadatas = (
                retrieve_relevant_chunks(
                    query=query,
                    user_id=user_id,
                    collection_name=collection_name
                )
            )

            all_documents.extend(
                documents
            )

            all_metadatas.extend(
                metadatas
            )

        except Exception as error:

            print(
                "MULTI QUERY ERROR:",
                error
            )

    unique_documents = []
    unique_metadatas = []

    seen = set()

    for document, metadata in zip(
        all_documents,
        all_metadatas
    ):

        if document not in seen:

            seen.add(document)

            unique_documents.append(
                document
            )

            unique_metadatas.append(
                metadata
            )

    print(
        "MULTI QUERY RESULTS:",
        len(unique_documents)
    )

    return (
        unique_documents,
        unique_metadatas
    )


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
            and metadata.get(
                "user_id"
            ) == user_id
        ):

            sources.add(
                metadata["source"]
            )

    return list(sources)

def get_document_chunks(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    chunks = []

    for document, metadata in zip(

        data.get(
            "documents",
            []
        ),

        data.get(
            "metadatas",
            []
        )

    ):

        if (
            metadata
            and metadata.get(
                "user_id"
            ) == user_id
        ):

            chunks.append(
                document
            )

    return chunks


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

            and metadata.get(
                "source"
            ) == filename

            and metadata.get(
                "user_id"
            ) == user_id

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
            and metadata.get(
                "user_id"
            ) == user_id
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