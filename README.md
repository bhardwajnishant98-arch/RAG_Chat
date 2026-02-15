# RAG_Chat

**Ask Questions about your data** - A Retrieval-Augmented Generation (RAG) application that allows you to upload documents and ask intelligent questions about their content.

## Overview

RAG_Chat is an intelligent document Q&A system powered by OpenAI's language models and Chroma vector database. Upload PDFs, Word documents, web pages, or YouTube videos, and get instant answers to your questions using semantic search and advanced language understanding.

### Key Features

- 📄 **Multiple Document Formats**: Support for PDF, DOCX, web pages, and YouTube transcripts
- 🔍 **Semantic Search**: Uses embeddings to find contextually relevant passages
- 💬 **Intelligent Q&A**: Powered by GPT-4 for accurate, contextual responses
- 🗄️ **Persistent Storage**: Vector database with Chroma for fast retrieval
- 🎨 **User-Friendly Interface**: Built with Gradio for easy interaction
- ⚡ **Fast Processing**: Optimized chunking and token management

## Tech Stack

- **LLM**: OpenAI (GPT-4o or GPT-4o-mini)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Chroma DB
- **UI Framework**: Gradio
- **Document Processing**: pypdf, python-docx, BeautifulSoup, youtube-transcript-api
- **Language**: Python 3.8+

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- pip or conda package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bhardwajnishant98-arch/RAG_Chat.git
cd RAG_Chat
```

### 2. Create Python Environment

**Using conda (recommended):**
```bash
conda create -n rag_chat python=3.10
conda activate rag_chat
```

**Using venv:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=sk-proj-your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
STORAGE_DIR=./app/storage
COLLECTION_NAME=knowledge_agent
MAX_CHUNK_TOKENS=1000
CHUNK_OVERLAP_TOKENS=150
```

## Usage

### Running the Application

```bash
python app/gradio_app.py
```

The application will start at `http://localhost:7860`

### Using the Interface

1. **Upload Documents**: Click "Upload Files" to add PDFs, Word docs, or provide URLs
2. **Process Content**: System automatically processes and vectorizes documents
3. **Ask Questions**: Type your question in the chat interface
4. **Get Answers**: Receive AI-powered responses based on your documents

## Project Structure

```
RAG_Chat/
├── app/
│   ├── gradio_app.py          # Main application
│   ├── loaders/               # Document loaders
│   │   ├── __init__.py
│   │   ├── pdf.py
│   │   ├── docx.py
│   │   ├── web.py
│   │   └── youtube.py
│   └── storage/               # Vector database storage
├── scripts/                   # Utility scripts
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_CHAT_MODEL` | Model for chat responses | gpt-4o-mini |
| `OPENAI_EMBEDDING_MODEL` | Model for embeddings | text-embedding-3-small |
| `STORAGE_DIR` | Vector database directory | ./app/storage |
| `COLLECTION_NAME` | Chroma collection name | knowledge_agent |
| `MAX_CHUNK_TOKENS` | Maximum tokens per chunk | 1000 |
| `CHUNK_OVERLAP_TOKENS` | Token overlap for context | 150 |

## Security

⚠️ **Important Security Notes:**

- **Never commit `.env` file** with real API keys - it's in `.gitignore` by default
- Store API keys securely using environment variables or secret management tools
- For GitHub Actions, use repository secrets, not hardcoded credentials
- Regularly rotate your API keys

## Troubleshooting

### Issue: "OpenAI API key not found"
**Solution**: Ensure `.env` file exists in the project root with `OPENAI_API_KEY` set

### Issue: "Chroma database connection error"
**Solution**: Check that `STORAGE_DIR` exists and is writable. Create it with: `mkdir -p app/storage`

### Issue: "No module named 'gradio'"
**Solution**: Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

We follow PEP 8 style guidelines. Format with:
```bash
black app/
flake8 app/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is provided as-is. See LICENSE file for details.

## Support

For issues, questions, or suggestions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Contact the maintainers

## Roadmap

- [ ] Support for more document formats (Excel, CSV, JSON)
- [ ] Multi-language support
- [ ] Advanced caching and indexing
- [ ] API endpoint for programmatic access
- [ ] Deployment guides (Docker, Heroku, AWS)
- [ ] Unit and integration tests
- [ ] Performance monitoring and logging

## Related Projects

- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Chroma DB](https://github.com/chroma-core/chroma) - Vector database
- [OpenAI Python](https://github.com/openai/openai-python) - OpenAI SDK

---

**Made with ❤️ for better document intelligence**
