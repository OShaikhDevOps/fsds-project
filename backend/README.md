# Fruit Ripeness Inference (FastAPI)

This service exposes a simple FastAPI application that loads a classification model from the `model/` folder and provides a `/predict` endpoint.

Quick start

1. Install dependencies (prefer inside a virtualenv):

```bash
pip install -r backend/requirements.txt
```

2. Run the API with Uvicorn (from repository root):

```bash
uvicorn backend.inference:app --host 0.0.0.0 --port 8000 --reload
```

3. Open Swagger UI: http://localhost:8000/docs

Notes
- The app prefers the `ultralytics` package to load YOLO-style `.pt` models. If `ultralytics` is not available it will attempt to `torch.load` the checkpoint and run a generic forward pass (this may not succeed for all checkpoint formats).
- The expected model path for this repo is `backend/models/best_fruit_model.pt` (used by `backend/predict.py`). Ensure the model file exists at that location or update `backend/inference.py` to point to your model.
