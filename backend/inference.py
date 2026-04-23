from pathlib import Path
import time
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_TITLE = "Fruit Ripeness Inference"
APP_DESC = "Inference API that predicts fruit ripeness using a classification model stored in /model"

app = FastAPI(title=APP_TITLE, description=APP_DESC, version="1.0.2")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "best_fruit_model.pt"

# Globals populated at startup
model = None
model_backend: Optional[str] = None
model_names: Optional[dict] = None
load_error: Optional[str] = None


class PredictResponse(BaseModel):
    label: str
    confidence: float
    class_idx: int
    inference_ms: float


@app.on_event("startup")
def load_model():
    """Attempt to load the model. Prefer `ultralytics.YOLO` (recommended).

    If `ultralytics` is not installed the app will set a helpful load_error
    message and endpoints will return 500 until the required packages are installed.
    """
    global model, model_backend, model_names, load_error
    if not MODEL_PATH.exists():
        load_error = f"Model file not found at {MODEL_PATH}."
        logger.error(load_error)
        return

    try:
        # Prefer ultralytics YOLO class for common .pt models from Ultralytics
        from ultralytics import YOLO

        model = YOLO(str(MODEL_PATH))
        model_backend = "ultralytics"
        # model.names may exist for detector/classifier
        model_names = getattr(model, "names", None)
        return
    except Exception as exc:  # pragma: no cover - runtime dependency handling
        load_error = str(exc)
        logger.exception("Failed to load model with ultralytics YOLO: %s", exc)

    try:
        import torch

        model = torch.load(str(MODEL_PATH), map_location="cpu")
        model_backend = "torch"
        # no reliable names mapping for arbitrary torch checkpoints
        model_names = None
        return
    except Exception as exc:  # pragma: no cover
        load_error = load_error + " | " + str(exc) if load_error else str(exc)
        logger.exception("Failed to load model with torch.load: %s", exc)

    if model is not None:
        logger.info("Model loaded successfully (backend=%s)", model_backend)
    else:
        logger.error("Model failed to load: %s", load_error)


@app.get("/", tags=["Health"])
def root():
    return {"service": APP_TITLE, "model_path": str(MODEL_PATH), "loaded": model is not None, "backend": model_backend}


@app.post("/predict", response_model=PredictResponse, tags=["Inference"])
async def predict(file: UploadFile = File(...)):
    """Predict ripeness from an uploaded image file.

    Requires `ultralytics` package for best compatibility with the provided .pt model.
    """
    if model is None:
        logger.error("Prediction requested but model not loaded: %s", load_error)
        raise HTTPException(status_code=500, detail={"error": "model not loaded", "load_error": load_error})

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    start = time.time()

    # Preferred backend: ultralytics YOLO
    if model_backend == "ultralytics":
        import tempfile
        import os
        tmp_path = None
        try:
            # Save uploaded bytes to a temp file and call the model as in predict.py
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(contents)
                tmp_path = tmp.name

            results = model(str(tmp_path), device="cpu")
            res0 = results[0]

            # names may live on the result or the model
            names_dict = getattr(res0, "names", None) or model_names

            probs = None
            if hasattr(res0, "probs") and res0.probs is not None:
                try:
                    probs = res0.probs.data.tolist()
                except Exception:
                    try:
                        probs = list(res0.probs)
                    except Exception:
                        probs = None

            if probs is None:
                scores = getattr(res0, "scores", None)
                if scores is not None:
                    try:
                        probs = list(scores)
                    except Exception:
                        probs = None

            if not probs:
                raise RuntimeError("Model result does not contain probability scores")

            # try to use top1 if available (predict.py uses r.probs.top1)
            try:
                class_idx = int(res0.probs.top1)
            except Exception:
                import numpy as np

                probs_arr = np.array(probs)
                class_idx = int(probs_arr.argmax())

            confidence = float(probs[class_idx])
            label = names_dict[class_idx] if names_dict and class_idx in names_dict else str(class_idx)
        except Exception as exc:
            logger.exception("Ultralytics prediction error")
            raise HTTPException(status_code=500, detail={"error": "ultralytics prediction error", "detail": str(exc)})
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
    elif model_backend == "torch":
        # Try to run a very generic torch forward pass if the checkpoint exposes a callable model
        try:
            import io
            from PIL import Image
            import torchvision.transforms as T
            import torch

            img = Image.open(io.BytesIO(contents)).convert("RGB")
            transform = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])])
            x = transform(img).unsqueeze(0)
            model.eval()
            with torch.no_grad():
                out = model(x)
            # assume classification logits
            probs = torch.nn.functional.softmax(out.squeeze(), dim=0).cpu().numpy()
            import numpy as np

            class_idx = int(np.argmax(probs))
            confidence = float(probs[class_idx])
            label = str(class_idx)
        except Exception as exc:
            logger.exception("Torch prediction error")
            raise HTTPException(status_code=500, detail={"error": "torch prediction error", "detail": str(exc)})
    else:
        raise HTTPException(status_code=500, detail="No supported model backend loaded")

    inference_ms = (time.time() - start) * 1000.0

    return PredictResponse(label=label, confidence=confidence, class_idx=class_idx, inference_ms=inference_ms)
