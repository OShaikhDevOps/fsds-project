import io

import requests
import streamlit as st
from PIL import Image


st.title("Fruit Ripeness Demo")
st.write("Upload an image or provide a URL. Ensure the backend is running at the endpoint below.")

endpoint = st.text_input("Inference endpoint", "http://localhost:8000/predict")

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"]) 
img_url = st.text_input("Or image URL")


def predict_image_bytes(img_bytes: bytes, filename: str):
    files = {"file": (filename, img_bytes, "image/jpeg")}
    try:
        resp = requests.post(endpoint, files=files, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        st.error(f"Request failed: {exc}")
        return None


if st.button("Predict"):
    if not uploaded and not img_url:
        st.error("Please upload an image or provide an image URL.")
    else:
        img_bytes = None
        filename = "upload.jpg"
        if uploaded:
            filename = uploaded.name
            img_bytes = uploaded.read()
        else:
            try:
                r = requests.get(img_url, timeout=15)
                r.raise_for_status()
                img_bytes = r.content
                filename = img_url.split("/")[-1] or filename
            except Exception as exc:
                st.error(f"Failed to download image: {exc}")

        if img_bytes:
            with st.spinner("Sending image to inference endpoint..."):
                result = predict_image_bytes(img_bytes, filename)

            if result:
                st.success("Prediction received")
                st.json(result)
                try:
                    conf = float(result.get("confidence", 0.0))
                    label = result.get("label", "-")
                    st.subheader(f"{label} — {conf*100:.2f}%")
                except Exception:
                    st.subheader(f"Result: {result}")

                try:
                    st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
                except Exception:
                    pass
