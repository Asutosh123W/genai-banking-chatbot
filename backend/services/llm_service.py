import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

def rewrite_query(
    query,
    history_messages
):

    history_text = ""

    for message in history_messages[-4:]:

        history_text += (
            f"{message.sender}: "
            f"{message.content}\n"
        )

    prompt = f"""
You are a search query optimizer.

Rewrite the user's latest question
into a complete standalone search query.

Rules:
- Preserve the exact meaning
- Add missing context from conversation history
- Do NOT broaden the topic
- Do NOT generalize
- Do NOT answer the question
- Output only the rewritten query

Bad Example:
User Question:
What is internship duration?

Bad Rewrite:
Internship duration for various fields and locations

Good Rewrite:
What is the duration of the Generative AI internship?

Conversation:
{history_text}

User Question:
{query}

Rewritten Query:
"""

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload
        )

        result = response.json()

        rewritten_query = result.get(
            "response",
            query
        )

        print(
            "REWRITTEN QUERY:",
            rewritten_query
        )

        return rewritten_query.strip()

    except Exception:

        return query
    
    
def generate_search_queries(
    query
):

    prompt = f"""
You are a retrieval query generator.

Generate exactly 3 short search queries.

Rules:
- Maximum 6 words each
- No numbering
- No bullet points
- No quotes
- No explanations
- Focus on keywords
- Optimize for document retrieval

User Query:
{query}

Search Queries:
"""

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload
        )

        result = response.json()

        text = result.get(
            "response",
            ""
        )

        queries = []

        for line in text.split("\n"):

            line = line.strip()

            if not line:
                continue

            line = line.replace('"', "")

            if line.startswith("1."):
                line = line[2:].strip()

            elif line.startswith("2."):
               line = line[2:].strip()

            elif line.startswith("3."):
               line = line[2:].strip()

            queries.append(line)

        queries = queries[:3]

        print(
            "MULTI QUERIES:"
        )

        print(
            queries
        )

        print(
    "SEARCH QUERIES:"
)

        print(
            queries
)

        return queries

    except Exception:

        return [query]

def generate_response(
    query,
    retrieved_chunks,
    history_messages
):

    # Combine retrieved chunks
    context = "\n\n".join(
        retrieved_chunks
    )

    # Build session conversation history
    history_text = ""

    for message in reversed(
        history_messages
    ):

        history_text += (
            f"{message.sender}: "
            f"{message.content}\n"
        )

    # Final Prompt
    prompt = f"""
You are a professional AI Banking Assistant.

Your responsibilities:
- Answer clearly and professionally
- Use ONLY the retrieved context and previous conversation
- Keep responses concise and accurate
- Do NOT make up information
- If answer is unavailable, say:
  "I could not find relevant information in the uploaded documents."

Guidelines:
- Use short paragraphs
- Use bullet points when helpful
- Avoid repeating the question
- Be conversational but professional
- Keep answers under 120 words whenever possible

Previous Conversation:
{history_text}

Retrieved Context:
{context}

Current User Question:
{query}

Helpful Answer:
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

            {
                "role": "user",
                "content": prompt
            }

        ],

            temperature=0.3

    )

        result = (
            response.choices[0]
            .message
            .content
    )

        print(
        "GROQ RESPONSE:"
    )

        print(result)

        return result

    except Exception as error:

        print(
        "ERROR:",
        error
    )

        return (
        "Error generating response."
    )
    
    # =====================================
# SIMPLE LLM RESPONSE
# =====================================

def generate_simple_response(
    prompt
):

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.3

        )

        result = (
            response.choices[0]
            .message
            .content
        )

        print(
            "GROQ RESPONSE:"
        )

        print(result)

        return result

    except Exception as error:

        print(
            "ERROR:",
            error
        )

        return (
            "Error generating response."
        )


def stream_response(
    query,
    retrieved_chunks,
    history_messages
):

    context = "\n\n".join(
        retrieved_chunks
    )

    history_text = ""

    for message in reversed(
        history_messages
    ):

        history_text += (
            f"{message.sender}: "
            f"{message.content}\n"
        )

    prompt = f"""
You are a professional AI Banking Assistant.

Your responsibilities:
- Answer clearly and professionally
- Use ONLY the retrieved context and previous conversation
- Keep responses concise and accurate
- Do NOT make up information
- If answer is unavailable, say:
  "I could not find relevant information in the uploaded documents."

Guidelines:
- Use short paragraphs
- Use bullet points when helpful
- Avoid repeating the question
- Be conversational but professional
- Keep answers under 120 words whenever possible

Previous Conversation:
{history_text}

Retrieved Context:
{context}

Current User Question:
{query}

Helpful Answer:
"""

    try:

        stream = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.3,

            stream=True

        )

        for chunk in stream:

            content = (
                chunk.choices[0]
                .delta
                .content
            )

            if content:

                yield content

    except Exception as error:

        print(
            "STREAM ERROR:",
            error
        )

        yield (
            "Error generating response."
        )