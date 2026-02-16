"""knowledge-agent Gradio app.

Run locally with:
    python app/gradio_app.py
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Iterable

import chromadb
import gradio as gr
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

from app.loaders.docx import load_docx_text
from app.loaders.pdf import load_pdf_text
from app.loaders.web import load_webpage_text
from app.loaders.youtube import load_youtube_transcript

load_dotenv()

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
STORAGE_DIR = Path("app/storage")
COLLECTION_NAME = "knowledge_agent"
MAX_CHUNK_TOKENS = 1000
CHUNK_OVERLAP_TOKENS = 150


def get_openai_client() -> OpenAI:
    return OpenAI()


def get_chroma_collection(session_id: str):
    """Get or create a collection specific to a user session."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(STORAGE_DIR))
    collection_name = f"knowledge_agent_{session_id}"
    return client.get_or_create_collection(name=collection_name)


def split_text_by_tokens(
    text: str, chunk_size: int = MAX_CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP_TOKENS
) -> list[str]:
    """Split text into overlapping token chunks using a simple sliding window."""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)

    for start in range(0, len(tokens), step):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        if not chunk_tokens:
            continue
        chunk_text = encoding.decode(chunk_tokens).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end >= len(tokens):
            break

    return chunks


def embed_texts(client: OpenAI, texts: Iterable[str], model: str) -> list[list[float]]:
    text_list = list(texts)
    if not text_list:
        return []
    response = client.embeddings.create(model=model, input=text_list)
    return [item.embedding for item in response.data]


def ingest_source_text(session_id: str, source_name: str, source_type: str, text: str) -> int:
    if not text.strip():
        raise ValueError("Loaded content is empty and cannot be ingested.")
    chunks = split_text_by_tokens(text)
    if not chunks:
        raise ValueError("No chunks were created from this source.")
    openai_client = get_openai_client()
    embeddings = embed_texts(openai_client, chunks, EMBEDDING_MODEL)
    collection = get_chroma_collection(session_id)
    existing_count = collection.count()
    ids = [f"doc_{existing_count + idx}" for idx in range(len(chunks))]
    metadatas = [
        {"source": source_name, "source_type": source_type, "chunk_index": idx}
        for idx in range(len(chunks))
    ]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def list_sources(session_id: str) -> list[str]:
    collection = get_chroma_collection(session_id)
    if collection.count() == 0:
        return []
    result = collection.get(include=["metadatas"])
    labels = {
        f"{meta.get('source')} ({meta.get('source_type')})"
        for meta in result.get("metadatas", [])
        if isinstance(meta, dict)
    }
    return sorted(labels)


def clear_database(session_id: str) -> None:
    """Clear only the session-specific collection."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(STORAGE_DIR))
    collection_name = f"knowledge_agent_{session_id}"
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
    client.get_or_create_collection(name=collection_name)


def answer_question(session_id: str, question: str, top_k: int = 4) -> tuple[str, str]:
    collection = get_chroma_collection(session_id)
    if collection.count() == 0:
        raise ValueError("No content has been ingested yet.")
    openai_client = get_openai_client()
    query_embedding = embed_texts(openai_client, [question], EMBEDDING_MODEL)[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return (
            "I couldn't find relevant information in the current knowledge base.",
            "No citations found.",
        )

    context_parts: list[str] = []
    citations: list[str] = []

    for idx, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        source = (
            meta.get("source", "unknown source")
            if isinstance(meta, dict)
            else "unknown source"
        )
        source_type = (
            meta.get("source_type", "unknown") if isinstance(meta, dict) else "unknown"
        )
        citation_label = f"[{idx}] {source} ({source_type})"
        citations.append(citation_label)
        context_parts.append(citation_label + "\n" + doc)

    context_text = "\n\n".join(context_parts)
    prompt = (
        "You are a helpful assistant answering from provided context only. "
        "If answer is missing, say you don't know. "
        "Include bracket citations like [1], [2].\n\n"
        + f"Question:\n{question}\n\n"
        + f"Context:\n{context_text}"
    )

    completion = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer using only provided context and cite sources.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    answer = completion.choices[0].message.content or "No answer returned."
    citation_text = "\n".join(f"- {item}" for item in citations)
    return answer, citation_text


def ingest_website(session_id: str, url: str) -> tuple[str, str]:
    if not url.strip():
        return "Please provide a website URL.", sources_markdown(session_id)
    try:
        text = load_webpage_text(url)
        count = ingest_source_text(session_id, url, "web", text)
        return f"✅ Ingested {count} chunks from website.", sources_markdown(session_id)
    except Exception as exc:  # noqa: BLE001
        return f"❌ Website ingest failed: {exc}", sources_markdown(session_id)


def ingest_youtube(session_id: str, url: str) -> tuple[str, str]:
    if not url.strip():
        return "Please provide a YouTube URL.", sources_markdown(session_id)
    try:
        text = load_youtube_transcript(url)
        count = ingest_source_text(session_id, url, "youtube", text)
        return f"✅ Ingested {count} chunks from YouTube transcript.", sources_markdown(session_id)
    except Exception as exc:  # noqa: BLE001
        return f"❌ YouTube ingest failed: {exc}", sources_markdown(session_id)


def ingest_uploaded_file(session_id: str, file_obj) -> tuple[str, str]:
    if file_obj is None:
        return "Please upload a file first.", sources_markdown(session_id)
    file_path = Path(file_obj)
    try:
        file_bytes = file_path.read_bytes()
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            text = load_pdf_text(file_bytes)
        elif suffix == ".docx":
            text = load_docx_text(file_bytes)
        elif suffix == ".txt":
            text = file_bytes.decode("utf-8", errors="ignore")
        else:
            raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")
        count = ingest_source_text(session_id, file_path.name, suffix.replace(".", ""), text)
        return f"✅ Ingested {count} chunks from {file_path.name}.", sources_markdown(session_id)
    except Exception as exc:  # noqa: BLE001
        return f"❌ File ingest failed: {exc}", sources_markdown(session_id)


def sources_markdown(session_id: str) -> str:
    sources = list_sources(session_id)
    if not sources:
        return "No sources ingested yet."
    return "\n".join(f"- {src}" for src in sources)


def clear_db_action(session_id: str) -> str:
    try:
        clear_database(session_id)
        return "✅ Database cleared."
    except Exception as exc:  # noqa: BLE001
        return f"❌ Failed to clear database: {exc}"


def ask_question(session_id: str, question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""
    try:
        return answer_question(session_id, question)
    except Exception as exc:  # noqa: BLE001
        return f"❌ Question answering failed: {exc}", ""


def build_interface() -> gr.Blocks:
    # Custom CSS for fancy background and rotating stars
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    .gradio-container {
        background: linear-gradient(135deg, #0a0e27 0%, #16213e 25%, #1a3a5e 50%, #16213e 75%, #0a0e27 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .rotating-stars {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 120px;
        height: 120px;
        opacity: 0.8;
        animation: rotate 20s linear infinite;
        pointer-events: none;
        z-index: 1;
    }
    
    .star {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #ffd700;
        border-radius: 50%;
        animation: twinkle 3s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
    }
    
    .star:nth-child(1) { top: 10%; left: 50%; animation-delay: 0s; }
    .star:nth-child(2) { top: 25%; left: 85%; animation-delay: 0.3s; }
    .star:nth-child(3) { top: 50%; left: 95%; animation-delay: 0.6s; }
    .star:nth-child(4) { top: 75%; left: 85%; animation-delay: 0.9s; }
    .star:nth-child(5) { top: 90%; left: 50%; animation-delay: 1.2s; }
    .star:nth-child(6) { top: 75%; left: 15%; animation-delay: 1.5s; }
    .star:nth-child(7) { top: 50%; left: 5%; animation-delay: 1.8s; }
    .star:nth-child(8) { top: 25%; left: 15%; animation-delay: 2.1s; }
    
    h1, h2, h3 {
        color: #fff;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        animation: float 3s ease-in-out infinite;
    }
    
    .gradio-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .gradio-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    .gradio-button[variant="primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .gradio-textbox, .gradio-file {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1.5px solid rgba(255, 215, 0, 0.3) !important;
        color: white !important;
    }
    
    .gradio-textbox input, .gradio-textbox textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
    }
    
    .gradio-markdown {
        color: #e0e0e0;
    }
    
    .gradio-markdown h1, .gradio-markdown h2, .gradio-markdown h3 {
        color: #ffd700;
    }
    """
    
    with gr.Blocks(title="knowledge-agent", css=custom_css, theme=gr.themes.Soft(primary_hue="purple")) as demo:
        # Rotating stars container (Akash Ganga)
        gr.HTML("""
        <div class="rotating-stars">
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
            <div class="star"></div>
        </div>
        """)
        
        # Initialize session state with unique session ID
        session_id = gr.State(value=str(uuid.uuid4()))
        
        gr.Markdown("# ✨ knowledge-agent")
        gr.Markdown(
            "Ingest web pages, YouTube transcripts, and files. Then ask cited questions."
        )
        gr.Markdown("*Each session has isolated knowledge base.*")
        if not os.getenv("OPENAI_API_KEY"):
            gr.Markdown(
                "⚠️ `OPENAI_API_KEY` is missing. Add it to `.env` before using the app."
            )
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Ingest content")
                website_url = gr.Textbox(
                    label="Website URL", placeholder="https://example.com/article"
                )
                website_btn = gr.Button("Ingest website")
                youtube_url = gr.Textbox(
                    label="YouTube URL", placeholder="https://www.youtube.com/watch?v=..."
                )
                youtube_btn = gr.Button("Ingest YouTube transcript")
                upload_file = gr.File(
                    label="Upload file (PDF, DOCX, TXT)",
                    file_count="single",
                    type="filepath",
                )
                upload_btn = gr.Button("Ingest uploaded file")
                ingest_status = gr.Markdown()
            with gr.Column():
                gr.Markdown("## Knowledge base")
                sources_box = gr.Markdown(value="No sources ingested yet.")
                clear_btn = gr.Button("Clear database")
                clear_status = gr.Markdown()
        gr.Markdown("---")
        gr.Markdown("## Ask a question")
        question = gr.Textbox(label="Question", lines=4)
        ask_btn = gr.Button("Get answer", variant="primary")
        answer_box = gr.Markdown(label="Answer")
        citations_box = gr.Markdown(label="Citations")

        website_btn.click(
            ingest_website, inputs=[session_id, website_url], outputs=[ingest_status, sources_box]
        )
        youtube_btn.click(
            ingest_youtube, inputs=[session_id, youtube_url], outputs=[ingest_status, sources_box]
        )
        upload_btn.click(
            ingest_uploaded_file, inputs=[session_id, upload_file], outputs=[ingest_status, sources_box]
        )
        clear_btn.click(clear_db_action, inputs=[session_id], outputs=[clear_status]).then(
            sources_markdown, inputs=[session_id], outputs=[sources_box]
        )
        ask_btn.click(
            ask_question, inputs=[session_id, question], outputs=[answer_box, citations_box]
        )

        return demo


if __name__ == "__main__":
    app = build_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)
