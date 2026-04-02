# Streamlit Community Cloud Pre-Deploy Checklist

Use this checklist before deploying `exam_ai_system` to Streamlit Community Cloud.

## 1. Repository Readiness

- Ensure the project is pushed to GitHub.
- Ensure the main app file is `app.py`.
- Ensure `.env` is not committed.
- Ensure these files exist in the repo:
  - `app.py`
  - `requirements.txt`
  - `runtime.txt`
  - `README.md`

## 2. Recommended Cloud Provider Setup

Use `groq` as the default provider for Streamlit Community Cloud.

Why:
- Groq is API-based and works well in hosted environments.
- Ollama is primarily local and is not the recommended primary provider for Streamlit Community Cloud.

## 3. Required Secrets

Add these values in Streamlit Community Cloud app settings:

```toml
LLM_PROVIDER = "groq"
GROQ_API_KEY = "your_real_groq_api_key"
GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_MODEL = "mistral"
```

Minimum required for cloud deployment:
- `LLM_PROVIDER`
- `GROQ_API_KEY`
- `GROQ_MODEL`

## 4. Local Verification Before Deploy

Run the app locally:

```powershell
streamlit run app.py
```

Run the tests:

```powershell
pip install -r requirements-dev.txt
python -m pytest -q
```

Verify these flows manually:
- Provider selector works
- Groq configuration shows as ready
- Exam generation works
- Flash-card navigation works
- Practice exam answer reveal works
- Submit locks answers
- Balloons show only once after passing

## 5. Streamlit Community Cloud Setup

In Streamlit Community Cloud:

1. Click `New app`
2. Select the GitHub repository
3. Choose the correct branch
4. Set the app file path to `app.py`
5. Add the secrets in the app settings
6. Deploy

## 6. Post-Deploy Smoke Test

After deployment:

- Open the app URL
- Confirm the sidebar shows the correct provider/model
- Generate a practice exam
- Answer at least one question
- Submit the exam
- Verify score/result rendering
- Verify correct-answer reveal only appears for practice mode

## 7. Known Deployment Guidance

- Prefer Groq in cloud
- Keep Ollama as a local development option
- Do not rely on `.env` in Streamlit Community Cloud
- Use app secrets instead of committing credentials

## 8. If Deployment Fails

Check:
- Missing `GROQ_API_KEY`
- Bad model name
- Missing dependency in `requirements.txt`
- Wrong app file path
- Python version mismatch
