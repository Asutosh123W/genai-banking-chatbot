import requests
from backend.services.memory_store import conversation_history

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_response(query, retrieved_chunks):

    # Combine retrieved chunks
    context = "\n\n".join(retrieved_chunks)

    # Build previous conversation memory
    history_text = ""

    for message in conversation_history[-6:]:

        role = message["role"]
        content = message["content"]

        history_text += f"{role}: {content}\n"

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

    # Request payload for Ollama
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

        # Send request to Ollama
        response = requests.post(
            OLLAMA_URL,
            json=payload
        )

        # Convert response to JSON
        result = response.json()

        # DEBUGGING
        print("OLLAMA RESPONSE:")
        print(result)

        # Extract AI response safely
        ai_response = result.get("response", "No response generated")

    except Exception as error:

        print("ERROR:", error)

        ai_response = "Error generating response from local LLM."

    # Store conversation memory
    conversation_history.append({
        "role": "user",
        "content": query
    })

    conversation_history.append({
        "role": "assistant",
        "content": ai_response
    })

    return ai_response

def stream_response(
    query,
    retrieved_chunks
):

    context = "\n\n".join(
        retrieved_chunks
    )

    history_text = ""

    for message in conversation_history[-6:]:

        role = message["role"]
        content = message["content"]

        history_text += (
            f"{role}: {content}\n"
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

        full_response = ""

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

            full_response += token

            yield token

        conversation_history.append({
            "role": "user",
            "content": query
        })

        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

    except Exception as error:

        print(
            "STREAM ERROR:",
            error
        )

        yield (
            "Error generating response."
        )