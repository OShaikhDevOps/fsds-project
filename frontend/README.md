# Frontend Streamlit Demo

This folder contains a small Streamlit demo that calls the FastAPI inference endpoint in `backend`.

Quick start

1. Ensure the backend is running (from repository root):

```bash
uvicorn backend.inference:app --host 0.0.0.0 --port 8000 --reload
```

2. Install frontend dependencies (prefer a virtualenv):

```bash
pip install -r frontend/requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run frontend/streamlit_app.py
```

The app defaults to `http://localhost:8000/predict`. Upload an image or provide a URL and click `Predict`.
