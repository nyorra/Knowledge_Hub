# Knowledge Hub

AI-powered document management system with intelligent question-answering using Retrieval-Augmented Generation
(RAG).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![React](https://img.shields.io/badge/React-19-61dafb)
![Tailwind](https://img.shields.io/badge/Tailwind-4-38bdf8)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

---

## Overview

Knowledge Hub is a full-stack RAG application that demonstrates modern web development practices and AI
integration. The system allows users to manage documents, ask intelligent questions based on document content
using semantic search and large language models, and interact via voice input.

**Key Capabilities:**
- Document management (upload, create, edit, delete)
- Multi-format document parsing (PDF, DOCX, TXT, Markdown)
- AI-powered question answering based on document content
- Voice recording with speech-to-text transcription
- Semantic search using vector embeddings
- Conversation history tracking
- Real-time document indexing
- Docker deployment ready

**Technology Stack:**
- Backend: Python 3.13, FastAPI, LangChain, ChromaDB
- Frontend: React 19, Vite 8, Tailwind CSS 4
- AI/ML: sentence-transformers, Llama 3.1 (OpenRouter), Whisper (Groq)
- Deployment: Docker, Docker Compose, Nginx

---

## Features

### Document Management
- **Multi-format Support**: PDF, DOCX, TXT, Markdown
- **Drag & Drop Upload**: Modern file upload interface
- **Encoding Detection**: Automatic detection of UTF-8, Windows-1251, ISO-8859-1
- **Language Detection**: Identifies document language (en, ru, zh, etc.)
- **Real-time Indexing**: Automatic RAG ingestion on upload/edit
- **File Operations**: Create, edit, preview, delete with toast notifications

### AI Assistant
- **RAG-powered Q&A**: Answers based on uploaded documents
- **Semantic Search**: ChromaDB vector similarity search
- **Context-aware**: Retrieves top-5 relevant chunks per query
- **Conversation History**: Tracks all Q&A interactions
- **LLM Integration**: Llama 3.1 8B via OpenRouter API

### Voice Features
- **Browser Recording**: Native MediaRecorder API
- **Speech-to-Text**: Whisper transcription via Groq API
- **Audio Format**: WebM with Opus codec
- **Seamless Integration**: Voice input → transcription → AI response

### Technical Features
- **Async Operations**: Non-blocking file processing with asyncio
- **Background Ingestion**: Fast startup with background file indexing
- **Persistent Storage**: ChromaDB vector store, filesystem storage
- **Comprehensive Logging**: Timestamped logs for all operations
- **CORS Configuration**: Secure cross-origin requests
- **Error Handling**: Graceful failures with user feedback

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- uv (Python package manager)
- npm
- Docker & Docker Compose (for deployment)

### Local Development

**1. Clone the repository**
```bash
git clone <https://github.com/nyorra/Knowledge_Hub.git>
cd Knowledge_Hub
```

**2. Set up environment variables**
```bash
cp .env.example .env
```

**3. Edit .env and add your API keys:**
```env
CLIENT_URL=http://localhost:5173
SERVER_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000
STORAGE_PATH=D:\.PROJECTS\Knowledge_Hub\storage

OPENROUTER_API_KEY=sk-or-v1-your_key_here
GROQ_API_KEY=gsk_your_key_here
```

**4. Start Backend**
```bash
cd server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**5. Start Frontend**
```bash
cd client
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Build and Run

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean restart (removes volumes)
docker-compose down -v
```

### Production Configuration

**1. Create .env.production:**
```env
OPENROUTER_API_KEY=sk-or-v1-your_production_key
GROQ_API_KEY=gsk_your_production_key
```

**2. Update docker-compose.yml ports for your server**

**3. Deploy:**
```bash
docker-compose --env-file .env.production up -d --build
```

**Access:**
- Frontend: http://your-server-ip:3000
- Backend API: http://your-server-ip:8000
- API Docs: http://your-server-ip:8000/docs

---

## Usage Guide

### Document Management

- **Upload**: Click Upload button or drag-and-drop files
- **Create**: Add new text files directly in the app
- **Edit**: Modify existing files (re-indexes automatically)
- **Preview**: Double-click any file to view content
- **Delete**: Remove files (also removes from vector store)

**Supported Formats:**
- `.txt` - Plain text with encoding detection
- `.md`, `.markdown` - Markdown files
- `.pdf` - PDF documents (pypdf + pdfplumber fallback)
- `.docx` - Microsoft Word documents

### AI Assistant

- Switch to **AI Assistant** tab
- Type your question about the documents
- Press **Enter** to send (Shift+Enter for new line)
- View conversation history with sources

### Voice Input

- Click **microphone icon** to start recording
- Speak your question
- Click **stop** to end recording
- Automatic transcription → AI processes question → response

---

## Tech Stack

### Backend

- **FastAPI** - Modern async Python web framework
- **LangChain** - LLM orchestration and RAG pipeline
- **ChromaDB** - Vector database for embeddings (persistent)
- **sentence-transformers** - Local embedding model (all-MiniLM-L6-v2)
- **OpenAI SDK** - Whisper API client
- **Pydantic** - Data validation and settings
- **uvicorn** - ASGI server
- **Document Parsers**: pypdf, python-docx, pdfplumber, chardet, langdetect

### Frontend

- **React 19** - UI library with hooks
- **Vite 8** - Fast build tool and dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **MediaRecorder API** - Browser audio recording

### AI/ML

- **Llama 3.1 8B Instruct** - Language model (via OpenRouter)
- **Whisper Large V3 Turbo** - Speech-to-text (via Groq)
- **all-MiniLM-L6-v2** - Embedding model (384-dim, local CPU)
- **RAG Pattern** - Retrieval-Augmented Generation

### Deployment

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Frontend web server (production)
- **Multi-stage Builds** - Optimized image sizes

---

## Project Structure

```
Knowledge_Hub/
├── server/                     # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── main.py            # API routes & lifespan
│   │   ├── core/
│   │   │   ├── settings.py    # Pydantic settings
│   │   │   ├── schemas.py     # Request/response models
│   │   │   ├── logger.py      # Logging configuration
│   │   │   └── startup.py     # RAG initialization
│   │   └── services/
│   │       ├── assistant.py   # LLM + RAG integration
│   │       ├── storage.py     # File CRUD operations
│   │       ├── RAG.py         # Vector store + ingestion
│   │       ├── transcription.py # Whisper STT service
│   │       ├── document_parser.py # Parsing facade
│   │       └── parsers/       # Format-specific parsers
│   ├── chroma_db/             # ChromaDB persistent storage
│   ├── logs/                  # Application logs
│   ├── pyproject.toml         # Python dependencies (uv)
│   ├── uv.lock                # Locked dependencies
│   ├── Dockerfile             # Backend container
│   └── .dockerignore
├── client/                    # Frontend (React/Vite)
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Tailwind + custom styles
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── Dockerfile            # Frontend container
│   ├── nginx.conf            # Nginx configuration
│   └── .dockerignore
├── storage/                  # User-uploaded files
├── docker-compose.yml        # Multi-container orchestration
├── .env                      # Environment variables (gitignored)
├── .env.production           # Production env vars
├── .gitignore
└── README.md                 # This file
```

---

## Configuration

### Backend Settings

Located in `server/app/core/settings.py`:
- `STORAGE_PATH` - Where uploaded files are stored
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM access
- `GROQ_API_KEY` - Groq API key for Whisper transcription
- `CLIENT_URL` - Frontend URL for CORS
- `SERVER_URL` - Backend URL

### RAG Configuration

Located in `server/app/services/RAG.py`:
- `chunk_size: 1000` - Characters per chunk
- `chunk_overlap: 200` - Overlap between chunks
- `top_k: 5` - Number of chunks retrieved per query
- `embedding_model: all-MiniLM-L6-v2` - Local embedding model
- `collection_name: knowledge_hub` - ChromaDB collection

### Frontend Settings

Located in `client/.env`:
- `VITE_API_URL` - Backend API endpoint

### Docker Configuration

Located in `docker-compose.yml`:
- Backend port: `8000`
- Frontend port: `3000` (nginx serves on 80 internally)
- Persistent volumes: storage, chroma_db, logs
- Network: `knowledge_hub_network` (bridge)

---

## API Endpoints

### AI Assistant

- `POST /ai` - Answer question using RAG + LLM
- `POST /ai/transcribe` - Transcribe audio to text (Whisper)

### File Storage

- `POST /storage/create` - Create text file + ingest
- `PUT /storage/edit` - Update file + re-ingest
- `POST /storage/upload` - Upload binary file + ingest
- `DELETE /storage/delete` - Delete file + remove chunks
- `GET /storage/files` - List all files
- `GET /storage/content` - Read file content

---

## Architecture

### Data Flow

**File Upload:**
```
Client (FormData)
    → POST /storage/upload
    → storage_service.upload_file_from_pc() [binary write]
    → rag_service.ingest_files() [async]
    → document_parser_service.parse_file() [in thread pool]
    → text_splitter.split_text() [in thread pool]
    → vector_store.add_texts() [in thread pool]
    → Response: {status: "success", filename: "..."}
```

**Question Answering:**
```
Client (question)
    → POST /ai
    → assistant_service.answer_question() [async]
    → rag_service.retrieve(question, top_k=5) [async]
        → vector_store.similarity_search() [in thread pool]
    → Build context from chunks
    → llm.ainvoke([system_prompt, question]) [async]
    → Response: {status: "success", answer: "..."}
```

**Voice Transcription:**
```
Client (audio recording)
    → POST /ai/transcribe
    → transcription_service.transcribe_audio() [async]
    → Save to temp file [in thread pool]
    → Groq Whisper API call [in thread pool]
    → Delete temp file
    → Response: {status: "success", text: "..."}
```

### Key Design Decisions

**Async RAG Operations:**
- Problem: Parsing large PDFs blocks FastAPI event loop
- Solution: Wrap blocking operations in `asyncio.to_thread()`
- Result: Server stays responsive during file processing

**Background Startup Ingestion:**
- Problem: Ingesting 100+ files on startup delays server readiness
- Solution: Start ingestion in background task, return immediately
- Result: Server starts in <5 seconds regardless of file count

**Remove Old Chunks Before Re-ingestion:**
- Problem: Editing a file leaves old chunks in vector store
- Solution: Delete chunks by source filename before adding new ones
- Result: No stale data, accurate retrieval

**Factory Pattern for Parsers:**
- Problem: Need to support multiple file formats
- Solution: Factory selects parser by extension, each format has dedicated class
- Result: Easy to add new formats, clean separation of concerns

---

## Performance Metrics

- **Server Startup**: <5 seconds (background ingestion)
- **File Upload (10MB PDF)**: 2-5 seconds (non-blocking)
- **Document Parsing**: 100-500ms per file
- **RAG Retrieval**: 100-200ms
- **LLM Response**: 2-5 seconds (depends on OpenRouter)
- **Voice Transcription**: 1-3 seconds (depends on audio length)
- **Concurrent Uploads**: Fully supported (async operations)
- **Capacity**: Tested with hundreds of documents
- **Vector DB Size**: ~1-5MB per 100 documents

---

## Troubleshooting

### Backend Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
cd server
uv sync --frozen
```

**ChromaDB errors:**
```bash
# Delete and recreate vector database
rm -rf server/chroma_db/
# Restart backend - it will reingest all files
```

**Transcription fails:**
- Verify `GROQ_API_KEY` is valid (starts with `gsk_`)
- Check Groq API is accessible (may be region-blocked)
- Review logs: `server/logs/*.log`

### Frontend Issues

**Frontend won't start:**
```bash
# Clear cache and reinstall
cd client
rm -rf node_modules package-lock.json
npm install
```

**Voice recording not working:**
- Check browser permissions for microphone
- Ensure HTTPS or localhost (required for MediaRecorder)
- Verify browser supports WebM/Opus codec

### Docker Issues

**Containers won't start:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

**Volume permission errors:**
```bash
# Ensure directories exist and are writable
mkdir -p storage server/chroma_db server/logs
chmod -R 755 storage server/chroma_db server/logs
```

### Data Issues

**Files not appearing in search:**
- Verify file format is supported (PDF, DOCX, TXT, MD)
- Check files are not empty (0 bytes)
- Review backend logs for parsing errors
- Restart backend to force re-ingestion

**Empty AI responses:**
- Verify documents are uploaded and indexed
- Check `OPENROUTER_API_KEY` is valid
- Review logs for LLM errors

---

## Security Considerations

### Current Implementation

- Designed for local/private deployment
- No authentication implemented
- API keys stored in .env (gitignored)
- CORS restricted to configured CLIENT_URL
- File uploads not validated for malicious content

### Production Recommendations

- Implement user authentication (JWT, OAuth)
- Add file validation and sanitization
- Use environment-specific configurations
- Set up HTTPS with SSL certificates
- Implement rate limiting (per-user, per-IP)
- Add input validation and sanitization
- Use secrets management (Vault, AWS Secrets Manager)
- Enable audit logging
- Implement file size limits
- Scan uploads for malware

---

## Known Limitations

1. **Storage Service Encoding**: `get_file_content()` assumes UTF-8, breaks for binary files
2. **No File Size Limits**: Can upload arbitrarily large files
3. **No Duplicate Handling**: Uploading same filename overwrites without warning
4. **Binary File Preview**: Frontend can't preview PDF/DOCX content
5. **No Progress Indicators**: Large uploads show no progress feedback
6. **Metadata Duplication**: Metadata stored per-chunk (wasteful for large documents)
7. **Region Restrictions**: Groq API may be blocked in some regions

---

## Development Roadmap

### Phase 1: Completed ✓
- ✓ Multi-format document support (PDF, DOCX, TXT, MD)
- ✓ Voice recording and speech-to-text
- ✓ Docker containerization
- ✓ Docker Compose setup
- ✓ Production-ready deployment

### Phase 2: Enhancements
- User authentication and authorization
- Multi-user support with isolated storage
- Dark mode UI
- Export conversations (JSON, PDF)
- Advanced search filters
- File metadata display (author, date, size)
- Progress indicators for uploads
- File size validation

### Phase 3: Advanced Features
- Real-time collaboration
- Document versioning
- Folder organization
- Batch operations
- Advanced analytics dashboard
- Custom embedding models
- Multi-language UI
- Mobile app

---

## License

Author: Nyorra @nyorraa
All Rights Reserved

This project is a portfolio demonstration and is provided for educational and showcase purposes only.

**Restrictions:**
- No commercial use permitted
- No redistribution without explicit permission
- No modification for commercial purposes
- Viewing and learning from the code is encouraged

**Purpose:**
This project demonstrates technical skills in:
- Full-stack web development
- AI/ML integration (RAG, embeddings, LLMs)
- Modern Python and JavaScript frameworks
- System architecture and design
- Docker containerization and deployment
- Async programming patterns
- API design and integration

For inquiries about usage or collaboration, please contact the repository owner.

---

## Acknowledgments

**Technologies:**
- [LangChain](https://langchain.com) - LLM orchestration framework
- [ChromaDB](https://www.trychroma.com) - Vector database
- [OpenRouter](https://openrouter.ai) - LLM API access

---

## Acknowledgments

**Technologies:**
- [LangChain](https://langchain.com) - LLM orchestration framework
- [ChromaDB](https://www.trychroma.com) - Vector database
- [OpenRouter](https://openrouter.ai) - LLM API access
- [Groq](https://groq.com) - Fast Whisper inference
- [Hugging Face](https://huggingface.co) - Embedding models
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [React](https://react.dev) - UI library
- [Tailwind CSS](https://tailwindcss.com) - CSS framework

---

## Contact

Telegram: @nyorraa
For questions, feedback, or collaboration inquiries, please open an issue on GitHub.

---


**Last Updated:** 2026-05-09