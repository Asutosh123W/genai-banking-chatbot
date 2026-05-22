# GenAI Banking Chatbot

An AI-powered Banking Assistant using Retrieval-Augmented Generation (RAG).

## Features

- PDF/TXT document upload
- Semantic search using Vector Database
- RAG-based response generation
- Conversational chatbot memory
- Modern responsive UI
- Ollama + Mistral integration
- FastAPI backend
- React frontend

---

# Tech Stack

## Frontend
- React
- Vite
- CSS

## Backend
- FastAPI
- Python

## AI Stack
- Ollama
- Mistral
- Sentence Transformers
- ChromaDB

---

# Architecture

User Query
↓
Frontend (React)
↓
FastAPI Backend
↓
Embedding Generation
↓
Vector DB Retrieval
↓
Relevant Context
↓
Mistral LLM (Ollama)
↓
Generated Response
↓
Frontend Chat UI

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone <repo-link>
```

## 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn main:app --reload
```

## 3. Frontend Setup

```bash
cd frontend/frontend-app
npm install
npm run dev
```

---

# Deployment

Frontend deployed using Vercel.

Backend currently runs locally using Ollama + Mistral.

---

# Screenshots

(Add screenshots here if needed)
