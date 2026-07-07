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
- **Milestone 4**: Speech-to-Text transcription with Faster-Whisper. (Completed)
- **Milestone 5**: Word-level alignment with WhisperX. (Completed)
- **Milestone 6**: Subtitle generation engine. (Completed)
- **Milestone 7**: Caption style engine. (Completed)
- **Milestone 8**: Caption animation engine. (Completed)
- **Milestone 9**: Video rendering with stylized and animated captions.
- **Milestone 10**: Frontend UI development (React + TypeScript + Tailwind CSS).
- **Milestone 11**: Database integrations, user history, and job queue.
- **Milestone 12**: Deployment, Dockerization, and CI/CD pipelines.

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

## Speech Recognition Architecture (Milestone 4)

We implement a highly optimized AI Speech Recognition Service using Faster-Whisper, loaded once on application startup as a cached singleton for maximum speed.

### How Faster-Whisper Works

Faster-Whisper is a reimplementation of OpenAI's Whisper model using **CTranslate2**, a fast inference engine for Transformer models. It optimizes execution via several techniques:
1. **Weight Quantization**: Converts float32 parameters to float16 or 8-bit integers (int8). This reduces model size by up to 4x and accelerates CPU and GPU calculations with minimal loss in word error rate (WER).
2. **Layer Fusion & Memory Reusage**: Fuses successive neural network operations (like matrix multiplication and activation layers) to minimize memory access overhead.
3. **C++ Execution Engine**: Leverages optimized BLAS libraries (Intel MKL, OpenBLAS) for matrix operations on CPU, bypassing Python global interpreter lock (GIL) and runtime overhead.

### Model Loading Singleton Pattern

Loading neural networks from disk is a heavy task that takes several seconds and consumes significant RAM. We implement a **Cached Singleton Pattern** inside `TranscriptionService`:
- On application startup (FastAPI `lifespan` initialization), the `TranscriptionService.load_model()` method is invoked.
- It parses configurations (`WHISPER_MODEL`, `DEVICE`, `COMPUTE_TYPE` from environment variables) and loads the Whisper model once.
- Subscriptions/transcription requests reuse the pre-loaded instance, bringing request latency down from several seconds to instantaneous inference.

### New Module Files

1. **[transcription_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/transcription_service.py)**: Manages class-level singleton caching for the loaded model and executes transcription segments mapping.
2. **[transcription.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/transcription.py)**: Defines request body schemas (`TranscriptionRequest`) and responses (`TranscriptionResponse`).
3. **[transcription.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/transcription.py)**: Exposes the `POST /api/v1/transcribe` endpoint route.

### REST API Documentation

#### Transcribe Audio to Text
- **Endpoint**: `POST /api/v1/transcribe`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "audio_id": "8c257d90-349f-43b6-96cb-52ebc689d0c2"
  }
  ```
- **Validations Enforced**:
  - **Presence Check**: Verifies if the WAV file corresponding to `audio_id` exists in the local directory. (Returns `HTTP 404 Not Found` if missing).
  - **Model State Check**: Verifies model loaded status. (Returns `HTTP 500 Internal Server Error` if initialization failed).
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "id": "bfcc4358-81da-4007-b44f-afb451940e64",
    "language": "en",
    "duration": 35.4,
    "processing_time": 2.1,
    "segments": [
      {
        "start": 0.0,
        "end": 2.5,
        "text": "Hello everyone."
      },
      {
        "start": 2.5,
        "end": 5.0,
        "text": "Welcome back."
      }
    ],
    "status": "completed"
  }
  ```

---

## Word Alignment Architecture (Milestone 5)

We implement a production-grade Word Alignment Service using WhisperX to generate precise word-level timestamps.

### What WhisperX Does

WhisperX builds upon Whisper by incorporating phoneme alignment. While standard Whisper models only yield coarse segment-level timestamps (often spanning several words or seconds), WhisperX utilizes a phonetic alignment model (typically a Wav2Vec2 framework trained on phonemes) to align individual character/word boundaries precisely against the raw audio waveform.

### Difference Between Faster-Whisper and WhisperX

1. **Faster-Whisper**: A fast transformer implementation focusing on ASR (Automatic Speech Recognition) execution speed and RAM footprint optimization via CTranslate2. It is highly optimized for converting speech to text segments, but its timestamps are segment-level and can drift.
2. **WhisperX**: Focuses on micro-precision word boundaries. It takes the text segment outputs (from ASR engines like Faster-Whisper) and uses a Wav2Vec2 model to phonetically map each individual word's start and end times to the milliseconds of the audio track.

### Why Word-Level Timestamps are Required

State-of-the-art subtitle systems require micro-precision word timestamps to:
- Render animated word-by-word active coloring (e.g., karaoke-style captions popular on social media).
- Avoid lag between voice onset and text rendering.
- Dynamically split text segments into clean, readable lines without breaking sentences in half.

### New Module Files

1. **[transcript.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/models/transcript.py)**: Declares database schemas (`Transcript` and `TranscriptSegment`) to persist transcript runs and enable segment retrieval by UUID.
2. **[alignment_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/alignment_service.py)**: Manages class-level cached dictionary of WhisperX alignment models per language and runs the phonetic alignment process.
3. **[alignment.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/alignment.py)**: Defines request payload schemas (`AlignmentRequest`) and responses (`AlignmentResponse`).
4. **[alignment.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/alignment.py)**: Exposes the `POST /api/v1/align` endpoint router.

### REST API Documentation

#### Align Transcript to Audio Waveform
- **Endpoint**: `POST /api/v1/align`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "audio_id": "8c257d90-349f-43b6-96cb-52ebc689d0c2",
    "transcript_id": "9a12b456-78c9-0d12-e34f-5678ab9012cd"
  }
  ```
- **Validations Enforced**:
  - **Transcript Check**: Verifies the `transcript_id` exists in the database. (Returns `HTTP 404 Not Found` if missing).
  - **Audio Check**: Verifies the wav file exists on disk. (Returns `HTTP 404 Not Found` if missing).
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
    "language": "en",
    "duration": 35.2,
    "words": [
      {
        "word": "Hello",
        "start": 0.01,
        "end": 0.45,
        "confidence": 0.99
      },
      {
        "word": "everyone",
        "start": 0.45,
        "end": 0.90,
        "confidence": 0.98
      }
    ],
    "status": "completed"
  }
  ```

---

## Subtitle Generation Architecture (Milestone 6)

We implement a production-grade Subtitle Generation Engine supporting JSON, SRT, and Advanced SubStation Alpha (ASS) formats.

### Difference Between Subtitle Formats

1. **JSON Format**: A custom structured representation of words and captions. It retains word-level properties (confidence, line_index, caption_index) and is optimized for front-end rendering engines or custom databases.
2. **SRT Format (SubRip)**: The most widely supported, lightweight subtitle format. It uses sequential numbering and simple `HH:MM:SS,mmm` timestamp blocks. It is pure text and supports minimal styling.
3. **ASS Format (Advanced SubStation Alpha)**: A highly advanced, programmable subtitle format. It contains stylesheet definitions (font family, colors, shadows, borders, alignments) and supports complex layout positioning and karaoke-style text animation effects.

### Subtitle Segmentation Strategy

To ensure natural readability, we group raw words into structured caption blocks using the following rules:
- **Punctuation Awareness**: Natural splits are triggered at sentence boundaries (`.`, `?`, `!`) and weak punctuation pauses (`,`, `;`, `:`) to match the speaker's cadence.
- **Duration/Pause Detection**: Large silences between words (> 1.0s) trigger automatic caption splits.
- **Line Balancing**: Captions are limited to `2` lines and a configurable words-per-line maximum (default: `5`). If a caption block spans multiple lines, the words are evenly divided (balanced) in half to avoid leaving single words on a line.
- **Reading Speed Limits**: Ensures captions do not flash too fast. If a caption has a duration shorter than the required reading speed threshold (characters per second, default `18`), the start and end times are expanded outward (left and right) safely without overlapping adjacent captions.

### New Module Files

1. **[subtitle_builder.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/subtitle_builder.py)**: Grouping algorithm managing unaligned word interpolation, segment divisions, and reading speed expansions.
2. **[subtitle_formatter.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/subtitle_formatter.py)**: Serializes caption structures into valid SRT time blocks, ASS stylesheet event layers, and custom JSON trees.
3. **[subtitle_exporter.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/subtitle_exporter.py)**: Exporter pipeline writing output content to `backend/outputs/subtitles/` using UTF-8, handling write errors safely.
4. **[subtitle_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/subtitle_service.py)**: Orchestrates retrieval of alignments from the database, runs builder, and writes the requested formats.
5. **[subtitle.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/subtitle.py)**: Declares API validation schemas for requests and responses.
6. **[subtitle.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/subtitle.py)**: Exposes the `POST /api/v1/subtitles/generate` route.

### REST API Documentation

#### Generate Subtitle Files
- **Endpoint**: `POST /api/v1/subtitles/generate`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "alignment_id": "8c257d90-349f-43b6-96cb-52ebc689d0c2",
    "style": "default",
    "max_words_per_line": 5,
    "max_lines": 2,
    "output_formats": ["json", "srt", "ass"]
  }
  ```
- **Validations Enforced**:
  - **Alignment Presence Check**: Verifies if the `alignment_id` is registered in the database. (Returns `HTTP 404 Not Found` if missing).
  - **Layout Parameters**: Enforces constraints (`max_words_per_line` between 1-20, `max_lines` between 1-5).
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "subtitle_files": {
      "json": "backend/outputs/subtitles/8c257d90-349f-43b6-96cb-52ebc689d0c2.json",
      "srt": "backend/outputs/subtitles/8c257d90-349f-43b6-96cb-52ebc689d0c2.srt",
      "ass": "backend/outputs/subtitles/8c257d90-349f-43b6-96cb-52ebc689d0c2.ass"
    },
    "caption_count": 58,
    "status": "completed"
  }
  ```

---

## Caption Style Engine Architecture (Milestone 7)

We implement a decoupled **Caption Style Engine** that defines visual presentation presets (font sizes, text spacing, outlines, background boxes) and text rendering effects (case transformations, auto emoji injections) with responsive resolution scaling.

### Supported Presets & Configs
The engine loads style properties dynamically from JSON files stored on disk. Predefined styles include:
- **TikTok**: Bold, uppercase Montserrat font, cyan outline, high-contrast black background box, and emojis enabled.
- **Instagram**: Bold, titlecase Proxima Nova font, magenta highlight color.
- **YouTube Shorts**: Bold Roboto font, red highlight, moderate safe margins.
- **Podcast**: Regular Georgia font, soft gold highlight color, wide spacing for high-end feel.
- **Alex Hormozi**: Extremely large uppercase yellow Impact font with a heavy black outline, green word-highlights, and emojis.
- **MrBeast**: Bold, uppercase Futura font, yellow highlights, cyan outlines, and emojis.
- **Minimal**: Simple white Arial font, bottom-center alignment, no boxes or outline clutter.
- **Cinema**: High letter-spacing Times New Roman font, safe layout margins.
- **Gaming**: Bright green uppercase Orbitron font, background box, left alignment.
- **Documentary**: Clean Helvetica font, bottom-left aligned background block.

### Responsive Design & Auto-Scaling
Visual attributes automatically adapt proportionally based on video dimensions and aspect ratio layout to maintain identical relative sizes on export:
- **Scaling Factor**: Calculated relative to base 1080p standard reference frames (e.g. 1080 width for vertical, 1920 width for horizontal).
- **Scaled Attributes**: Proportional adjustments are made to `font_size`, `outline_width`, `shadow_offset`, `padding`, `border_radius`, and `safe_margin`.

### Custom User Styles
Users can define customized style sheets through the API. The custom configuration is validated against the Pydantic schema and saved on disk in `backend/app/styles/custom/`. It is instantly available in the listing of styles.

### New Module Files
1. **[caption_style.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/caption_style.py)**: Decoupled Pydantic model schemas validating HEX color patterns, safe dimensions bounds, and request/response payloads.
2. **[style_loader.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/style_loader.py)**: Dynamic loader class scanning directory folders, verifying JSON syntax, and writing custom profiles to disk.
3. **[style_manager.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/style_manager.py)**: Formatting manager applying casing transformations (uppercase, lowercase, titlecase), sentence auto capitalization, and emoji mapping injections (e.g. "fire" -> "🔥"). Also implements the layout scaling helper.
4. **[caption_style_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/caption_style_service.py)**: Orchestrator service routing raw caption sequences to loaders and formatters.
5. **[caption_style.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/caption_style.py)**: Exposes endpoint paths to apply styles, fetch files, and register custom profiles.

---

### REST API Documentation

#### 1. List Available Caption Styles
- **Endpoint**: `GET /api/v1/styles`
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  [
    "cinema",
    "default",
    "documentary",
    "gaming",
    "hormozi",
    "instagram",
    "mrbeast",
    "podcast",
    "tiktok",
    "youtube"
  ]
  ```

#### 2. Create Custom Style Sheet
- **Endpoint**: `POST /api/v1/styles/custom`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "style_name": "my_brand_style",
    "style_properties": {
      "font_family": "Futura",
      "font_size": 24.0,
      "font_weight": "bold",
      "text_color": "#FF5500",
      "highlight_color": "#00FF55",
      "outline_color": "#000000",
      "outline_width": 2.0,
      "shadow_color": "#000000",
      "shadow_offset_x": 1.0,
      "shadow_offset_y": 1.0,
      "background_box": true,
      "background_color": "#111111",
      "background_opacity": 0.8,
      "border_radius": 4.0,
      "padding": 8.0,
      "line_spacing": 1.3,
      "letter_spacing": 0.5,
      "safe_margin": 15.0,
      "vertical_position": "bottom",
      "horizontal_position": "center",
      "max_width_pct": 75.0,
      "alignment": "center",
      "opacity": 1.0,
      "text_effects": {
        "case": "uppercase",
        "word_highlight": "current",
        "auto_capitalization": true,
        "auto_emoji": true
      }
    }
  }
  ```
- **Successful Response (`HTTP 201 Created`)**:
  ```json
  {
    "message": "Custom style 'my_brand_style' created successfully",
    "filepath": "backend/app/styles/custom/my_brand_style.json"
  }
  ```

#### 3. Apply Style Configuration
- **Endpoint**: `POST /api/v1/styles/apply`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "style_name": "tiktok",
    "width": 1080,
    "height": 1920,
    "aspect_ratio": "vertical",
    "subtitles": [
      {
        "index": 1,
        "start": 0.0,
        "end": 2.0,
        "text": "this is a cool fire game",
        "words": [
          {"word": "this", "start": 0.0, "end": 0.3},
          {"word": "is", "start": 0.3, "end": 0.6},
          {"word": "a", "start": 0.6, "end": 0.8},
          {"word": "cool", "start": 0.8, "end": 1.2},
          {"word": "fire", "start": 1.2, "end": 1.6},
          {"word": "game", "start": 1.6, "end": 2.0}
        ]
      }
    ]
  }
  ```
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "style_name": "tiktok",
    "width": 1080,
    "height": 1920,
    "aspect_ratio": "vertical",
    "style_properties": {
      "font_family": "Montserrat",
      "font_size": 28.0,
      "font_weight": "bold",
      "text_color": "#FFFFFF",
      "highlight_color": "#00FFFF",
      "outline_color": "#000000",
      "outline_width": 2.5,
      "shadow_color": "#FF007F",
      "shadow_offset_x": 2.0,
      "shadow_offset_y": 2.0,
      "background_box": true,
      "background_color": "#000000",
      "background_opacity": 0.7,
      "border_radius": 8.0,
      "padding": 12.0,
      "line_spacing": 1.3,
      "letter_spacing": 0.5,
      "safe_margin": 15.0,
      "vertical_position": "center",
      "horizontal_position": "center",
      "max_width_pct": 75.0,
      "alignment": "center",
      "opacity": 1.0,
      "text_effects": {
        "case": "uppercase",
        "word_highlight": "current",
        "auto_capitalization": true,
        "auto_emoji": true
      }
    },
    "styled_subtitles": [
      {
        "index": 1,
        "start": 0.0,
        "end": 2.0,
        "text": "THIS IS A COOL 😎 FIRE 🔥 GAME 🎮",
        "words": [
          {"word": "THIS", "start": 0.0, "end": 0.3},
          {"word": "IS", "start": 0.3, "end": 0.6},
          {"word": "A", "start": 0.6, "end": 0.8},
          {"word": "COOL 😎", "start": 0.8, "end": 1.2},
          {"word": "FIRE 🔥", "start": 1.2, "end": 1.6},
          {"word": "GAME 🎮", "start": 1.6, "end": 2.0}
        ]
      }
    ]
  }
  ```

---

## Caption Animation Engine Architecture (Milestone 8)

We implement a production-grade **Caption Animation Engine** that generates animation timelines and transition keyframes for subtitles and individual words.

### Decoupling Animations from Rendering
To keep rendering nodes lightweight and highly performant, all animation configurations (keyframes, displacement offsets, opacity levels, color transitions, scales) are calculated as pure data parameters inside the backend. The renderer (e.g. FFmpeg, HTML5 canvas, or WebGL) simply consumes this JSON timeline on playback or export without needing to run complex timing generators or styling logic locally.

### Keyframe Easing System
Transition keyframes are generated utilizing standard mathematical easing curves to ensure smooth and fluid visual movement:
- **Linear**: Constant change rate.
- **Ease In / Ease Out / Ease In Out**: Smooth acceleration and deceleration using quadratic/cubic curves.
- **Bounce**: Rebound effect when settling into target states.
- **Elastic**: Overshooting spring oscillation effect.

### Supported Animation Presets
The engine maps visual effects to coordinate changes and timings during a word's spoken window:
- **Word Highlight**: Active word transitions to the configured highlight color during its timeframe.
- **Word Pop**: Proportional scale pops from 1.0 to 1.35 and settles back.
- **Word Fade**: Opacity fades in from 0.0 to 1.0.
- **Word Bounce**: Vertical displacement coordinates bounce upwards (`-15.0px`).
- **Word Slide / Rotate**: Translates horizontally or rotates by specified angle offsets.
- **Zoom In / Out**: Spans scale values between 0.0 and 1.0.

### Performance Caching
A memory cache is integrated inside the manager. It keys generated sequences by MD5 hashes of combined inputs (subtitle lists, style configuration fields, preset codes), guaranteeing instant lookup hits for duplicated sequences while protecting memory limits.

### New Module Files
1. **[animation.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/schemas/animation.py)**: Validation models specifying request payloads, frame transitions, and nested animated segment outputs.
2. **[keyframe_generator.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/animations/keyframe_generator.py)**: Easing math library calculating progress curves (Elastic, Bounce, Cubic).
3. **[animation_presets.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/animations/animation_presets.py)**: Preset structures mapping pop scales, fade opacities, and gold highlights to word boundaries.
4. **[timeline_generator.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/animations/timeline_generator.py)**: Timings helper evaluating maximum duration bounds.
5. **[animation_engine.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/animations/animation_engine.py)**: Sequence compiler compiling words and preset layouts into frame lists.
6. **[animation_manager.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/animations/animation_manager.py)**: Memory manager utilizing MD5 hashes to cache computed runs.
7. **[animation_service.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/services/animation_service.py)**: Orchestrator service routing request parameters.
8. **[animation.py](file:///c:/Users/Om%20Pathare/OneDrive/Documents/AI%20CAPTION/backend/app/api/v1/endpoints/animation.py)**: Exposes routes `GET /api/v1/animations` and `POST /api/v1/animations/apply`.

---

### REST API Documentation

#### 1. List Available Animations
- **Endpoint**: `GET /api/v1/animations`
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  [
    "word_highlight",
    "word_pop",
    "word_scale",
    "word_fade",
    "word_bounce",
    "word_slide",
    "word_rotate",
    "word_blur",
    "letter_animation",
    "character_animation",
    "sentence_fade",
    "sentence_pop",
    "karaoke_highlight",
    "progress_fill",
    "opacity_fade",
    "zoom_in",
    "zoom_out"
  ]
  ```

#### 2. Apply Animation Keyframes
- **Endpoint**: `POST /api/v1/animations/apply`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "subtitles": [
      {
        "index": 1,
        "start": 0.0,
        "end": 2.0,
        "text": "hello world",
        "words": [
          {"word": "hello", "start": 0.1, "end": 0.8},
          {"word": "world", "start": 0.9, "end": 1.7}
        ]
      }
    ],
    "style": {
      "font_family": "Arial",
      "font_size": 24.0,
      "font_weight": "normal",
      "text_color": "#FFFFFF",
      "highlight_color": "#FFFF00",
      "outline_color": "#000000",
      "text_effects": {
        "case": "normal",
        "word_highlight": "current",
        "auto_capitalization": true,
        "auto_emoji": false
      }
    },
    "animation_preset": "word_highlight"
  }
  ```
- **Successful Response (`HTTP 200 OK`)**:
  ```json
  {
    "animation_preset": "word_highlight",
    "duration": 2.0,
    "animated_subtitles": [
      {
        "index": 1,
        "start": 0.0,
        "end": 2.0,
        "text": "hello world",
        "words": [
          {
            "word": "hello",
            "start": 0.1,
            "end": 0.8,
            "animation_type": "word_highlight",
            "scale": 1.0,
            "opacity": 1.0,
            "rotation": 0.0,
            "position_x": 0.0,
            "position_y": 0.0,
            "color": "#FFFFFF",
            "highlight_color": "#FFFF00",
            "shadow_color": "#000000",
            "keyframes": [
              {"time": 0.09, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFFFF"},
              {"time": 0.1, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFF00"},
              {"time": 0.8, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFF00"},
              {"time": 0.81, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFFFF"}
            ]
          },
          {
            "word": "world",
            "start": 0.9,
            "end": 1.7,
            "animation_type": "word_highlight",
            "scale": 1.0,
            "opacity": 1.0,
            "rotation": 0.0,
            "position_x": 0.0,
            "position_y": 0.0,
            "color": "#FFFFFF",
            "highlight_color": "#FFFF00",
            "shadow_color": "#000000",
            "keyframes": [
              {"time": 0.89, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFFFF"},
              {"time": 0.9, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFF00"},
              {"time": 1.7, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFF00"},
              {"time": 1.71, "scale": 1.0, "opacity": 1.0, "rotation": 0.0, "position_x": 0.0, "position_y": 0.0, "color": "#FFFFFF"}
            ]
          }
        ]
      }
    ]
  }
  ```

---

## License
MIT
