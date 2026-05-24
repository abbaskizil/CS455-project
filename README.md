# CodeSage 🧠

**RAG-Based Legacy Code Understanding and Explanation Tool**

CodeSage lets you ask natural language questions about any GitHub repository and get grounded, cited answers referencing specific functions and line numbers. All indexing and retrieval run locally — your code never leaves your machine.

---

## Features

- **Multi-language support** — Python, C++, C, Java, JavaScript, TypeScript, Go, Jupyter Notebooks
- **AST-based chunking** — function-level parsing via Tree-sitter, not line-based splitting
- **Two-stage retrieval** — bi-encoder dense retrieval + cross-encoder reranking
- **Conversation history** — follow-up questions reference prior turns
- **Citations** — every answer cites the file name, function name, and line numbers
- **Local-first** — code stays on your machine; only the query and context go to the LLM API

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/omuremreyildiz03/CS455-project
cd CS455-project
```

### 2. Create and activate the environment

```bash
conda create -n lce-venv python=3.11
conda activate lce-venv
pip install -r requirements.txt
```

### 3. Set your API key

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key at [console.anthropic.com](https://console.anthropic.com).

---

## Running the App

### Step 1 — Start the backend

```bash
conda activate lce-venv
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`.

### Step 2 — Open the frontend

Open `index.html` in your browser using VS Code Live Server, or simply open the file directly:

```
File → Open File → index.html
```

---

## Usage

1. Paste a GitHub repository URL into the input field (e.g. `https://github.com/user/repo`)
2. Click **Index** — the repo will be cloned, parsed, embedded, and indexed into ChromaDB
3. Ask questions about the codebase in the chat panel
4. Each answer includes citations showing which file and function the answer came from

**Example questions:**
- *How is authentication handled in this project?*
- *Is there a function that clears the cart?*
- *How is the database session managed?*
- *Where is the payment logic implemented?*

---

## Project Structure

```
CS455-project/
├── api.py          # FastAPI backend (endpoints, pipeline orchestration)
├── chunker.py      # Tree-sitter AST-based code chunking
├── indexer.py      # Embedding and ChromaDB indexing
├── retriever.py    # Bi-encoder retrieval + cross-encoder reranking
├── generator.py    # Prompt construction and LLM generation
├── eval.py         # Evaluation script (BERTScore + manual scoring)
├── index.html      # Web UI
├── style.css       # UI styles
├── app.js          # UI logic
├── .env.example    # API key template
└── requirements.txt
```

---

## Notes

- Indexing large repositories (1000+ functions) may take a few minutes
- A new index replaces the previous one — re-index to switch repositories
- The `chroma_db/` folder stores the vector index on disk and persists across restarts
- Add `current_repo.txt` and `chroma_db/` to `.gitignore` to avoid committing index data

---

## Requirements

- Python 3.11
- Conda
- Anthropic API key
- VS Code with Live Server extension (optional, for frontend)
