from backend.services.vector_store import (
    get_document_chunks
)

from backend.services.llm_service import (
    generate_response
)


def summarize_documents(
    user_id,
    collection_name="general"
):

    documents = get_document_chunks(
        user_id=user_id,
        collection_name=collection_name
    )

    if not documents:

        return (
            "No documents found."
        )

    document_text = "\n".join(
        documents
    )

    prompt = f"""
You are analyzing uploaded documents.

Create a professional report using EXACTLY this structure:

# Uploaded Documents Summary

## Document 1
- Name
- Purpose
- Key Information

## Document 2
- Name
- Purpose
- Key Information

## Key Skills Found
- ...

## Important Dates / Duration
- ...

## Overall Conclusion
- ...

Documents:

{document_text}
"""

    return generate_response(
        prompt,
        [document_text],
        []
    )