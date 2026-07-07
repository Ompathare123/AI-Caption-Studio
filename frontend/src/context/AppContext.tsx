import React, { createContext, useContext, useState, useEffect } from "react";
import type {
  VideoMetadata,
  AudioMetadata,
  TranscriptionResponse,
  AlignmentResponse,
  SubtitleResponse,
} from "../services/api";

export interface StyleConfig {
  font_family: string;
  font_size: number;
  font_weight: string;
  text_color: string;
  highlight_color: string;
  outline_color: string;
  outline_width: number;
  shadow_color: string;
  shadow_offset_x: number;
  shadow_offset_y: number;
  background_box: boolean;
  background_color: string;
  background_opacity: number;
  border_radius: number;
  padding: number;
  line_spacing: number;
  letter_spacing: number;
  vertical_position: "top" | "center" | "bottom";
  horizontal_position: "left" | "center" | "right";
  alignment: "left" | "center" | "right";
  safe_margin: number;
}

export const defaultStyle: StyleConfig = {
  font_family: "Arial",
  font_size: 24,
  font_weight: "normal",
  text_color: "#FFFFFF",
  highlight_color: "#FFFF00",
  outline_color: "#000000",
  outline_width: 2,
  shadow_color: "#000000",
  shadow_offset_x: 0,
  shadow_offset_y: 0,
  background_box: false,
  background_color: "#000000",
  background_opacity: 0.5,
  border_radius: 4,
  padding: 8,
  line_spacing: 1.2,
  letter_spacing: 0,
  vertical_position: "bottom",
  horizontal_position: "center",
  alignment: "center",
  safe_margin: 50,
};

interface AppContextProps {
  currentVideo: VideoMetadata | null;
  setCurrentVideo: (video: VideoMetadata | null) => void;
  currentAudio: AudioMetadata | null;
  setCurrentAudio: (audio: AudioMetadata | null) => void;
  currentTranscription: TranscriptionResponse | null;
  setCurrentTranscription: (
    transcription: TranscriptionResponse | null
  ) => void;
  currentAlignment: AlignmentResponse | null;
  setCurrentAlignment: (alignment: AlignmentResponse | null) => void;
  currentSubtitle: SubtitleResponse | null;
  setCurrentSubtitle: (subtitle: SubtitleResponse | null) => void;
  activeStylePreset: string;
  setActiveStylePreset: (preset: string) => void;
  activeStyle: StyleConfig;
  updateActiveStyle: (updates: Partial<StyleConfig>) => void;
  activeAnimation: string;
  setActiveAnimation: (anim: string) => void;
  renderId: string | null;
  setRenderId: (id: string | null) => void;
  recentVideos: VideoMetadata[];
  saveVideoToRecent: (video: VideoMetadata) => void;
}

const AppContext = createContext<AppContextProps | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [currentVideo, setCurrentVideo] = useState<VideoMetadata | null>(null);
  const [currentAudio, setCurrentAudio] = useState<AudioMetadata | null>(null);
  const [currentTranscription, setCurrentTranscription] =
    useState<TranscriptionResponse | null>(null);
  const [currentAlignment, setCurrentAlignment] =
    useState<AlignmentResponse | null>(null);
  const [currentSubtitle, setCurrentSubtitle] =
    useState<SubtitleResponse | null>(null);

  const [activeStylePreset, setActiveStylePreset] = useState<string>("default");
  const [activeStyle, setActiveStyle] = useState<StyleConfig>(defaultStyle);
  const [activeAnimation, setActiveAnimation] =
    useState<string>("word_highlight");
  const [renderId, setRenderId] = useState<string | null>(null);
  const [recentVideos, setRecentVideos] = useState<VideoMetadata[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem("recent_videos");
    if (stored) {
      try {
        setRecentVideos(JSON.parse(stored));
      } catch (e) {
        // ignore
      }
    }
  }, []);

  const saveVideoToRecent = (video: VideoMetadata) => {
    setRecentVideos((prev) => {
      const filtered = prev.filter((v) => v.id !== video.id);
      const updated = [video, ...filtered].slice(0, 20);
      localStorage.setItem("recent_videos", JSON.stringify(updated));
      return updated;
    });
  };

  const updateActiveStyle = (updates: Partial<StyleConfig>) => {
    setActiveStyle((prev) => ({ ...prev, ...updates }));
  };

  return (
    <AppContext.Provider
      value={{
        currentVideo,
        setCurrentVideo,
        currentAudio,
        setCurrentAudio,
        currentTranscription,
        setCurrentTranscription,
        currentAlignment,
        setCurrentAlignment,
        currentSubtitle,
        setCurrentSubtitle,
        activeStylePreset,
        setActiveStylePreset,
        activeStyle,
        updateActiveStyle,
        activeAnimation,
        setActiveAnimation,
        renderId,
        setRenderId,
        recentVideos,
        saveVideoToRecent,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
