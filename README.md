# AI RAG Full-Stack Dashboard 🚀

A high-performance, modular Retrieval-Augmented Generation (RAG) system built with **FastAPI** and **React**. This project features a multi-strategy document ingestion pipeline, a stateful conversational agent with Redis-backed memory, and an automated interview booking system—all presented through a premium, responsive glassmorphism dashboard.

---

## ✨ Features

### 1. Document Ingestion API

- **Dynamic File Processing:** Support for `.pdf` and `.txt` files using `PyMuPDF`.
- **Selectable Chunking:**
  - `RecursiveCharacterSplitter`: Best for maintaining semantic context.
  - `SlidingWindowSplitter`: Fixed-size chunks with configurable overlap.
- **Vector Storage:** Integrated with **Qdrant** for lightning-fast similarity search (supports local file-based mode or Docker).
- **Metadata Management:** Structured SQL storage via SQLAlchemy and SQLite.

### 2. Conversational RAG API

- **Custom Agent Logic:** Pure implementation avoiding standard LangChain chains for maximum control over context-injection.
- **Multi-Turn Memory:** Integrated with **Redis** (with local in-memory fallback) to maintain professional, context-aware dialogues.
- **Intelligent Intent Extraction:** Uses **GPT-4o-mini** to detect interview booking requests and extract `name`, `email`, and `timestamp` directly from the chat.

### 3. Premium Frontend UI

- **Modern Design:** Glassmorphism UI with smooth CSS transitions and Framer-inspired animations.
- **Theme Engine:** Full Support for **Dark Mode** and **Light Mode**.
- **Interactive Dashboard:** Unified view for file uploads, real-time chat, and booking status.

---

## 🏗️ Implementation Overview

The project follows clean architecture principles to ensure modularity and scalability:

1.  **API Layer (`app/api/v1`):** FastAPI routers for ingestion and chat logic.
2.  **Service Layer (`app/services`):** Core logic for chunking, vectorization, and RAG prompt engineering.
3.  **Database Layer (`app/db`):** Async session management and structured models for metadata and bookings.
4.  **Frontend Layer (`app/static`):** A high-performance Single-File React SPA served directly by FastAPI.

---

## 🚀 Getting Started (Local Installation)

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/hunter-devil2057/AI-RAG-Dashboard.git
cd AI-RAG-Dashboard
```

### 2. Install Dependencies

It is recommended to use a virtual environment, but you can also install directly:

```bash
pip install -r requirements.txt --break-system-packages
```

### 3. Configure Environment Variables

Copy the template file and add your **OpenAI API Key**:

```bash
cp .env.template .env
```

Open **`.env`** and set:
`OPENAI_API_KEY=your_real_key_here`

### 4. Run the Infrastructure (Optional)

If you have Docker, you can run the full Redis and Qdrant servers:

```bash
docker-compose up -d
```

_Note: If you don't have Docker, the app will automatically switch to **Local Fallback Mode** (using disk-based Qdrant and in-memory session storage)._

### 5. Start the Application

Run the FastAPI server from the root directory:

```bash
python3 -m uvicorn app.main:app --reload
```

### 6. Access the Dashboard

Visit **[http://localhost:8000/](http://localhost:8000/)** in your browser.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3, SQLAlchemy, Pydantic, PyMuPDF.
- **AI/LLM:** OpenAI API (GPT-4o-mini, Text-Embeddings-3).
- **Storage:** Qdrant (Vector Store), Redis (Memory), SQLite (Relational).
- **Frontend:** React, Tailwind CSS, Lucide Icons.

## 🤝 Contribution

Feel free to fork this project and submit pull requests for any features or improvements!
