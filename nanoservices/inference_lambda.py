import io
import os
import json
import base64
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "best_fruit_model.pt"

model = None
model_backend: Optional[str] = None
model_names: Optional[dict] = None
load_error: Optional[str] = None


def _load_model():
    global model, model_backend, model_names, load_error

    if not MODEL_PATH.exists():
        load_error = f"Model file not found at {MODEL_PATH}."
        logger.error(load_error)
        return

    try:
        from ultralytics import YOLO
        model = YOLO(str(MODEL_PATH))
        model_backend = "ultralytics"
        model_names = getattr(model, "names", None)
        logger.info("Model loaded with ultralytics (names=%s)", model_names)
        return
    except Exception as exc:
        load_error = str(exc)
        logger.exception("Failed to load model with ultralytics: %s", exc)

    try:
        import torch
        model = torch.load(str(MODEL_PATH), map_location="cpu")
        model_backend = "torch"
        model_names = None
        logger.info("Model loaded with torch")
        return
    except Exception as exc:
        load_error = (load_error + " | " + str(exc)) if load_error else str(exc)
        logger.exception("Failed to load model with torch: %s", exc)

    logger.error("Model failed to load: %s", load_error)


def _predict_ultralytics(image_bytes: bytes) -> dict:
    import numpy as np

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir="/tmp") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        results = model(str(tmp_path), device="cpu")
        res0 = results[0]
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

        try:
            class_idx = int(res0.probs.top1)
        except Exception:
            class_idx = int(np.array(probs).argmax())

        confidence = float(probs[class_idx])
        label = names_dict[class_idx] if names_dict and class_idx in names_dict else str(class_idx)
        return {"label": label, "confidence": confidence, "class_idx": class_idx}
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _predict_torch(image_bytes: bytes) -> dict:
    import torch
    import numpy as np
    from PIL import Image
    import torchvision.transforms as T

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    x = transform(img).unsqueeze(0)
    model.eval()
    with torch.no_grad():
        out = model(x)

    probs = torch.nn.functional.softmax(out.squeeze(), dim=0).cpu().numpy()
    class_idx = int(np.argmax(probs))
    confidence = float(probs[class_idx])
    return {"label": str(class_idx), "confidence": confidence, "class_idx": class_idx}


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, _context):
    global model

    if model is None:
        _load_model()

    if model is None:
        return _response(500, {"error": "model not loaded", "load_error": load_error})

    http_method = (
        event.get("httpMethod")
        or event.get("requestContext", {}).get("http", {}).get("method", "")
    )

    if http_method == "GET":
        return _response(200, {
            "service": "Fruit Ripeness Inference",
            "model_path": str(MODEL_PATH),
            "loaded": model is not None,
            "backend": model_backend,
        })

    body = event.get("body", "")
    if not body:
        return _response(400, {"error": "empty body"})

    image_bytes = base64.b64decode(body) if event.get("isBase64Encoded") else (
        body.encode() if isinstance(body, str) else body
    )

    if not image_bytes:
        return _response(400, {"error": "empty image"})

    start = time.time()
    try:
        if model_backend == "ultralytics":
            result = _predict_ultralytics(image_bytes)
        elif model_backend == "torch":
            result = _predict_torch(image_bytes)
        else:
            return _response(500, {"error": "no supported model backend"})
    except Exception as exc:
        logger.exception("Prediction error")
        return _response(500, {"error": "prediction error", "detail": str(exc)})

    result["inference_ms"] = round((time.time() - start) * 1000, 2)
    return _response(200, result)
