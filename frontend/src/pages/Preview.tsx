import React, { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useApp, defaultStyle } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService } from "../services/api";
import Layout from "../components/Layout";
import { PlayIcon, PauseIcon, SparklesIcon } from "@heroicons/react/24/solid";

const Preview: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentVideo,
    currentAlignment,
    currentSubtitle,
    activeStylePreset,
    setActiveStylePreset,
    activeStyle,
    updateActiveStyle,
    activeAnimation,
    setActiveAnimation,
    setRenderId,
  } = useApp();

  const { showToast } = useToast();
  const videoRef = useRef<HTMLVideoElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [rendering, setRendering] = useState(false);

  // Available font presets
  const fontPresets = [
    "Arial",
    "Impact",
    "Montserrat",
    "Roboto",
    "Georgia",
    "Times New Roman",
    "Orbitron",
  ];

  // List of visual style presets
  const stylePresets = [
    {
      id: "default",
      name: "Default Minimal",
      config: {
        ...defaultStyle,
        font_family: "Arial",
        text_color: "#FFFFFF",
        highlight_color: "#3B82F6",
        background_box: false,
      },
    },
    {
      id: "tiktok",
      name: "TikTok Classic",
      config: {
        ...defaultStyle,
        font_family: "Montserrat",
        text_color: "#FFFFFF",
        highlight_color: "#FFFF00",
        background_box: true,
        background_color: "#000000",
        background_opacity: 0.8,
        border_radius: 6,
        padding: 10,
      },
    },
    {
      id: "mrbeast",
      name: "MrBeast Gaming",
      config: {
        ...defaultStyle,
        font_family: "Impact",
        font_size: 32,
        text_color: "#FFFFFF",
        highlight_color: "#FFFF00",
        outline_color: "#000000",
        outline_width: 3,
        shadow_color: "#000000",
        shadow_offset_x: 4,
        shadow_offset_y: 4,
      },
    },
    {
      id: "hormozi",
      name: "Alex Hormozi",
      config: {
        ...defaultStyle,
        font_family: "Montserrat",
        font_weight: "bold",
        font_size: 28,
        text_color: "#FFFFFF",
        highlight_color: "#10B981",
        outline_color: "#000000",
        outline_width: 2,
      },
    },
  ];

  // Standard animation presets list
  const animationPresets = [
    { id: "word_highlight", name: "Word Highlight" },
    { id: "word_pop", name: "Pop Zoom" },
    { id: "word_bounce", name: "Vertical Bounce" },
    { id: "word_fade", name: "Fade In" },
    { id: "word_rotate", name: "Rotate Spin" },
    { id: "zoom_in", name: "Zoom In" },
    { id: "zoom_out", name: "Zoom Out" },
  ];

  useEffect(() => {
    if (!currentVideo || !currentSubtitle) {
      showToast("No active video or subtitles session found.", "warning");
      navigate("/dashboard");
    }
  }, [currentVideo, currentSubtitle]);

  const handlePlayPause = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!videoRef.current) return;
    const val = parseFloat(e.target.value);
    videoRef.current.currentTime = val;
    setCurrentTime(val);
  };

  const selectStylePreset = (presetId: string) => {
    const found = stylePresets.find((p) => p.id === presetId);
    if (found) {
      setActiveStylePreset(presetId);
      updateActiveStyle(found.config);
      showToast(`Style preset '${found.name}' applied!`, "success");
    }
  };

  // Helper to determine word visual class styles during HTML overlay simulation
  const getSimulatedWordStyle = (word: any) => {
    const isActive = currentTime >= word.start && currentTime <= word.end;
    let color = activeStyle.text_color;
    let transform = "scale(1)";

    if (isActive) {
      color = activeStyle.highlight_color;
      if (activeAnimation === "word_pop") transform = "scale(1.2)";
      if (activeAnimation === "word_bounce")
        transform = "translateY(-10px) scale(1.05)";
      if (activeAnimation === "word_rotate") transform = "rotate(8deg)";
    }

    return {
      color,
      transform,
      fontFamily: activeStyle.font_family,
      fontSize: `${activeStyle.font_size}px`,
      textShadow:
        activeStyle.shadow_offset_x || activeStyle.shadow_offset_y
          ? `${activeStyle.shadow_offset_x}px ${activeStyle.shadow_offset_y}px 0px ${activeStyle.shadow_color}`
          : "none",
      WebkitTextStroke:
        activeStyle.outline_width > 0
          ? `${activeStyle.outline_width}px ${activeStyle.outline_color}`
          : "none",
      backgroundColor: activeStyle.background_box
        ? activeStyle.background_color
        : "transparent",
      padding: activeStyle.background_box
        ? `${activeStyle.padding}px`
        : "0px",
      borderRadius: activeStyle.background_box
        ? `${activeStyle.border_radius}px`
        : "0px",
      transition: "all 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
      display: "inline-block",
      margin: "0 6px",
    };
  };

  // Retrieve caption segment active at current video playback timestamp
  const getActiveCaptionSegment = () => {
    if (!currentAlignment || !currentAlignment.segments) return null;
    return currentAlignment.segments.find(
      (seg) => currentTime >= seg.start && currentTime <= seg.end
    );
  };

  const handleTriggerRender = async () => {
    if (!currentVideo || !currentSubtitle) return;

    setRendering(true);
    showToast("Starting rendering pipeline job...", "info");

    try {
      const renderStatus = await apiService.startRender(
        currentVideo.id,
        currentVideo.id, // subtitle id matches video/alignment id
        activeStylePreset,
        activeAnimation
      );

      setRenderId(renderStatus.render_id);
      showToast("Rendering initialized in background!", "success");
      navigate("/export");
    } catch (e: any) {
      console.error(e);
      const errMsg = e.response?.data?.detail || "Failed to start render task.";
      showToast(errMsg, "error");
    } finally {
      setRendering(false);
    }
  };

  if (!currentVideo) return null;

  const activeSegment = getActiveCaptionSegment();

  return (
    <Layout>
      <div className="grid lg:grid-cols-3 gap-8 items-start max-w-6xl mx-auto">
        {/* Left Column: Player & Overlay */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="relative aspect-video rounded-3xl overflow-hidden bg-black border border-slate-900 group shadow-2xl">
            {/* HTML5 Video Tag */}
            <video
              ref={videoRef}
              src={`http://localhost:8000/static/uploads/${currentVideo.filename}`}
              className="w-full h-full object-contain"
              onTimeUpdate={handleTimeUpdate}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onLoadedMetadata={handleLoadedMetadata}
              onClick={handlePlayPause}
            />

            {/* Custom Overlay Captions (Simulating Render Engine) */}
            {activeSegment && (
              <div
                className="absolute left-6 right-6 flex justify-center text-center pointer-events-none select-none transition-all duration-300"
                style={{
                  bottom:
                    activeStyle.vertical_position === "bottom"
                      ? `${activeStyle.safe_margin}px`
                      : "auto",
                  top:
                    activeStyle.vertical_position === "top"
                      ? `${activeStyle.safe_margin}px`
                      : activeStyle.vertical_position === "center"
                        ? "50%"
                        : "auto",
                  transform:
                    activeStyle.vertical_position === "center"
                      ? "translateY(-50%)"
                      : "none",
                }}
              >
                <div className="flex flex-wrap justify-center max-w-lg leading-relaxed">
                  {activeSegment.words.map((w, idx) => (
                    <span key={idx} style={getSimulatedWordStyle(w)}>
                      {w.word}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Play overlay controls */}
            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all duration-200 pointer-events-none">
              <button
                onClick={handlePlayPause}
                className="p-4 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white pointer-events-auto hover:scale-110 transition-transform cursor-pointer"
              >
                {isPlaying ? (
                  <PauseIcon className="w-8 h-8" />
                ) : (
                  <PlayIcon className="w-8 h-8" />
                )}
              </button>
            </div>
          </div>

          {/* Timeline slider seek bar */}
          <div className="glass-card p-4 rounded-2xl border border-slate-900 flex items-center gap-4">
            <span className="text-xs font-mono text-slate-500">
              {currentTime.toFixed(2)}s
            </span>
            <input
              type="range"
              min={0}
              max={duration || 100}
              step={0.01}
              value={currentTime}
              onChange={handleSeek}
              className="flex-1 accent-primary h-1.5 rounded-lg bg-slate-900 appearance-none cursor-pointer"
            />
            <span className="text-xs font-mono text-slate-500">
              {duration.toFixed(2)}s
            </span>
          </div>
        </div>

        {/* Right Column: Style Sidebar Editor */}
        <div className="glass-card p-6 rounded-3xl border border-slate-900 flex flex-col gap-6 h-[75vh] overflow-y-auto">
          <div>
            <h2 className="text-lg font-extrabold text-slate-100">
              Visual Style Editor
            </h2>
            <p className="text-slate-500 text-xs mt-0.5">
              Customize text outlines, background shapes, colors, and keyframe
              presets.
            </p>
          </div>

          {/* Presets List */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
              Style Preset
            </label>
            <div className="grid grid-cols-2 gap-2">
              {stylePresets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => selectStylePreset(preset.id)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                    activeStylePreset === preset.id
                      ? "bg-primary/10 text-primary border-primary"
                      : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-300"
                  }`}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Animation selection */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
              Animation Effect
            </label>
            <select
              value={activeAnimation}
              onChange={(e) => setActiveAnimation(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-300 focus:outline-none focus:border-primary cursor-pointer"
            >
              {animationPresets.map((anim) => (
                <option key={anim.id} value={anim.id}>
                  {anim.name}
                </option>
              ))}
            </select>
          </div>

          {/* Colors Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Text Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={activeStyle.text_color}
                  onChange={(e) =>
                    updateActiveStyle({ text_color: e.target.value })
                  }
                  className="w-8 h-8 rounded-lg border border-slate-800 bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-400">
                  {activeStyle.text_color.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Highlight Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={activeStyle.highlight_color}
                  onChange={(e) =>
                    updateActiveStyle({ highlight_color: e.target.value })
                  }
                  className="w-8 h-8 rounded-lg border border-slate-800 bg-transparent cursor-pointer"
                />
                <span className="text-xs font-mono text-slate-400">
                  {activeStyle.highlight_color.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Fonts selection */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Font Family
              </label>
              <select
                value={activeStyle.font_family}
                onChange={(e) =>
                  updateActiveStyle({ font_family: e.target.value })
                }
                className="bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-xs font-semibold text-slate-300 focus:outline-none cursor-pointer"
              >
                {fontPresets.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Font Size
              </label>
              <input
                type="number"
                min={10}
                max={100}
                value={activeStyle.font_size}
                onChange={(e) =>
                  updateActiveStyle({ font_size: parseInt(e.target.value) })
                }
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none"
              />
            </div>
          </div>

          {/* Background Toggle Box */}
          <div className="flex items-center justify-between p-3.5 bg-slate-900/40 rounded-xl border border-slate-900 select-none">
            <span className="text-xs font-bold text-slate-300">
              Text Background Box
            </span>
            <input
              type="checkbox"
              checked={activeStyle.background_box}
              onChange={(e) =>
                updateActiveStyle({ background_box: e.target.checked })
              }
              className="w-4 h-4 accent-primary cursor-pointer"
            />
          </div>

          {/* Action Trigger Render */}
          <button
            onClick={handleTriggerRender}
            disabled={rendering}
            className="w-full py-4 rounded-xl font-bold bg-gradient-to-r from-primary to-accent hover:from-blue-600 hover:to-violet-600 text-white shadow-lg shadow-primary/10 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <SparklesIcon className="w-5 h-5" />
            <span>{rendering ? "Triggering..." : "Render Video"}</span>
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default Preview;
