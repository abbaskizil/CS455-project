# CodeSage 🧠
 
**RAG-based legacy code understanding and explanation tool**
 
CodeSage lets you ask natural-language questions about any GitHub repository. Its answers cite the exact file, function and line numbers they come from. Indexing and retrieval run locally, so your code never leaves your machine; only the question and the retrieved context are sent to the LLM.
 
> Course project for CS455 Large Language Models, Sabancı University (Spring 2026).
 
---
 
## Results
 
We evaluated CodeSage on 3 private repositories, including a ~12K-line Java/React full-stack application. Answers were scored manually on a 1–5 scale and also compared with BERTScore.
 
| Setup | Average manual score (1–5) |
|---|---|
| Claude with **no** retrieved context | 1.70 |
| **CodeSage** (RAG with citations) | **4.77** |
 
Without context, the model gives generic answers that could fit any codebase. With CodeSage's retrieved functions, it answers about the actual code and points to where that code lives.
 
---
 
## How it works
 
```
GitHub URL ──► clone ──► Tree-sitter AST parsing ──► function-level chunks
                                                          │
                                                          ▼
                                      all-MiniLM-L6-v2 embeddings ──► ChromaDB
                                                          │
Question ──► embed ──► top-20 dense retrieval ──► ms-marco-MiniLM-L6-v2 reranking ──► top-5
                                                          │
                                                          ▼
                                  Claude (claude-haiku-4-5) ──► answer with citations
```
 
1. **AST-based chunking:** Tree-sitter splits code into whole functions and methods, keeping class context, instead of fixed-size line windows. Each chunk keeps its file path and line range so answers can be cited.
2. **Two-stage retrieval:** a fast bi-encoder (`sentence-transformers/all-MiniLM-L6-v2`) pulls the 20 most similar functions from ChromaDB. A cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`) then reranks them against the question and keeps the best 5.
3. **Grounded generation:** the top functions, with their file names and line ranges, go to Claude together with the last 10 messages of the conversation. The model answers only from that context, cites the file and function for each answer, and replies "I do not know" when the context doesn't contain the answer.
---
 
## Team and my contributions
 
This was a team project. **I designed and implemented the two-stage retrieval pipeline** (`retriever.py` and the embedding setup in `indexer.py`): bi-encoder dense retrieval over ChromaDB followed by cross-encoder reranking.
 
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
git clone https://github.com/abbaskizil/CS455-project
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
---
 
## Requirements
 
- Python 3.11
- Conda
- Anthropic API key
- VS Code with Live Server extension (optional, for frontend)
