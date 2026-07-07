import axios from "axios";

// Standard Backend FastAPI base URL
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 600000,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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

export interface ProjectResponse {
  id: string;
  user_id: string | null;
  video_id: string;
  name: string;
  is_favorite: boolean;
  captions_data: AlignmentSegment[];
  style_data: any;
  animation_preset: string;
  created_at: string;
  updated_at: string;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  language: string;
  timezone: string;
  created_at: string;
}

export interface JobResponse {
  id: string;
  project_id: string;
  status: string;
  progress: number;
  current_step: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
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

  /**
   * Create/Initialize a timeline editing project
   */
  createProject: async (
    videoId: string,
    subtitleId?: string
  ): Promise<ProjectResponse> => {
    const response = await api.post<ProjectResponse>("/projects", {
      video_id: videoId,
      subtitle_id: subtitleId,
    });
    return response.data;
  },

  /**
   * Load project metadata and captions timeline
   */
  loadProject: async (projectId: string): Promise<ProjectResponse> => {
    const response = await api.get<ProjectResponse>(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Save caption adjustments and styles to project
   */
  saveProject: async (
    projectId: string,
    updateData: {
      captions_data: AlignmentSegment[];
      style_data: any;
      animation_preset: string;
    }
  ): Promise<ProjectResponse> => {
    return apiService.updateProject(projectId, updateData);
  },

  /**
   * Update project fields (e.g. rename, favorite, style, captions)
   */
  updateProject: async (
    projectId: string,
    updateData: {
      captions_data?: AlignmentSegment[];
      style_data?: any;
      animation_preset?: string;
      name?: string;
      is_favorite?: boolean;
    }
  ): Promise<ProjectResponse> => {
    const response = await api.put<ProjectResponse>(
      `/projects/${projectId}`,
      updateData
    );
    return response.data;
  },

  /**
   * Submit background caption alignment job
   */
  createJob: async (projectId: string): Promise<JobResponse> => {
    const response = await api.post<JobResponse>("/jobs", {
      project_id: projectId,
    });
    return response.data;
  },

  /**
   * Get background job details
   */
  getJob: async (jobId: string): Promise<JobResponse> => {
    const response = await api.get<JobResponse>(`/jobs/${jobId}`);
    return response.data;
  },

  /**
   * Cancel running background job
   */
  cancelJob: async (jobId: string): Promise<any> => {
    const response = await api.delete(`/jobs/${jobId}`);
    return response.data;
  },

  /**
   * Build WebSocket url for progress updates channel
   */
  getJobProgressWsUrl: (jobId: string): string => {
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = "localhost:8000"; // backend default port mapping
    return `${wsProto}//${host}/api/v1/jobs/${jobId}/progress`;
  },

  /**
   * List all projects belonging to logged in user
   */
  listProjects: async (): Promise<ProjectResponse[]> => {
    const response = await api.get<ProjectResponse[]>("/projects");
    return response.data;
  },

  /**
   * Delete project
   */
  deleteProject: async (projectId: string): Promise<any> => {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Duplicate project
   */
  duplicateProject: async (projectId: string): Promise<ProjectResponse> => {
    const response = await api.post<ProjectResponse>(`/projects/${projectId}/duplicate`);
    return response.data;
  },

  /**
   * Register new user account
   */
  registerUser: async (payload: any): Promise<UserResponse> => {
    const response = await api.post<UserResponse>("/auth/register", payload);
    return response.data;
  },

  /**
   * Authenticate user credentials and create session cookies
   */
  loginUser: async (payload: any): Promise<any> => {
    const response = await api.post("/auth/login", payload);
    return response.data;
  },

  /**
   * Destroy user session and clear cookies
   */
  logoutUser: async (): Promise<any> => {
    const response = await api.post("/auth/logout");
    return response.data;
  },

  /**
   * Reissue access tokens using refresh token cookies
   */
  refreshTokens: async (): Promise<any> => {
    const response = await api.post("/auth/refresh");
    return response.data;
  },

  /**
   * Retrieve current user profile
   */
  getMe: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>("/users/me");
    return response.data;
  },

  /**
   * Update user profile settings
   */
  updateMe: async (payload: any): Promise<UserResponse> => {
    const response = await api.put<UserResponse>("/users/me", payload);
    return response.data;
  },
};
