# Exam AI System

A Streamlit-based GenAI exam generator that supports both Groq and Ollama providers, plus Supabase-backed authentication and exam history.

## Features

- Provider selection in the UI: `groq` or `ollama`
- Practice, certification, and assessment modes
- Flash-card style question flow
- Practice-mode answer reveal after submit
- Supabase-backed login and registration
- Persistent exam history per user

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`
4. Fill in the required LLM and Supabase values.
5. Start the app:

```powershell
streamlit run app.py
```

## Supabase Setup

1. Create a Supabase project.
2. Open the project dashboard.
3. Go to `Project Settings > API`.
4. Copy:
- `Project URL` into `SUPABASE_URL`
- a secure backend key into `SUPABASE_SERVICE_ROLE_KEY`
5. Open `SQL Editor` and run [schema.sql](/d:/GenAI_Capstone/exam_ai_system/supabase/schema.sql)

Required Supabase schema:
- `exam_attempts` table for storing user attempt history

## Run Tests

Install dev dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the full test suite:

```powershell
python -m pytest -q
```

Run the auth/history tests only:

```powershell
python -m pytest tests/test_auth_service.py tests/test_history_service.py -q
```

## Environment Variables

- `LLM_PROVIDER`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `OLLAMA_MODEL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Deployment Notes

### Streamlit Community Cloud

- Use `groq` as the recommended cloud provider
- Add both LLM and Supabase secrets in the deployment dashboard
- Set the app file to `app.py`
- Use `requirements.txt` and `runtime.txt`
- Follow [STREAMLIT_CLOUD_CHECKLIST.md](/d:/GenAI_Capstone/exam_ai_system/STREAMLIT_CLOUD_CHECKLIST.md)

### Render / Docker / VM

- Install dependencies from `requirements.txt`
- Set environment variables through the hosting platform
- Run:

```powershell
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Important Security Note

- Never commit your Supabase service key to GitHub
- Keep `SUPABASE_SERVICE_ROLE_KEY` only in local `.env` and hosting secrets
- Rotate keys immediately if they are ever exposed

## Recommended Production Improvements

- Add stronger row-level security and user-safe database policies
- Add automated tests for more end-to-end auth/session scenarios
- Add structured logging and provider error monitoring
- Add account recovery and email verification flows
