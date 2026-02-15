# RAG_Chat Deployment & Testing Guide

## Deployment Steps

### Local Development Deployment

#### Prerequisites
- Python 3.10+
- pip/conda package manager
- OpenAI API key
- Git

#### Step 1: Clone Repository
```bash
git clone https://github.com/bhardwajnishant98-arch/RAG_Chat.git
cd RAG_Chat
```

#### Step 2: Set Up Python Environment
```bash
# Using venv (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n rag_chat python=3.10
conda activate rag_chat
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Copy example to actual .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-your_key_here
```

#### Step 5: Run Pre-deployment Tests
```bash
# Test imports
python -c "import app.gradio_app; print('✓ App imports successfully')"

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

#### Step 6: Start Application
```bash
python app/gradio_app.py
```

The app will be available at: **http://localhost:7860**

---

## Testing Procedures

### Unit Tests (When Available)
```bash
pytest tests/ -v
```

### Manual Testing Checklist

#### Gradio Interface Tests
- [ ] **Home Page Loads**: Application starts without errors
- [ ] **Upload Files**: Try uploading a PDF (if available)
- [ ] **Web Input**: Enter a valid website URL
- [ ] **Chat Interface**: Basic text input works
- [ ] **Styling**: UI displays properly with all controls visible

#### Application Functionality Tests
- [ ] **Import Test**: All modules import correctly
  ```bash
  python -c "from app.gradio_app import *; print('All imports OK')"
  ```

- [ ] **Configuration Test**: Environment variables load properly
  ```python
  import os
  print(f"API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
  print(f"Chat Model: {os.getenv('OPENAI_CHAT_MODEL')}")
  ```

- [ ] **Chroma DB Test**: Vector database initializes
  ```python
  from app.gradio_app import get_chroma_collection
  collection = get_chroma_collection()
  print(f"Collection initialized: {collection is not None}")
  ```

#### Document Processing Tests
- [ ] **PDF Loading**: Test with sample PDF (optional)
- [ ] **Web Scraping**: Test with valid URL
- [ ] **Text Chunking**: Verify token splitting works correctly

#### Error Handling Tests
- [ ] **Missing API Key**: Verify graceful error message
- [ ] **Invalid Model**: Check error handling for unavailable models
- [ ] **Empty Document**: Handle edge case of empty upload

---

## CI/CD Pipeline Testing

### GitHub Actions Workflow
The repository includes automated CI/CD through `.github/workflows/python-package-conda.yml`

**Workflow Checks:**
- ✅ Dependencies install successfully
- ✅ Code passes flake8 linting
- ✅ App imports without errors
- ✅ All Python files have valid syntax

**View Workflow Status:**
1. Go to: **Actions** tab in GitHub
2. Check latest workflow run
3. All checks should show ✅ (green)

---

## Troubleshooting Deployment

### Issue: "ModuleNotFoundError: No module named 'gradio'"
**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "OpenAI API key not found"
**Solution:**
Ensure `.env` file exists in root directory with:
```
OPENAI_API_KEY=sk-proj-your_actual_key
```

### Issue: "Chroma database connection error"
**Solution:**
```bash
mkdir -p app/storage
# Ensure app/storage directory is writable
chmod 755 app/storage
```

### Issue: "Port 7860 already in use"
**Solution:**
```bash
# Find and kill process using port 7860
lsof -i :7860
kill -9 <PID>

# Or use different port
gradio --port 7861
```

---

## Performance Monitoring

### Key Metrics to Monitor
- **Startup Time**: Should complete in <30 seconds
- **First Query Response**: Should respond in <10 seconds
- **Memory Usage**: Monitor for memory leaks during long sessions
- **API Rate Limits**: Track OpenAI API usage

### Logging
Enable debug logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Production Deployment

For production deployments, consider:

### Docker Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app/gradio_app.py"]
```

### Environment Variables (Production)
- Store API keys in secure secret management (AWS Secrets Manager, Azure Key Vault)
- Set `GRADIO_SERVER_NAME=0.0.0.0` for external access
- Configure `GRADIO_SERVER_PORT` as needed

### Health Checks
```bash
curl -f http://localhost:7860/health || exit 1
```

---

## Testing Results Summary

| Test Category | Status | Notes |
|---|---|---|
| Imports | ✅ | All modules import correctly |
| Linting | ✅ | Code passes flake8 checks |
| Dependencies | ✅ | requirements.txt installs successfully |
| Configuration | ✅ | .env loads correctly |
| UI Load | ✅ | Gradio interface loads at localhost:7860 |
| CI/CD Pipeline | ✅ | GitHub Actions workflow passing |

---

**Last Updated:** February 15, 2026  
**Status:** ✅ Ready for Deployment
