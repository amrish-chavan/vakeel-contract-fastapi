# vakeel-contract-api

AI-powered contract analysis API built with FastAPI and Google Gemini.

## Features

- Upload contract documents (`.pdf`, `.txt`)
- AI analysis of contract clauses using Google Gemini
- Document storage in MongoDB (via Motor, async driver)

## Tech Stack

- **FastAPI** — web framework
- **Motor / PyMongo** — async MongoDB driver
- **google-genai** — Gemini API client
- **pypdf / PyPDF2** — PDF text extraction
- **uv** — dependency management

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Docker + docker-compose (for MongoDB)

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create your environment file:

   ```bash
   cp app/.env.example app/.env
   ```

   Then edit `app/.env` and set real values:
   - `MONGODB_URI` — MongoDB connection string
   - `GEMINI_API_KEY` — Google Gemini API key

3. Start MongoDB:

   ```bash
   docker-compose up -d
   ```

4. Run the API:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000` (interactive docs at `/docs`).

## Project Structure

```
app/
  main.py            # FastAPI app entrypoint
  config.py          # Environment / settings
  database.py        # MongoDB connection
  models.py          # Data models
  routes/            # API routers (contracts, analysis)
  service/           # Parsing & Gemini analysis logic
  .env.example       # Example environment variables
docker-compose.yml   # MongoDB service
uploads/             # Runtime user uploads (gitignored)
```

## Configuration

| Variable         | Description                     |
| ---------------- | ------------------------------- |
| `MONGODB_URI`    | MongoDB connection string       |
| `GEMINI_API_KEY` | Google Gemini API key           |
| `UPLOAD_DIR`     | Upload directory (default `uploads`) |
| `MAX_FILE_SIZE`  | Max upload size in MB (default 10) |
| `ALLOWED_EXTENSIONS` | Allowed file types (`.pdf`, `.txt`) |
