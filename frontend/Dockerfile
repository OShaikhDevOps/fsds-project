FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app/frontend

# system deps needed for some packages 
RUN apt-get update && \
	apt-get install -y --no-install-recommends build-essential git curl libsndfile1 libgl1 && \
	rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker layer caching
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
	pip install --no-cache-dir -r requirements.txt

# DUCKDNS
COPY duckdns.sh .
RUN chmod +x duckdns.sh

# Copy app sources
COPY ./ ./

EXPOSE 8080

CMD ["./duckdns.sh"]
# Default command runs the Streamlit app on port 8080 and binds to 0.0.0.0
# CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]