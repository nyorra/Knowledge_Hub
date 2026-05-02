 # Knowledge Hub

  AI-powered document management system with intelligent question-answering using Retrieval-Augmented Generation (RAG).

  ![Python](https://img.shields.io/badge/Python-3.13-blue)
  ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
  ![React](https://img.shields.io/badge/React-19-61dafb)
  ![Tailwind](https://img.shields.io/badge/Tailwind-4-38bdf8)

  ---

  ## Overview

  Knowledge Hub is a full-stack application that demonstrates modern web development practices and AI integration. The system allows users to manage documents and ask intelligent
  questions based on document content using semantic search and large language models.

  **Key Capabilities:**
  - Document management (upload, create, edit, delete)
  - AI-powered question answering based on document content
  - Semantic search using vector embeddings
  - Conversation history tracking
  - Real-time document indexing

  **Technology Stack:**
  - Backend: Python, FastAPI, LangChain
  - Frontend: React, Vite, Tailwind CSS
  - AI/ML: ChromaDB, sentence-transformers, Llama 3.1

  ---

  ## Features

  ### Current Implementation
  - Modern, responsive UI with drag-and-drop file upload
  - Real-time document indexing with RAG
  - Semantic search across all documents
  - AI-powered question answering
  - Conversation history tracking
  - File preview and editing
  - Toast notifications for user feedback
  - Comprehensive backend logging

  ### Planned Enhancements
  - Voice recording and speech-to-text
  - PDF, DOCX, PPTX support
  - Docker deployment
  - Cloud hosting
  - Dark mode
  - User authentication
  
  ---

  ## Quick Start

  ### Prerequisites

  - Python 3.13+
  - Node.js 18+
  - uv (Python package manager)
  - npm or yarn

  ### Installation

  **1. Clone the repository**
  ```bash
  git clone <repository-url>
  cd Knowledge_Hub
  ```

  **2. Set up environment variables**
  ```bash
  cp .env.example .env
  ```

  **3. Edit .env and add your API keys:**
  ```bash
  CLIENT_URL=http://localhost:5173
  SERVER_URL=http://localhost:8000
  VITE_API_URL=http://localhost:8000
  STORAGE_PATH=./storage
  GROQ_API_KEY=your_openrouter_api_key_here
  ```

  **4. Install backend dependencies**
  ```bash
  cd server
  uv venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  uv pip install -r requirements.txt
  ```

 **5. Install frontend dependencies**
  ```bash
  cd ../client
  npm install
  ```

  ---
  ## Running the Application

  ### Start Backend

  ```bash
  cd server
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

  Backend available at: http://localhost:8000

  ### Start Frontend

  ```bash
  cd client
  npm run dev
  ```

  Frontend available at: http://localhost:5173

  ---
  Usage Guide

  Document Management

  - Upload: Click Upload button or drag-and-drop files
  - Create: Add new text files directly in the app
  - Edit: Modify existing files
  - Preview: Double-click any file to view content
  - Delete: Remove files (also removes from search index)

  Note: Currently supports .txt files only. Additional formats coming soon.

  AI Assistant

  - Switch to AI Assistant tab
  - Type your question about the documents
  - Press Enter to send (Shift+Enter for new line)
  - View conversation history

  ---
  Tech Stack

  Backend

  - FastAPI - Modern Python web framework
  - LangChain - LLM orchestration
  - ChromaDB - Vector database for embeddings
  - sentence-transformers - Local embedding model (all-MiniLM-L6-v2)
  - Pydantic - Data validation
  - uvicorn - ASGI server

  Frontend

  - React 19 - UI library
  - Vite 8 - Build tool
  - Tailwind CSS 4 - Utility-first CSS framework

  AI/ML

  - Llama 3.1 8B - Language model (via OpenRouter)
  - all-MiniLM-L6-v2 - Embedding model (local, CPU)
  - RAG - Retrieval-Augmented Generation pattern

  ---
  Project Structure

  Knowledge_Hub/
  ├── server/                 # Backend (Python/FastAPI)
  │   ├── app/
  │   │   ├── main.py        # API routes
  │   │   ├── core/          # Configuration & schemas
  │   │   └── services/      # Business logic
  │   ├── .venv/             # Virtual environment
  │   └── requirements.txt   # Python dependencies
  ├── client/                # Frontend (React/Vite)
  │   ├── src/
  │   │   ├── App.jsx       # Main component
  │   │   ├── main.jsx      # Entry point
  │   │   └── index.css     # Styles
  │   ├── public/           # Static assets
  │   └── package.json      # Node dependencies
  ├── storage/              # User uploaded files
  ├── chroma_db/            # Vector database storage
  ├── .env                  # Environment variables (gitignored)
  ├── .gitignore
  ├── CLAUDE.md             # Development guidelines
  └── README.md             # This file

  ---
  Configuration

  Backend Settings

  Located in server/app/core/settings.py:
  - STORAGE_PATH - Where uploaded files are stored
  - GROQ_API_KEY - OpenRouter API key for LLM access

  RAG Configuration

  Located in server/app/services/RAG.py:
  - chunk_size: 1000 - Characters per chunk
  - chunk_overlap: 200 - Overlap between chunks
  - top_k: 5 - Number of chunks retrieved per query

  Frontend Settings

  Located in client/vite.config.js:
  - Development server port: 5173
  - API proxy configuration

  ---
  Troubleshooting

  Backend Issues

  Backend won't start
  # Check Python version
  python --version  # Should be 3.13+

  # Reinstall dependencies
  cd server
  uv pip install -r requirements.txt --force-reinstall

  ChromaDB errors
  # Delete and recreate vector database
  rm -rf chroma_db/
  # Restart backend - it will reingest all files

  Frontend Issues

  Frontend won't start
  # Clear cache and reinstall
  cd client
  rm -rf node_modules package-lock.json
  npm install

  Data Issues

  Files not appearing in search
  - Verify files are .txt format
  - Check files are not empty (0 bytes)
  - Review backend logs for ingestion errors
  - Restart backend to force re-ingestion

  ---
  Performance Metrics

  - File ingestion: 100-500ms per file
  - Query retrieval: 100-200ms
  - LLM response: 2-5 seconds (depends on OpenRouter)
  - Capacity: Tested with hundreds of documents
  - Vector DB size: ~1-5MB per 100 documents

  ---
  Security Considerations

  Current Implementation:
  - Designed for local use only
  - No authentication implemented
  - API keys stored in .env (gitignored)
  - CORS restricted to localhost:5173
  - File uploads not validated

  Production Recommendations:
  - Implement user authentication
  - Add file validation and sanitization
  - Use environment-specific configurations
  - Set up HTTPS
  - Implement rate limiting
  - Add input validation and sanitization

  ---
  Development Roadmap

  Phase 1: File Support

  - PDF support
  - DOCX support
  - PPTX support
  - Markdown support
  - File size validation

  Phase 2: Voice Features

  - Voice recording in browser
  - Speech-to-text integration (Whisper)
  - Text-to-speech responses

  Phase 3: Deployment

  - Docker containerization
  - Docker Compose setup
  - Cloud deployment guide
  - Production logging and monitoring

  Phase 4: Enhancements

  - User authentication
  - Multi-user support
  - Dark mode
  - Export conversations
  - Advanced search filters
  - File metadata display

  ---
  License

  All Rights Reserved

  This project is a portfolio demonstration and is provided for educational and showcase purposes only.

  Restrictions:
  - No commercial use permitted
  - No redistribution without explicit permission
  - No modification for commercial purposes
  - Viewing and learning from the code is encouraged

  Purpose:
  This project demonstrates technical skills in:
  - Full-stack web development
  - AI/ML integration
  - Modern Python and JavaScript frameworks
  - System architecture and design

  For inquiries about usage or collaboration, please contact the repository owner.

  ---
  Acknowledgments

  Technologies:
  - LangChain - LLM orchestration framework
  - ChromaDB - Vector database
  - OpenRouter - LLM API access
  - Hugging Face - Embedding models

  ---
  Contact

  For questions, feedback, or collaboration inquiries, please open an issue on GitHub.

  ---
  Last Updated: 2026-05-02

  ---