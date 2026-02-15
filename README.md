# knowledge-agent

A beginner-friendly local RAG (retrieval-augmented generation) app with a **Gradio UI**.

## Features

- Ingest knowledge from:
  - Website URLs
  - YouTube URLs (via `youtube-transcript-api`)
  - Uploaded files: PDF, DOCX, TXT
- Chunk content with a simple overlapping token strategy (~1000 tokens with overlap)
- Create embeddings with OpenAI
- Persist vectors locally in ChromaDB at `app/storage`
- Ask questions and get answers with citations
- View ingested source list
- Clear the local vector database

## Project structure

```text
app/
  loaders/
    web.py
    youtube.py
    pdf.py
    docx.py
  storage/                  # ChromaDB persisted files
  gradio_app.py
scripts/
  bootstrap.sh              # setup helper (online/proxy/offline)
  create_wheelhouse.sh      # offline wheel download helper
.env.example
requirements.txt
README.md
```

## Quick setup (recommended)

```bash
scripts/bootstrap.sh
cp .env.example .env
# add OPENAI_API_KEY in .env
python app/gradio_app.py
```

Then open `http://127.0.0.1:7860`.

## Manual setup

1. **Create and activate a Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set:

   - `OPENAI_API_KEY`
   - optional: `OPENAI_CHAT_MODEL`
   - optional: `OPENAI_EMBEDDING_MODEL`

4. **Run locally**

   ```bash
   python app/gradio_app.py
   ```

## Missing dependency troubleshooting

If you see errors like `ModuleNotFoundError: No module named 'chromadb'`, your environment did not install dependencies successfully.

### A) Proxy-based environments

```bash
scripts/bootstrap.sh --proxy http://<proxy-host>:<port>
```

You can also specify a custom package index:

```bash
scripts/bootstrap.sh --index-url https://pypi.org/simple
```

### B) Offline / restricted environments

On a machine with internet access:

```bash
scripts/create_wheelhouse.sh wheelhouse
```

Copy `wheelhouse/` into the target environment, then run:

```bash
scripts/bootstrap.sh --wheelhouse wheelhouse
```

## Run on GitHub (Codespaces)

1. Open the repo in a new Codespace.
2. Run `scripts/bootstrap.sh`.
3. Add `.env` with your OpenAI key.
4. Run `python app/gradio_app.py`.
5. Use the forwarded port **7860** from the Codespaces "Ports" tab.

## Usage

1. Ingest one or more sources.
2. Verify sources in the "Knowledge base" section.
3. Ask a question.
4. Review answer + citations.
5. Use **Clear database** to reset everything.


## GitHub Actions

Yes — once this PR is merged, GitHub Actions can run CI automatically on pushes/PRs using `.github/workflows/ci.yml`.

Current CI checks:

- install dependencies from `requirements.txt`
- validate shell script syntax for setup helpers
- compile all app modules
- run a basic import smoke test

Note: this CI intentionally does **not** call OpenAI APIs, so no `OPENAI_API_KEY` is required for CI to pass.
