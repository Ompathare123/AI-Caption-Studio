import axios from "axios";

// Standard Backend FastAPI base URL
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 600000, // 10 minutes timeout for heavy transcription or rendering tasks
});

export interface VideoMetadata {
  id: string;
  filename: string;
  size: number;
  duration: number;
  status: string;
}

export interface AudioMetadata {
  id: string;
  video_id: string;
  filepath: string;
  duration: number;
}

export interface TranscriptionSegment {
  text: string;
  start: number;
  end: number;
}

export interface TranscriptionResponse {
  id: string;
  audio_id: string;
  text: string;
  segments: TranscriptionSegment[];
}

export interface WordAlignment {
  word: string;
  start: number;
  end: number;
  score: number;
}

export interface AlignmentSegment {
  text: string;
  start: number;
  end: number;
  words: WordAlignment[];
}

export interface AlignmentResponse {
  id: string;
  audio_id: string;
  transcript_id: string;
  segments: AlignmentSegment[];
}

export interface SubtitleResponse {
  id: string;
  subtitle_files: {
    json: string;
    srt: string;
    ass: string;
  };
}

export interface RenderStatusResponse {
  render_id: string;
  status: string;
  progress: number;
  output_path: string | null;
  error_message: string | null;
}

export const apiService = {
  /**
   * Upload video binary file
   */
  uploadVideo: async (
    file: File,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<VideoMetadata> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post<VideoMetadata>("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
    return response.data;
  },

  /**
   * Extract audio channel from video file
   */
  extractAudio: async (videoId: string): Promise<AudioMetadata> => {
    const response = await api.post<AudioMetadata>("/audio/extract", {
      video_id: videoId,
    });
    return response.data;
  },

  /**
   * Transcribe extracted audio file using Faster-Whisper
   */
  transcribeAudio: async (audioId: string): Promise<TranscriptionResponse> => {
    const response = await api.post<TranscriptionResponse>("/transcribe", {
      audio_id: audioId,
    });
    return response.data;
  },

  /**
   * Align audio and transcripts at the word level using WhisperX Wav2Vec2
   */
  alignTranscript: async (
    audioId: string,
    transcriptId: string
  ): Promise<AlignmentResponse> => {
    const response = await api.post<AlignmentResponse>("/align", {
      audio_id: audioId,
      transcript_id: transcriptId,
    });
    return response.data;
  },

  /**
   * Generate subtitle files (SRT, ASS, JSON formats)
   */
  generateSubtitles: async (
    alignmentId: string,
    format = "json"
  ): Promise<SubtitleResponse> => {
    const response = await api.post<SubtitleResponse>("/subtitles/generate", {
      alignment_id: alignmentId,
      format,
    });
    return response.data;
  },

  /**
   * Fetch pre-compiled style templates list
   */
  listStyles: async (): Promise<string[]> => {
    const response = await api.get<string[]>("/styles");
    return response.data;
  },

  /**
   * Fetch supported animation presets
   */
  listAnimations: async (): Promise<string[]> => {
    const response = await api.get<string[]>("/animations");
    return response.data;
  },

  /**
   * Trigger captions video rendering task
   */
  startRender: async (
    videoId: string,
    subtitleId: string,
    styleName: string,
    animationPreset: string
  ): Promise<RenderStatusResponse> => {
    const response = await api.post<RenderStatusResponse>("/render", {
      video_id: videoId,
      subtitle_id: subtitleId,
      style_name: styleName,
      animation_preset: animationPreset,
    });
    return response.data;
  },

  /**
   * Get rendering status progress
   */
  getRenderStatus: async (renderId: string): Promise<RenderStatusResponse> => {
    const response = await api.get<RenderStatusResponse>(`/render/${renderId}`);
    return response.data;
  },

  /**
   * Build backend static media file resource URL
   */
  getMediaUrl: (path: string | null): string => {
    if (!path) return "";
    // If output path is returned relative or absolute, normalize it
    const cleanPath = path.replace(/\\/g, "/");
    // Check if the backend returns static files server paths
    if (cleanPath.startsWith("backend/")) {
      return `http://localhost:8000/static/${cleanPath.substring(8)}`;
    }
    if (cleanPath.startsWith("outputs/")) {
      return `http://localhost:8000/static/${cleanPath}`;
    }
    return `http://localhost:8000/static/${cleanPath}`;
  },
};
