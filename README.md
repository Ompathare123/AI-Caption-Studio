# AI Caption Studio

AI Caption Studio is a professional, production-ready, AI-powered video caption generator. It extracts audio from uploaded videos, transcribes speech using Faster-Whisper, generates word-level timestamps using WhisperX, formats them into subtitles, and applies beautiful animated captions before rendering the final captioned video.

## Features
- **Video Upload**: Secure backend file uploads with size and format validation.
- **Audio Extraction**: Optimized high-quality audio extraction using FFmpeg.
- **Speech-to-Text Transcription**: High-performance transcription using `Faster-Whisper`.
- **Word-Level Alignment**: Exact word-level timestamp generation using `WhisperX`.
- **Subtitle Generation**: Automatic compilation of SRT and ASS subtitle formats.
- **Dynamic Captions Styling**: Rich ASS styles for animated and highlighted word captions.
- **Video Rendering**: High-speed video rendering overlaying animated captions via FFmpeg/MoviePy.
- **Interactive UI**: Sleek, responsive React frontend built with Vite, TypeScript, and Tailwind CSS.

## Tech Stack

### Backend
- **Core**: Python 3.14, FastAPI, Uvicorn, Pydantic
- **Database**: SQLite (development), PostgreSQL (production), SQLAlchemy, Alembic
- **Processing**: FFmpeg, MoviePy, OpenCV
- **AI/ML**: Faster-Whisper, WhisperX

### Frontend
- **Core**: React, Vite, TypeScript
- **Styling**: Tailwind CSS
- **Routing & Networking**: React Router, Axios, React Dropzone

### Deployment & DevOps
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Dotenv configuration management

---

## Installation & Local Development Setup

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the FastAPI Development Server**:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be available at `http://127.0.0.1:8000/`.

### Frontend Setup (Coming Soon)

---

## Development Roadmap

- **Milestone 1**: Project initialization, directory structure, health check endpoint, environment setup. (Completed)
- **Milestone 2**: Video upload & saving API, backend file storage, and integration tests.
- **Milestone 3**: Audio extraction using FFmpeg.
- **Milestone 4**: Speech-to-Text transcription with Faster-Whisper.
- **Milestone 5**: Word-level alignment and SRT/ASS subtitle generation.
- **Milestone 6**: Video rendering with stylized and animated captions.
- **Milestone 7**: Frontend UI development (React + TypeScript + Tailwind CSS).
- **Milestone 8**: Database integrations, user history, and job queue.
- **Milestone 9**: Deployment, Dockerization, and CI/CD pipelines.

---

## License
MIT
