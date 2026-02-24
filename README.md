# MediRoute AI - Backend

Autonomous Medical Evacuation Decision Engine

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Setup and Installation

1. **Navigate to the app folder**
   ```bash
   cd app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your required API keys and configuration.

## Running the Application

**Start the development server:**
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

- `GET /health` - Health check endpoint
- See http://localhost:8000/docs for full API documentation

## Development

The `--reload` flag enables auto-reload on code changes during development.

To run without auto-reload (production-like):
```bash
uvicorn main:app
```
