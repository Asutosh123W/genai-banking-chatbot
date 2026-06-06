from services.llm_service import (
    generate_simple_response
)

from services.vector_store import (
    get_documents,
    get_collection
)

# =========================
# SKILL DATABASE
# =========================

KNOWN_SKILLS = [

    "python",
    "java",
    "c++",
    "javascript",
    "react",
    "react native",
    "unity",
    "firebase",
    "api",
    "rest api",
    "json",
    "git",
    "prompt engineering",
    "generative ai",
    "chatgpt",
    "openai api",
    "langchain",
    "llamaindex",
    "nlp",
    "embeddings",
    "transformers",
    "vector database",
    "chromadb",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch"

]


# ======================================
# DOCUMENT COMPARISON TOOL
# ======================================

def compare_documents(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    document_chunks = {}

    for document, metadata in zip(
        data.get("documents", []),
        data.get("metadatas", [])
    ):

        if not metadata:
            continue

        if (
            metadata.get("user_id")
            != user_id
        ):
            continue

        source = metadata.get(
            "source",
            "Unknown"
        )

        if source not in document_chunks:

            document_chunks[source] = []

        document_chunks[source].append(
            document
        )

    if len(document_chunks) < 2:

        return (
            "Need at least two uploaded "
            "documents to compare."
        )

    comparison_text = ""

    for source, chunks in (
        document_chunks.items()
    ):

        comparison_text += (
            f"\n\nDocument: {source}\n"
        )

        comparison_text += (
            " ".join(chunks[:3])
        )

    prompt = f"""
Compare these uploaded documents.

Provide:

1. Main purpose of each document

2. Important similarities

3. Important differences

4. Skills mentioned

5. Key information

6. Final comparison summary

Documents:

{comparison_text}
"""

    return generate_simple_response(
        prompt
    )

def extract_skills_from_documents(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    combined_text = ""

    for document, metadata in zip(
        data["documents"],
        data["metadatas"]
    ):

        if (
            metadata.get("user_id")
            != user_id
        ):
            continue

        combined_text += (
            document.lower()
            + "\n"
        )

    found_skills = []

    for skill in KNOWN_SKILLS:

        if skill.lower() in combined_text:

            found_skills.append(
                skill.lower()
            )

    return list(
        set(found_skills)
    )

def match_job_requirements(
    user_id,
    collection_name="general"
):

    # =========================
    # EXTRACT USER SKILLS
    # =========================

    candidate_skills = (
        extract_skills_from_documents(
            user_id=user_id,
            collection_name=collection_name
        )
    )

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    combined_text = ""

    # =========================
    # ONLY THIS USER'S DOCS
    # =========================

    for document, metadata in zip(
        data["documents"],
        data["metadatas"]
    ):

        if (
            metadata.get("user_id")
            != user_id
        ):
            continue

        combined_text += (
            document + "\n"
        )

    lower_text = (
        combined_text.lower()
    )

    # =========================
    # JOB SKILL EXTRACTION
    # =========================

    job_skills = []

    for skill in KNOWN_SKILLS:

        if skill in lower_text:

            job_skills.append(
                skill
            )

    candidate_skills = list(
        set(candidate_skills)
    )

    job_skills = list(
        set(job_skills)
    )

    matched_skills = list(

        set(candidate_skills)
        &
        set(job_skills)

    )

    missing_skills = list(

        set(job_skills)
        -
        set(candidate_skills)

    )

    # =========================
    # SCORE CALCULATION
    # =========================

    if len(job_skills) > 0:

        match_score = round(

            (
                len(
                    matched_skills
                )
                /
                len(
                    job_skills
                )
            ) * 100,
            2

        )

    else:

        match_score = 0

    # =========================
    # DEBUG LOGS
    # =========================

    print(
        "CANDIDATE SKILLS:",
        candidate_skills
    )

    print(
        "JOB SKILLS:",
        job_skills
    )

    print(
        "MATCHED SKILLS:",
        matched_skills
    )

    print(
        "MISSING SKILLS:",
        missing_skills
    )

    print(
        "MATCH SCORE:",
        match_score
    )

    # =========================
    # LLM EXPLANATION
    # =========================

    prompt = f"""
You are an expert AI recruiter.

IMPORTANT:
Only use the provided skills.
Do not invent skills.
Do not assume missing qualifications.

Match Score:
{match_score}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Provide:

1. Strengths

2. Missing Skills

3. Learning Recommendations

4. Final Recommendation
"""

    explanation = (
        generate_simple_response(
            prompt
        )
    )

    return f"""

Match Score: {match_score}%

Matched Skills:
{', '.join(matched_skills)}

Missing Skills:
{', '.join(missing_skills)}

{explanation}
"""



def synthesize_tool_results(
    user_query,
    tool_outputs
):

    print(
        "REASONING LAYER ACTIVATED"
    )

    combined_output = "\n\n".join(
        tool_outputs
    )

    prompt = f"""
You are an intelligent AI analyst.

User Request:
{user_query}

Tool Outputs:
{combined_output}

Your task:

1. Combine all tool outputs.
2. Remove duplicate information.
3. Create a clean structured answer.
4. Highlight important insights.
5. Give a final conclusion.

Return one coherent response.
"""

    return generate_simple_response(
        prompt
    )


# ======================================
# TOOL ROUTER
# ======================================

def generate_document_report(
    user_id,
    collection_name="general"
):

    collection = get_collection(
        collection_name
    )

    data = collection.get()

    document_chunks = {}

    for document, metadata in zip(
        data["documents"],
        data["metadatas"]
    ):

        if (
            metadata.get("user_id")
            != user_id
        ):
            continue

        source = metadata["source"]

        if source not in document_chunks:

            document_chunks[source] = []

        document_chunks[source].append(
            document
        )

    if not document_chunks:

        return (
            "No documents found."
        )

    document_text = ""

    for source, chunks in (
        document_chunks.items()
    ):

        document_text += (
            f"\n\nDocument: {source}\n"
        )

        document_text += (
            " ".join(chunks[:3])
        )

    prompt = f"""
Create a professional report.

Include:

1. Executive Summary

2. Documents Reviewed

3. Main Topics Found

4. Skills Identified

5. Important Findings

6. Recommendations

7. Final Conclusion

Documents:

{document_text}
"""

    return generate_simple_response(
        prompt
    )

def choose_tool(query):

    print(
        "AGENT RECEIVED:",
        query
    )

    query = query.lower().strip()

    # ======================================
    # DOCUMENT SUMMARY
    # ======================================

    if any(
        phrase in query
        for phrase in [

            "summarize",

            "summary",

            "summarise",

            "document summary",

            "summarize document",

            "summarize documents",

            "summarize file",

            "summarize files",

            "give me a summary",

            "brief summary",

            "overview of document",

            "overview of documents"

        ]
    ):

        return "summarize_document"

    # ======================================
    # DOCUMENT COMPARISON
    # ======================================

    if any(
        phrase in query
        for phrase in [

            "compare documents",

            "compare document",

            "compare my documents",

            "compare uploaded documents",

            "compare my uploaded documents",

            "compare all documents",

            "compare the documents",

            "compare files",

            "compare my files",

            "difference between documents",

            "difference between my documents",

            "document comparison",

            "compare"

        ]
    ):

        return "compare_documents"
    
    # =====================
# REPORT GENERATION
# =====================

    if any(
        phrase in query
        for phrase in [

        "generate report",

        "create report",

        "document report",

        "generate document report",

        "report on my documents",

        "create document report",

        "analysis report",

        "generate analysis",

        "generate executive summary",

        "create executive summary"

    ]
):

        return "generate_report"

    # ======================================
    # DOCUMENT LISTING
    # ======================================

    if any(
        phrase in query
        for phrase in [

            "what documents",

            "uploaded documents",

            "uploaded files",

            "my documents",

            "my files",

            "list documents",

            "list files",

            "show documents",

            "show files",

            "files i've uploaded",

            "documents i've uploaded"

        ]
    ):

        return "list_documents"
    
    if any(
        phrase in query
        for phrase in [

        "job match",

        "match score",

        "am i suitable",

        "am i fit",

        "fit for this role",

        "fit for this job",

        "eligible for this job",

        "how well do i match",

        "analyze my profile",

        "candidate match"

    ]
):

        return "job_match"

    # ======================================
    # ANALYTICS
    # ======================================

    if any(
        phrase in query
        for phrase in [

            "analytics",

            "evaluation",

            "accuracy",

            "rag score",

            "faithfulness",

            "relevancy",

            "precision",

            "how accurate"

        ]
    ):

        return "analytics"

    # ======================================
    # DEFAULT RAG
    # ======================================

    return "retrieve_documents"

def plan_tools(query):

    query = query.lower()

    tools = []

    # =====================
    # SUMMARY
    # =====================

    if any(
        phrase in query
        for phrase in [

            "summarize",

            "summary",

            "summarise"
        ]
    ):

        tools.append(
            "summarize_document"
        )

    # =====================
    # COMPARE
    # =====================

    if any(
        phrase in query
        for phrase in [

            "compare",

            "difference",

            "comparison"
        ]
    ):

        tools.append(
            "compare_documents"
        )

    # =====================
    # REPORT
    # =====================

    if any(
        phrase in query
        for phrase in [

            "report",

            "analysis",

            "executive summary"
        ]
    ):

        tools.append(
            "generate_report"
        )

    if any(
        phrase in query
        for phrase in [

        "job match",

        "match score",

        "am i suitable",

        "fit for this role",

        "analyze my profile"

    ]
):

        tools.append(
        "job_match"
    )

    # =====================
    # ANALYTICS
    # =====================

    if any(
        phrase in query
        for phrase in [

            "analytics",

            "accuracy",

            "faithfulness"
        ]
    ):

        tools.append(
            "analytics"
        )

    return tools