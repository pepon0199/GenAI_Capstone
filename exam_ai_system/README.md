# Exam AI System

A Streamlit-based GenAI exam generator that supports both Groq and Ollama providers.

## Features

- Provider selection in the UI: `groq` or `ollama`
- Practice, certification, and assessment modes
- Flash-card style question flow
- Practice-mode answer reveal after submit
- Session-based exam review and scoring

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your values.
4. Start the app:

```powershell
streamlit run app.py
```

## Run Tests

Install dev dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the test suite:

```powershell
python -m pytest -q
```

## Environment Variables

- `LLM_PROVIDER`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `OLLAMA_MODEL`

## Deployment Notes

### Streamlit Community Cloud

- Use `groq` as the recommended cloud provider
- Set the app file to `app.py`
- Add the required secrets in the deployment dashboard
- Use `requirements.txt` and `runtime.txt`
- Follow [STREAMLIT_CLOUD_CHECKLIST.md](/d:/GenAI_Capstone/exam_ai_system/STREAMLIT_CLOUD_CHECKLIST.md)

### Render / Docker / VM

- Install dependencies from `requirements.txt`
- Set environment variables through the hosting platform
- Run:

```powershell
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Recommended Production Improvements

- Add automated tests for scoring, provider selection, and session-state navigation
- Add structured logging and provider error monitoring
- Add authentication if multiple real users will access the system
- Add persistent storage if exam history must be saved
