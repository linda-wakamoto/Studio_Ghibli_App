FROM python:3.11-slim

WORKDIR /app

# Copy the API-specific requirements from the root context
COPY requirements_api.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API logic and the required model matrix
COPY api/model.py .
COPY models/ ./models/

EXPOSE 8080

CMD ["uvicorn", "model:app", "--host", "0.0.0.0", "--port", "8080"]