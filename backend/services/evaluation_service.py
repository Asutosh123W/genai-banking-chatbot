from sentence_transformers import util

from services.vector_store import (
    embedding_model
)


def calculate_answer_relevancy(
    query,
    answer
):

    query_embedding = (
        embedding_model.encode(
            query,
            convert_to_tensor=True
        )
    )

    answer_embedding = (
        embedding_model.encode(
            answer,
            convert_to_tensor=True
        )
    )

    score = util.cos_sim(
        query_embedding,
        answer_embedding
    )

    return round(
        float(score),
        3
    )

def calculate_faithfulness(
    answer,
    retrieved_chunks
):

    context = " ".join(
        retrieved_chunks
    )

    context_embedding = (
        embedding_model.encode(
            context,
            convert_to_tensor=True
        )
    )

    answer_embedding = (
        embedding_model.encode(
            answer,
            convert_to_tensor=True
        )
    )

    score = util.cos_sim(
        context_embedding,
        answer_embedding
    )

    return round(
        float(score),
        3
    )

def calculate_context_precision(
    query,
    retrieved_chunks
):

    if not retrieved_chunks:
        return 0

    query_embedding = (
        embedding_model.encode(
            query,
            convert_to_tensor=True
        )
    )

    scores = []

    for chunk in retrieved_chunks:

        chunk_embedding = (
            embedding_model.encode(
                chunk,
                convert_to_tensor=True
            )
        )

        similarity = util.cos_sim(
            query_embedding,
            chunk_embedding
        )

        scores.append(
            float(similarity)
        )

    return round(
        sum(scores) /
        len(scores),
        3
    )