# FinIntel AI

Enterprise Knowledge Intelligence Platform powered by Retrieval Augmented Generation (RAG), Vector Search and Conversational AI.

## Features

## Features

- JWT Authentication
- Multi-Session Conversational AI
- Knowledge Base Management
- Document Upload & Processing
- Retrieval Augmented Generation (RAG)
- Semantic Vector Search
- Cross-Encoder Re-ranking
- Analytics Dashboard
- Azure Cloud Deployment
- Vercel Frontend Deployment

---

# Tech Stack

## Frontend
- React
- Vite
- CSS

## Backend
- FastAPI
- Python
- PostgreSQL
- ChromaDB

## AI Stack
- Ollama
- Mistral
- Sentence Transformers
- ChromaDB
- Cross Encoder Reranking
- RAG Pipeline

---

# Architecture

```text
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
```

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

- Azure App Service
- Vercel

---

# Screenshots

(Add screenshots here if needed)
