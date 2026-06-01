import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


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

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload
        )

        result = response.json()

        print("OLLAMA RESPONSE:")
        print(result)

        ai_response = result.get(
            "response",
            "No response generated"
        )

        return ai_response

    except Exception as error:

        print(
            "ERROR:",
            error
        )

        return (
            "Error generating response "
            "from local LLM."
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

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True
        )

        for line in response.iter_lines():

            if not line:
                continue

            import json

            chunk = json.loads(
                line.decode("utf-8")
            )

            token = chunk.get(
                "response",
                ""
            )

            yield token

    except Exception as error:

        print(
            "STREAM ERROR:",
            error
        )

        yield (
            "Error generating response."
        )