# PharmaGuide-RAG

PharmaGuide-RAG is a drug-label question-answering application. It retrieves passages from the included processed DailyMed label data and uses OpenAI to generate answers grounded in those passages. It is an informational tool, not a substitute for professional medical advice.

## Project contents

- `src/` — data-processing scripts, vector-store builder, and FastAPI application
- `frontend/` — browser-based question interface
- `data/cleaned/` and `data/processed/` — source and processed label data, including the chunks used to build the vector store
- `evaluation/` — evaluation questions
- `requirements.txt` — Python dependencies

## Setup

Use Python 3.10 or newer. From the project root, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local `.env` file from the example and add your own OpenAI API key. Never commit `.env` or share its contents:

```powershell
Copy-Item .env.example .env
```

Edit `.env` so `OPENAI_API_KEY` contains your key. The `.env` file is excluded by `.gitignore`.

## Rebuild the vector database

The generated `chroma_db/` directory is intentionally excluded from GitHub. Rebuild it from the included data whenever needed, from the project root:

```powershell
python -m src.chunk_documents
python -m src.build_vectorstore
```

The first command regenerates `data/processed/chunks.json` from `data/cleaned/`. The second creates the local Chroma database in `chroma_db/`; it also downloads the configured sentence-transformers embedding model on first use. The processed data is kept in the repository so the database can be rebuilt without downloading the source label files again.

## Run the application

After rebuilding the vector database and configuring `.env`, start the API:

```powershell
python -m uvicorn src.api:app --reload
```

In another terminal, serve the frontend:

```powershell
python -m http.server 5500 --directory frontend
```

Open <http://127.0.0.1:5500>. The API is available at <http://127.0.0.1:8000>, with interactive API documentation at <http://127.0.0.1:8000/docs>.