# Build context is the rag/ directory.
# The chroma/ index is pre-built by CI before this runs (see .github/workflows/google-cloudrun-rag.yml).

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source + pre-built chroma index
COPY . .

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
