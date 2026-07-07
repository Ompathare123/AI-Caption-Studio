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
- **Milestone 2**: Video upload & saving API, backend file storage, and integration tests. (Completed)
- **Milestone 3**: Audio extraction using FFmpeg. (Completed)
- **Milestone 4**: Speech-to-Text transcription with Faster-Whisper.
- **Milestone 5**: Word-level alignment and SRT/ASS subtitle generation.
- **Milestone 6**: Video rendering with stylized and animated captions.
- **Milestone 7**: Frontend UI development (React + TypeScript + Tailwind CSS).
- **Milestone 8**: Database integrations, user history, and job queue.
- **Milestone 9**: Deployment, Dockerization, and CI/CD pipelines.

---

## System Architecture & Modules (Milestone 2)

We implement Clean Architecture to separate routing, data validation, business logic, configuration, and data persistence.

### Folder Structure & Purpose

- **`backend/app/core/`**: Configuration, error definitions, and global log configuration.
- **`backend/app/database/`**: Database engine and connection configurations.
- **`backend/app/models/`**: SQLAlchemy ORM models mapping to SQLite database structures.
- **`backend/app/schemas/`**: Pydantic schemas validating input payloads and formatting outgoing responses.
- **`backend/app/services/`**: The core business logic including file chunk streaming, OpenCV validation, and hash check.
- **`backend/app/utils/`**: Reusable low-level helpers like file hashing and validation criteria.
- **`backend/app/api/v1/endpoints/`**: API endpoint router logic.

### New Module Files

1. **[config.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/core/config.py)**: Loads settings from `.env` using Pydantic Settings. Ensures vital server subdirectories exist.
2. **[logging.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/core/logging.py)**: Configures standard formatted logger capturing execution metrics.
3. **[errors.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/core/errors.py)**: Declares custom upload exceptions and binds global error exception handlers to abstract traceback leaks.
4. **[session.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/database/session.py)**: Initiates SQLAlchemy engine connection pool and local DB session.
5. **[video.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/models/video.py)**: Defines `Video` schema storing original name, stored path, SHA-256 file hash, file size, duration, status, and timestamp.
6. **[upload.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/upload.py)**: Defines `VideoUploadResponse` validation structure.
7. **[file_utils.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/utils/file_utils.py)**: Low-level file checkers verifying extensions, MIME formats, generating date folders (`YYYY/MM`), and chunked file hashing.
8. **[upload_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/upload_service.py)**: The central business pipeline driving size validation, temp streaming, OpenCV checks, DB integration, and directory movement.

### REST API Documentation

#### Upload Video File
- **Endpoint**: `POST /api/v1/upload`
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `file`: Video binary payload.
- **Validations Enforced**:
  - **Allowed Extensions**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`. (Returns `HTTP 400 Bad Request` if mismatch).
  - **Allowed MIME Types**: `video/mp4`, `video/quicktime`, `video/x-msvideo`, `video/avi`, `video/msvideo`, `video/x-matroska`, `video/mkv`, `video/webm`. (Returns `HTTP 400 Bad Request` if mismatch).
  - **Maximum Size**: `2 GB`. (Returns `HTTP 413 Payload Too Large` if exceeded).
  - **Duplicate Validation**: SHA-256 hash comparison against existing records. (Returns `HTTP 409 Conflict` if duplicate).
  - **Corrupted Validation**: OpenCV integrity verification. (Returns `HTTP 400 Bad Request` if corrupted).
  - **Empty Validation**: File size must exceed 0 bytes. (Returns `HTTP 400 Bad Request` if empty).
- **Successful Response (`HTTP 201 Created`)**:
  ```json
  {
    "id": "bfcc4358-81da-4007-b44f-afb451940e64",
    "filename": "my_video.mp4",
    "size": 1048576,
    "duration": 12.4,
    "status": "uploaded"
  }
  ```

---

## Audio Processing Architecture (Milestone 3)

We implement a modular audio extraction service that utilizes FFmpeg to isolate and format audio streams for subsequent AI transcription.

### Why WAV Format & PCM 16-bit Mono 16 kHz?

1. **WAV (Waveform Audio File Format)**: WAV is an uncompressed or lossless audio container format. It stores audio in raw bytes (PCM), making it computationally trivial to read, segment, and stream compared to compressed codecs like MP3 or AAC.
2. **PCM 16-bit**: 16-bit linear pulse-code modulation (PCM) is standard for representing audio signal amplitude. Most automatic speech recognition (ASR) engines (including Faster-Whisper and WhisperX) are trained on 16-bit depth signals.
3. **16000 Hz (16 kHz) Sample Rate**: Human voice frequencies useful for speech recognition reside well within the 8 kHz band. By sampling at 16 kHz, we capture all speech details while avoiding excess high-frequency noise and keeping resource sizes small. Whisper models specifically require 16 kHz audio as input.
4. **Mono (1 Channel)**: Stereo channels record sound spatial orientation, which is redundant for speech transcription. Converting stereo to mono reduces the data volume by half and matches the expected input vector structure of the transcription neural networks.

### FFmpeg Extraction Mechanism

We run an FFmpeg subprocess using the following parameters:
- **`-y`**: Overwrites output files if they exist.
- **`-i <video_path>`**: Specifies the source video.
- **`-vn`**: Blocks video stream extraction (we only want audio).
- **`-acodec pcm_s16le`**: Codes audio using 16-bit little-endian PCM inside the WAV container.
- **`-ar 16000`**: Sets the sample rate to 16 kHz.
- **`-ac 1`**: Sets the channel count to 1 (mono).

### New Module Files

1. **[ffmpeg.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/utils/ffmpeg.py)**: Verifies that FFmpeg is callable on the host machine and executes subprocess calls safely with timeouts.
2. **[audio_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/audio_service.py)**: Orchestrates business checks (such as verifying video database records and file existences on disk) and runs the extraction.
3. **[audio.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/audio.py)**: Defines request payload schemas (`AudioExtractRequest`) and response bodies (`AudioExtractResponse`).
4. **[audio.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/audio.py)**: Declares the `POST /api/v1/audio/extract` endpoint router.

### REST API Documentation

#### Extract Audio from Video
- **Endpoint**: `POST /api/v1/audio/extract`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "video_id": "bfcc4358-81da-4007-b44f-afb451940e64"
  }
  ```
- **Validations Enforced**:
  - **Record Check**: Verifies if the `video_id` exists in SQLite database. (Returns `HTTP 404 Not Found` if missing).
  - **Disk Presence Check**: Verifies if the corresponding video file is present in physical storage. (Returns `HTTP 404 Not Found` if missing).
  - **Tool Availability Check**: Verifies that the FFmpeg executable is available and running on the host system. (Returns `HTTP 500 Internal Server Error` if missing).
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "audio_id": "8c257d90-349f-43b6-96cb-52ebc689d0c2",
    "audio_path": "backend/temp/audio/8c257d90-349f-43b6-96cb-52ebc689d0c2.wav",
    "duration": 12.4,
    "sample_rate": 16000,
    "channels": 1,
    "status": "completed"
  }
  ```

---

## License
MIT
