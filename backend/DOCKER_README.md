# Docker Deployment Guide

## Building the Docker Image

From the project root directory:

```bash
docker build -f backend/Dockerfile -t urdu-story-api .
```

## Running the Container

### Basic run:
```bash
docker run -p 8000:8000 urdu-story-api
```

### Run in detached mode:
```bash
docker run -d -p 8000:8000 --name urdu-api urdu-story-api
```

### Run with custom port:
```bash
docker run -p 3000:8000 urdu-story-api
```

## Accessing the API

Once the container is running:

- **API Endpoint**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/`

## Testing the API

### Using curl:
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prefix": "ایک دن", "max_length": 50}'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={"prefix": "ایک دن", "max_length": 50}
)
print(response.json()["story"])
```

## Container Management

### View logs:
```bash
docker logs urdu-api
```

### Stop container:
```bash
docker stop urdu-api
```

### Remove container:
```bash
docker rm urdu-api
```

### Remove image:
```bash
docker rmi urdu-story-api
```

## Container Details

- **Base Image**: python:3.11-slim
- **Exposed Port**: 8000
- **Working Directory**: /app/backend
- **Entry Point**: uvicorn server hosting FastAPI app
- **Image Size**: ~500MB (includes Python, FastAPI, models)

## Troubleshooting

### Port already in use:
```bash
# Use a different port
docker run -p 8001:8000 urdu-story-api
```

### View container processes:
```bash
docker ps
```

### Access container shell:
```bash
docker exec -it urdu-api /bin/bash
```

## Notes

- The container includes the trained BPE tokenizer and trigram model
- Models are loaded at startup (takes ~5 seconds)
- The API is production-ready with uvicorn ASGI server
- No GPU required - runs on CPU
