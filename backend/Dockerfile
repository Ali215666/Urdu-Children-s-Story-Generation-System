# Dockerfile for Urdu Story Generator FastAPI Service
# Build from project root: docker build -f backend/Dockerfile -t urdu-story-api .

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project modules
COPY tokenizer/ /app/tokenizer/
COPY model/ /app/model/
COPY backend/ /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard]

# Expose FastAPI port
EXPOSE 8000

# Set working directory to backend
WORKDIR /app/backend

# Run the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
