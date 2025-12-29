# Docker Usage

The framework can be run inside a Docker container.

## Prerequisites

- Docker installed on your machine.
- An OpenAI API Key.

## Build the Image

```bash
docker build -t ai-eval-framework .
```

## Run the Container

### With Mock Client (Local)
```bash
docker run --rm ai-eval-framework python -m src.main --mock
```

### With OpenAI API Key
Pass your API key as an environment variable:

```bash
docker run --rm \
  -e OPENAI_API_KEY="your-api-key-here" \
  ai-eval-framework python -m src.main
```

### With .env file
If you have a `.env` file locally:

```bash
# Run CLI tests in Docker
docker run --env-file .env ai-eval-framework python -m src.main
```

## Docker Compose (Full Stack)
To run the entire environment (Dashboard, Target Chatbot, and MongoDB) with a single command:

1.  **Start Services**:
    ```bash
    docker-compose up --build
    ```
2.  **Access Services**:
    -   **Dashboard**: `http://localhost:8501`
    -   **Target App**: `http://localhost:8503`
    -   **MongoDB**: `localhost:27018` (Mapped to 27017 internally)

3.  **Shutdown**:
    ```bash
    docker-compose down
    ```

## Troubleshooting

### Port Conflicts
By default, the Docker Compose configuration uses port **27018** for MongoDB to avoid conflicts with local instances running on 27017.

If you still encounter `Bind for 0.0.0.0:27018 failed`:
- **Solution**: Edit `docker-compose.yaml` and change the port mapping to another value (e.g., `"27019:27017"`).

### Networking Issues
If the dashboard cannot connect to the target app:
- Ensure `TARGET_URL` in `docker-compose.yaml` is set to `http://target_app:8503` (the internal Docker network address).
