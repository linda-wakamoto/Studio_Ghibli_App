# Use a slim Python base image
FROM python:3.11-slim

WORKDIR /workspace

# 1. FIX: Point explicitly to the api folder for requirements
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. FIX: Copy the API script and data folders smoothly
COPY api/ ./api
COPY data/ ./data

EXPOSE 8080

# Run Uvicorn pointing to your FastAPI app inside model.py
CMD ["uvicorn", "api.model:app", "--host", "0.0.0.0", "--port", "8080"]