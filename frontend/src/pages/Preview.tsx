import React, { useRef, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useApp, defaultStyle, type StyleConfig } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService, type AlignmentSegment, type WordAlignment } from "../services/api";
import Layout from "../components/Layout";
import {
  PlayIcon,
  PauseIcon,
  BackwardIcon,
  ForwardIcon,
  SparklesIcon,
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ScissorsIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/solid";

interface HistoryState {
  captions: AlignmentSegment[];
  style: StyleConfig;
  animation: string;
}

const Preview: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentVideo,
    projectId,
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
  const timelineRef = useRef<HTMLDivElement>(null);

  // Core Editor States
  const [captions, setCaptions] = useState<AlignmentSegment[]>([]);
  const [selectedSegmentIdx, setSelectedSegmentIdx] = useState<number | null>(
    null
  );
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(1); // Timeline zoom scale (1 = fit, 2-10 = zoomed in)
  const [snapToGrid, setSnapToGrid] = useState(true);

  // Undo/Redo queues
  const [undoStack, setUndoStack] = useState<HistoryState[]>([]);
  const [redoStack, setRedoStack] = useState<HistoryState[]>([]);

  // Auto save trackers
  const [saveStatus, setSaveStatus] = useState<
    "saved" | "saving" | "unsaved" | "error"
  >("saved");
  const lastSavedStateRef = useRef<string>("");
  const autoSaveTimerRef = useRef<any>(null);

  // Panel Tabs
  const [activeTab, setActiveTab] = useState<"text" | "style" | "animation">(
    "text"
  );

  // Load project from database/context
  useEffect(() => {
    const loadProjectData = async () => {
      if (!projectId) {
        showToast("No active project session initialized.", "warning");
        navigate("/dashboard");
        return;
      }
      try {
        setSaveStatus("saving");
        const project = await apiService.loadProject(projectId);
        setCaptions(project.captions_data);
        updateActiveStyle(project.style_data);
        setActiveAnimation(project.animation_preset);
        lastSavedStateRef.current = JSON.stringify({
          captions: project.captions_data,
          style: project.style_data,
          animation: project.animation_preset,
        });
        setSaveStatus("saved");
      } catch (e: any) {
        console.error(e);
        showToast("Failed to load timeline project data.", "error");
        setSaveStatus("error");
      }
    };

    loadProjectData();
  }, [projectId]);

  // Video playback callbacks
  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration);
    setVolume(videoRef.current.volume);
  };

  const handlePlayPause = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  };

  const handleSeek = (time: number) => {
    if (!videoRef.current) return;
    const clamped = Math.max(0, Math.min(duration, time));
    videoRef.current.currentTime = clamped;
    setCurrentTime(clamped);
  };

  const handleFrameStep = (direction: "forward" | "backward") => {
    const step = 0.04; // ~1 frame at 25fps
    handleSeek(currentTime + (direction === "forward" ? step : -step));
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (videoRef.current) {
      videoRef.current.volume = val;
    }
  };

  const handleSpeedChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = parseFloat(e.target.value);
    setPlaybackSpeed(val);
    if (videoRef.current) {
      videoRef.current.playbackRate = val;
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      }
    }
  };

  // Push state to Undo stack before modification
  const pushToHistory = (
    nextCaptions = captions,
    nextStyle = activeStyle,
    nextAnimation = activeAnimation
  ) => {
    const state: HistoryState = {
      captions: JSON.parse(JSON.stringify(nextCaptions)),
      style: { ...nextStyle },
      animation: nextAnimation,
    };
    setUndoStack((prev) => [...prev, state].slice(-50)); // limit history to 50 edits
    setRedoStack([]); // clear redo stack on new action
    setSaveStatus("unsaved");
  };

  // Undo/Redo logic
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return;
    const previous = undoStack[undoStack.length - 1];
    const current: HistoryState = {
      captions: JSON.parse(JSON.stringify(captions)),
      style: { ...activeStyle },
      animation: activeAnimation,
    };

    setRedoStack((prev) => [...prev, current]);
    setUndoStack((prev) => prev.slice(0, -1));

    setCaptions(previous.captions);
    updateActiveStyle(previous.style);
    setActiveAnimation(previous.animation);
    setSaveStatus("unsaved");
    showToast("Undo applied", "info");
  }, [undoStack, captions, activeStyle, activeAnimation]);

  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return;
    const next = redoStack[redoStack.length - 1];
    const current: HistoryState = {
      captions: JSON.parse(JSON.stringify(captions)),
      style: { ...activeStyle },
      animation: activeAnimation,
    };

    setUndoStack((prev) => [...prev, current]);
    setRedoStack((prev) => prev.slice(0, -1));

    setCaptions(next.captions);
    updateActiveStyle(next.style);
    setActiveAnimation(next.animation);
    setSaveStatus("unsaved");
    showToast("Redo applied", "info");
  }, [redoStack, captions, activeStyle, activeAnimation]);

  // Keyboard Shortcuts listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement;
      const isInput =
        activeEl?.tagName === "INPUT" || activeEl?.tagName === "TEXTAREA";
      if (isInput) return; // skip shortcut triggers inside textboxes

      if (e.code === "Space") {
        e.preventDefault();
        handlePlayPause();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        handleFrameStep("backward");
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        handleFrameStep("forward");
      } else if (e.code === "KeyZ" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handleUndo();
      } else if (e.code === "KeyY" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handleRedo();
      } else if (e.code === "Delete" && selectedSegmentIdx !== null) {
        e.preventDefault();
        handleDeleteCaption(selectedSegmentIdx);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPlaying, currentTime, undoStack, redoStack, selectedSegmentIdx, captions]);

  // Caption Editing Operations
  const handleUpdateText = (index: number, text: string) => {
    pushToHistory();
    const updated = [...captions];
    updated[index].text = text;

    // Distribute words alignment names in case user adds/modifies words
    const wordsArr = text.trim().split(/\s+/);
    const duration = updated[index].end - updated[index].start;
    const wordDur = duration / Math.max(1, wordsArr.length);

    updated[index].words = wordsArr.map((w, idx) => ({
      word: w,
      start: updated[index].start + idx * wordDur,
      end: updated[index].start + (idx + 1) * wordDur,
      score: 1.0,
    }));

    setCaptions(updated);
  };

  const handleUpdateTiming = (
    index: number,
    field: "start" | "end",
    val: number
  ) => {
    pushToHistory();
    const updated = [...captions];
    updated[index][field] = Math.max(0, val);

    // Ensure start is before end
    if (updated[index].start > updated[index].end) {
      if (field === "start") updated[index].end = updated[index].start + 0.5;
      else updated[index].start = Math.max(0, updated[index].end - 0.5);
    }
    setCaptions(updated);
  };

  const handleDeleteCaption = (index: number) => {
    pushToHistory();
    setCaptions((prev) => prev.filter((_, idx) => idx !== index));
    setSelectedSegmentIdx(null);
    showToast("Caption segment deleted", "success");
  };

  const handleSplitCaption = (index: number) => {
    pushToHistory();
    const seg = captions[index];
    const midTime = currentTime;

    if (midTime <= seg.start || midTime >= seg.end) {
      showToast(
        "Move playhead inside the segment duration to split.",
        "warning"
      );
      return;
    }

    const firstWords = seg.words.filter((w) => w.end <= midTime);
    const secondWords = seg.words.filter((w) => w.end > midTime);

    const firstText = firstWords.map((w) => w.word).join(" ");
    const secondText = secondWords.map((w) => w.word).join(" ");

    const firstSeg: AlignmentSegment = {
      text: firstText || "First Half",
      start: seg.start,
      end: midTime,
      words: firstWords.length > 0 ? firstWords : [{ word: "First", start: seg.start, end: midTime, score: 1.0 }],
    };

    const secondSeg: AlignmentSegment = {
      text: secondText || "Second Half",
      start: midTime,
      end: seg.end,
      words: secondWords.length > 0 ? secondWords : [{ word: "Second", start: midTime, end: seg.end, score: 1.0 }],
    };

    const updated = [...captions];
    updated.splice(index, 1, firstSeg, secondSeg);
    setCaptions(updated);
    setSelectedSegmentIdx(index);
    showToast("Segment split complete", "success");
  };

  const handleMergeCaption = (index: number) => {
    if (index >= captions.length - 1) {
      showToast("No next segment available to merge.", "warning");
      return;
    }
    pushToHistory();
    const current = captions[index];
    const next = captions[index + 1];

    const mergedSeg: AlignmentSegment = {
      text: `${current.text} ${next.text}`,
      start: current.start,
      end: next.end,
      words: [...current.words, ...next.words],
    };

    const updated = [...captions];
    updated.splice(index, 2, mergedSeg);
    setCaptions(updated);
    setSelectedSegmentIdx(index);
    showToast("Merged with next segment", "success");
  };

  const handleInsertCaption = () => {
    pushToHistory();
    const newSeg: AlignmentSegment = {
      text: "New Subtitle Block",
      start: currentTime,
      end: Math.min(duration, currentTime + 2.0),
      words: [
        {
          word: "New",
          start: currentTime,
          end: Math.min(duration, currentTime + 1.0),
          score: 1.0,
        },
        {
          word: "Block",
          start: Math.min(duration, currentTime + 1.0),
          end: Math.min(duration, currentTime + 2.0),
          score: 1.0,
        },
      ],
    };

    const insertIdx = captions.findIndex((c) => c.start > currentTime);
    const updated = [...captions];
    if (insertIdx === -1) updated.push(newSeg);
    else updated.splice(insertIdx, 0, newSeg);

    setCaptions(updated);
    setSelectedSegmentIdx(insertIdx === -1 ? updated.length - 1 : insertIdx);
    showToast("New caption segment inserted", "success");
  };

  // Auto-Save Trigger Syncs
  const handleSaveProject = async (manual = false) => {
    if (!projectId) return;
    setSaveStatus("saving");
    try {
      const updatePayload = {
        captions_data: captions,
        style_data: activeStyle,
        animation_preset: activeAnimation,
      };

      await apiService.saveProject(projectId, updatePayload);
      lastSavedStateRef.current = JSON.stringify(updatePayload);
      setSaveStatus("saved");
      if (manual) {
        showToast("Project saved successfully!", "success");
      }
    } catch (e) {
      console.error(e);
      setSaveStatus("error");
      showToast("Auto-save sync failed.", "error");
    }
  };

  // Periodic Auto-Save hook
  useEffect(() => {
    if (autoSaveTimerRef.current) clearInterval(autoSaveTimerRef.current);

    autoSaveTimerRef.current = setInterval(() => {
      const currentStateStr = JSON.stringify({
        captions,
        style: activeStyle,
        animation: activeAnimation,
      });

      if (
        currentStateStr !== lastSavedStateRef.current &&
        projectId &&
        captions.length > 0
      ) {
        handleSaveProject(false);
      }
    }, 5000); // Save every 5 seconds if changed

    return () => {
      if (autoSaveTimerRef.current) clearInterval(autoSaveTimerRef.current);
    };
  }, [captions, activeStyle, activeAnimation, projectId]);

  // Style Presets selector
  const selectStylePreset = (presetId: string) => {
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

    const found = stylePresets.find((p) => p.id === presetId);
    if (found) {
      pushToHistory(captions, found.config);
      setActiveStylePreset(presetId);
      updateActiveStyle(found.config);
      showToast(`Preset '${found.name}' applied!`, "success");
    }
  };

  // Video Overlays simulated highlight styles builder
  const getSimulatedWordStyle = (word: WordAlignment) => {
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
      padding: activeStyle.background_box ? `${activeStyle.padding}px` : "0px",
      borderRadius: activeStyle.background_box
        ? `${activeStyle.border_radius}px`
        : "0px",
      transition: "all 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
      display: "inline-block",
      margin: "0 6px",
    };
  };

  const getActiveCaptionSegment = () => {
    return captions.find(
      (seg) => currentTime >= seg.start && currentTime <= seg.end
    );
  };

  const handleTriggerRender = async () => {
    if (!currentVideo || !projectId) return;

    // Make sure latest edits are saved first
    await handleSaveProject(false);

    setRenderId(null);
    showToast("Initializing video rendering task...", "info");

    try {
      const renderStatus = await apiService.startRender(
        currentVideo.id,
        currentVideo.id, // subtitle id matches video id
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
    }
  };

  // Timeline resize drag handlers
  const handleTimelineResize = (
    e: React.MouseEvent,
    idx: number,
    boundary: "start" | "end"
  ) => {
    e.stopPropagation();
    e.preventDefault();

    const startX = e.clientX;
    const initialTime = captions[idx][boundary];
    const timelineWidth = timelineRef.current?.getBoundingClientRect().width || 1;

    const handleMouseMove = (moveEv: MouseEvent) => {
      const deltaX = moveEv.clientX - startX;
      // Convert pixel delta to seconds offset
      const durationFactor = duration * zoomLevel;
      const timeDelta = (deltaX / timelineWidth) * durationFactor;
      let newTime = initialTime + timeDelta;

      if (snapToGrid) {
        // Snap to nearest 0.1s grid increments
        newTime = Math.round(newTime * 10) / 10;
      }

      newTime = Math.max(0, Math.min(duration, newTime));

      setCaptions((prev) => {
        const updated = [...prev];
        updated[idx][boundary] = newTime;
        return updated;
      });
    };

    const handleMouseUp = () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      pushToHistory(); // Record state history for undo queue
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  if (!currentVideo) return null;

  const activeSegment = getActiveCaptionSegment();

  return (
    <Layout>
      <div className="flex flex-col gap-6 max-w-7xl mx-auto h-[82vh]">
        {/* Subtitle Workspace Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-[#070b19] border border-slate-900 px-6 py-3.5 rounded-2xl shadow-lg shadow-black/10 select-none">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-black text-slate-100 truncate max-w-xs">
              {currentVideo.filename}
            </h1>
            {/* Status indicators */}
            {saveStatus === "saved" && (
              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Saved
              </span>
            )}
            {saveStatus === "saving" && (
              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse">
                Saving...
              </span>
            )}
            {saveStatus === "unsaved" && (
              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Unsaved Changes
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Undo/Redo Buttons */}
            <button
              onClick={handleUndo}
              disabled={undoStack.length === 0}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-30 transition-all cursor-pointer"
              title="Undo (Ctrl+Z)"
            >
              <ArrowUturnLeftIcon className="w-4 h-4" />
            </button>
            <button
              onClick={handleRedo}
              disabled={redoStack.length === 0}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-30 transition-all cursor-pointer"
              title="Redo (Ctrl+Y)"
            >
              <ArrowUturnRightIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleSaveProject(true)}
              className="px-4 py-2 text-xs font-extrabold rounded-lg bg-slate-900 border border-slate-850 hover:bg-slate-800 hover:text-slate-100 transition-all cursor-pointer"
            >
              Save Project
            </button>
            <button
              onClick={handleTriggerRender}
              className="px-4 py-2 text-xs font-extrabold rounded-lg bg-primary hover:bg-blue-600 shadow-md shadow-primary/20 flex items-center gap-1.5 cursor-pointer"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>Export Render</span>
            </button>
          </div>
        </div>

        {/* Workspace Panels (Player vs. Editor Sidebar) */}
        <div className="flex-1 grid lg:grid-cols-3 gap-6 min-h-0">
          {/* Main Player Panel */}
          <div className="lg:col-span-2 flex flex-col gap-4 min-h-0">
            <div className="relative flex-1 rounded-3xl overflow-hidden bg-black border border-slate-900 group shadow-2xl flex items-center justify-center">
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

              {/* Real-time overlaid simulated captions */}
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
                  <div className="flex flex-wrap justify-center max-w-lg leading-relaxed bg-black/20 backdrop-blur-[1px] px-4 py-2 rounded-xl">
                    {activeSegment.words.map((w, idx) => (
                      <span key={idx} style={getSimulatedWordStyle(w)}>
                        {w.word}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Custom Video Controls Panel */}
            <div className="glass-card px-5 py-3 rounded-2xl border border-slate-950 flex flex-wrap items-center justify-between gap-4 select-none">
              <div className="flex items-center gap-3">
                {/* Frame Step Backward */}
                <button
                  onClick={() => handleFrameStep("backward")}
                  className="p-1.5 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
                  title="Frame Back (Left Arrow)"
                >
                  <BackwardIcon className="w-5 h-5" />
                </button>
                {/* Play/Pause */}
                <button
                  onClick={handlePlayPause}
                  className="p-2.5 rounded-full bg-primary text-white hover:scale-105 hover:bg-blue-600 transition-all cursor-pointer"
                  title="Play/Pause (Space)"
                >
                  {isPlaying ? (
                    <PauseIcon className="w-5 h-5" />
                  ) : (
                    <PlayIcon className="w-5 h-5" />
                  )}
                </button>
                {/* Frame Step Forward */}
                <button
                  onClick={() => handleFrameStep("forward")}
                  className="p-1.5 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
                  title="Frame Fwd (Right Arrow)"
                >
                  <ForwardIcon className="w-5 h-5" />
                </button>

                {/* Time Indicators */}
                <span className="text-xs font-mono text-slate-500 font-bold ml-2">
                  {currentTime.toFixed(2)}s / {duration.toFixed(2)}s
                </span>
              </div>

              <div className="flex items-center gap-4">
                {/* Playback speed */}
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    Speed
                  </span>
                  <select
                    value={playbackSpeed}
                    onChange={handleSpeedChange}
                    className="bg-slate-900 text-xs font-bold text-slate-300 border border-slate-800 rounded-lg px-2 py-1 focus:outline-none cursor-pointer"
                  >
                    <option value="0.5">0.5x</option>
                    <option value="1">1.0x</option>
                    <option value="1.5">1.5x</option>
                    <option value="2">2.0x</option>
                  </select>
                </div>

                {/* Volume slider */}
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    Vol
                  </span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={volume}
                    onChange={handleVolumeChange}
                    className="w-16 accent-primary h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Fullscreen */}
                <button
                  onClick={handleFullscreen}
                  className="text-xs font-bold text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  Fullscreen
                </button>
              </div>
            </div>
          </div>

          {/* Right Editing Workspace Sidebar */}
          <div className="glass-card border border-slate-900 rounded-3xl overflow-hidden flex flex-col min-h-0 h-full shadow-2xl">
            {/* Tabs Header */}
            <div className="flex border-b border-slate-950 bg-slate-900/30 select-none">
              {(["text", "style", "animation"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-all border-b-2 cursor-pointer ${
                    activeTab === tab
                      ? "text-primary border-primary bg-primary/5"
                      : "text-slate-500 border-transparent hover:text-slate-300"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Scrollable Tab Panels */}
            <div className="flex-1 overflow-y-auto p-5 min-h-0">
              {/* Tab 1: Caption Text Blocks list */}
              {activeTab === "text" && (
                <div className="flex flex-col gap-4">
                  <div className="flex justify-between items-center select-none">
                    <span className="text-[10px] font-black uppercase text-slate-500 tracking-wider">
                      Captions list ({captions.length})
                    </span>
                    <button
                      onClick={handleInsertCaption}
                      className="px-2.5 py-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20 text-xs font-extrabold hover:bg-primary/20 transition-all flex items-center gap-1 cursor-pointer"
                    >
                      <PlusIcon className="w-3.5 h-3.5" />
                      <span>Insert Segment</span>
                    </button>
                  </div>

                  <div className="flex flex-col gap-3">
                    {captions.map((seg, idx) => {
                      const isHighlighted = selectedSegmentIdx === idx;
                      const isTimeActive =
                        currentTime >= seg.start && currentTime <= seg.end;

                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedSegmentIdx(idx)}
                          className={`p-3 rounded-xl border transition-all cursor-pointer ${
                            isHighlighted
                              ? "bg-primary/5 border-primary shadow-lg shadow-primary/5"
                              : isTimeActive
                                ? "bg-slate-900/50 border-slate-800 border-l-4 border-l-primary"
                                : "bg-slate-950/20 border-slate-900 hover:border-slate-800"
                          }`}
                        >
                          <div className="flex justify-between gap-2 mb-2 select-none">
                            <span className="text-[10px] font-mono text-slate-500">
                              #{idx + 1} • {seg.start.toFixed(2)}s -{" "}
                              {seg.end.toFixed(2)}s
                            </span>
                            <div className="flex items-center gap-1.5">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSplitCaption(idx);
                                }}
                                className="p-1 rounded hover:bg-slate-900 text-slate-500 hover:text-slate-350 cursor-pointer"
                                title="Split Segment at Playhead"
                              >
                                <ScissorsIcon className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleMergeCaption(idx);
                                }}
                                className="p-1 rounded hover:bg-slate-900 text-slate-500 hover:text-slate-350 cursor-pointer"
                                title="Merge with Next Segment"
                              >
                                <PlusIcon className="w-3.5 h-3.5 rotate-45" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteCaption(idx);
                                }}
                                className="p-1 rounded hover:bg-red-500/10 text-slate-500 hover:text-red-500 cursor-pointer"
                                title="Delete Segment"
                              >
                                <TrashIcon className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <textarea
                            value={seg.text}
                            onChange={(e) =>
                              handleUpdateText(idx, e.target.value)
                            }
                            onClick={(e) => e.stopPropagation()}
                            className="w-full bg-slate-900/60 border border-slate-850 rounded-lg p-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-primary resize-none h-12"
                            placeholder="Subtitle text content..."
                          />

                          {/* Fine-tune Timings Inputs */}
                          <div className="grid grid-cols-2 gap-2 mt-2 select-none">
                            <div className="flex items-center gap-1.5">
                              <span className="text-[9px] font-bold text-slate-650">
                                Start:
                              </span>
                              <input
                                type="number"
                                step="0.05"
                                value={parseFloat(seg.start.toFixed(2))}
                                onChange={(e) =>
                                  handleUpdateTiming(
                                    idx,
                                    "start",
                                    parseFloat(e.target.value)
                                  )
                                }
                                onClick={(e) => e.stopPropagation()}
                                className="w-full bg-slate-900/50 border border-slate-900 rounded px-1.5 py-0.5 text-[10px] font-mono text-slate-450 focus:outline-none"
                              />
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-[9px] font-bold text-slate-650">
                                End:
                              </span>
                              <input
                                type="number"
                                step="0.05"
                                value={parseFloat(seg.end.toFixed(2))}
                                onChange={(e) =>
                                  handleUpdateTiming(
                                    idx,
                                    "end",
                                    parseFloat(e.target.value)
                                  )
                                }
                                onClick={(e) => e.stopPropagation()}
                                className="w-full bg-slate-900/50 border border-slate-900 rounded px-1.5 py-0.5 text-[10px] font-mono text-slate-450 focus:outline-none"
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tab 2: Visual Style Configurations */}
              {activeTab === "style" && (
                <div className="flex flex-col gap-5 select-none">
                  {/* Style Presets List */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                      Preset Styles
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {["default", "tiktok", "mrbeast", "hormozi"].map(
                        (presetId) => (
                          <button
                            key={presetId}
                            onClick={() => selectStylePreset(presetId)}
                            className={`px-3 py-2 rounded-xl text-xs font-extrabold border transition-all cursor-pointer capitalize ${
                              activeStylePreset === presetId
                                ? "bg-primary/10 text-primary border-primary"
                                : "bg-slate-950/40 text-slate-400 border-slate-900 hover:text-slate-200"
                            }`}
                          >
                            {presetId}
                          </button>
                        )
                      )}
                    </div>
                  </div>

                  {/* Colors */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-455 uppercase tracking-wide">
                        Text Color
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={activeStyle.text_color}
                          onChange={(e) => {
                            pushToHistory();
                            updateActiveStyle({ text_color: e.target.value });
                          }}
                          className="w-8 h-8 rounded-lg border border-slate-800 bg-transparent cursor-pointer"
                        />
                        <span className="text-xs font-mono text-slate-400 uppercase">
                          {activeStyle.text_color}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-455 uppercase tracking-wide">
                        Highlight
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={activeStyle.highlight_color}
                          onChange={(e) => {
                            pushToHistory();
                            updateActiveStyle({
                              highlight_color: e.target.value,
                            });
                          }}
                          className="w-8 h-8 rounded-lg border border-slate-800 bg-transparent cursor-pointer"
                        />
                        <span className="text-xs font-mono text-slate-400 uppercase">
                          {activeStyle.highlight_color}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Fonts */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-455 uppercase tracking-wide">
                        Font Family
                      </label>
                      <select
                        value={activeStyle.font_family}
                        onChange={(e) => {
                          pushToHistory();
                          updateActiveStyle({ font_family: e.target.value });
                        }}
                        className="bg-slate-900 border border-slate-800 rounded-xl px-2 py-2 text-xs font-semibold text-slate-300 focus:outline-none cursor-pointer"
                      >
                        {["Arial", "Impact", "Montserrat", "Roboto"].map(
                          (f) => (
                            <option key={f} value={f}>
                              {f}
                            </option>
                          )
                        )}
                      </select>
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-455 uppercase tracking-wide">
                        Size (px)
                      </label>
                      <input
                        type="number"
                        min={10}
                        max={100}
                        value={activeStyle.font_size}
                        onChange={(e) => {
                          pushToHistory();
                          updateActiveStyle({
                            font_size: parseInt(e.target.value) || 24,
                          });
                        }}
                        className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-300 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Position */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-bold text-slate-455 uppercase tracking-wide">
                      Vertical Alignment
                    </label>
                    <select
                      value={activeStyle.vertical_position}
                      onChange={(e) => {
                        pushToHistory();
                        updateActiveStyle({
                          vertical_position: e.target.value as any,
                        });
                      }}
                      className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none cursor-pointer"
                    >
                      <option value="top">Top</option>
                      <option value="center">Center</option>
                      <option value="bottom">Bottom</option>
                    </select>
                  </div>

                  {/* Background Box Switch */}
                  <div className="flex items-center justify-between p-3 bg-slate-900/40 rounded-xl border border-slate-900">
                    <span className="text-xs font-bold text-slate-300">
                      Background Overlay Box
                    </span>
                    <input
                      type="checkbox"
                      checked={activeStyle.background_box}
                      onChange={(e) => {
                        pushToHistory();
                        updateActiveStyle({
                          background_box: e.target.checked,
                        });
                      }}
                      className="w-4 h-4 accent-primary cursor-pointer"
                    />
                  </div>
                </div>
              )}

              {/* Tab 3: Animations Presets */}
              {activeTab === "animation" && (
                <div className="flex flex-col gap-2 select-none">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">
                    Highlight Animation Presets
                  </label>
                  <div className="flex flex-col gap-2">
                    {[
                      { id: "word_highlight", name: "Word Highlight" },
                      { id: "word_pop", name: "Word Zoom Pop" },
                      { id: "word_bounce", name: "Vertical Bounce" },
                      { id: "word_fade", name: "Fade In Opacity" },
                      { id: "word_rotate", name: "Rotate Spin" },
                    ].map((anim) => (
                      <button
                        key={anim.id}
                        onClick={() => {
                          pushToHistory(captions, activeStyle, anim.id);
                          setActiveAnimation(anim.id);
                        }}
                        className={`px-4 py-3 rounded-xl text-xs font-extrabold text-left border transition-all cursor-pointer ${
                          activeAnimation === anim.id
                            ? "bg-primary/10 text-primary border-primary"
                            : "bg-slate-950/40 text-slate-400 border-slate-900 hover:text-slate-200"
                        }`}
                      >
                        {anim.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Visual Timeline Panel (Zoomable, Scrollable, Playhead Synced) */}
        <div className="glass-card p-4 rounded-3xl border border-slate-900 flex flex-col gap-3 min-h-0 bg-[#030712]/90 shadow-2xl">
          {/* Timeline Toolbar controls */}
          <div className="flex justify-between items-center text-xs font-bold text-slate-500 border-b border-slate-900 pb-2 select-none">
            <div className="flex items-center gap-3">
              <span>Zoom Scale</span>
              <input
                type="range"
                min="1"
                max="10"
                step="0.5"
                value={zoomLevel}
                onChange={(e) => setZoomLevel(parseFloat(e.target.value))}
                className="w-32 h-1 accent-primary bg-slate-900 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-[10px] text-slate-400">
                {zoomLevel.toFixed(1)}x
              </span>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={snapToGrid}
                  onChange={(e) => setSnapToGrid(e.target.checked)}
                  className="w-3.5 h-3.5 accent-primary"
                />
                <span>Snap to 0.1s Grid</span>
              </label>
            </div>
          </div>

          {/* Zoomed Timeline Track Container */}
          <div className="relative flex-1 overflow-x-auto min-h-[90px] border border-slate-950 rounded-xl bg-slate-950/20 select-none">
            <div
              ref={timelineRef}
              className="relative h-full min-w-full"
              style={{ width: `${100 * zoomLevel}%` }}
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickedTime = (clickX / rect.width) * duration;
                handleSeek(clickedTime);
              }}
            >
              {/* Vertical Playhead sync line */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
                style={{
                  left: `${(currentTime / (duration || 1)) * 100}%`,
                }}
              >
                {/* Red playhead handle bulb */}
                <div className="absolute top-0 -left-1.5 w-3.5 h-3.5 rounded-full bg-red-500 shadow-md"></div>
              </div>

              {/* Video track background bar */}
              <div className="absolute left-0 right-0 top-3 h-6 bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border-y border-slate-900/50 flex items-center px-4">
                <span className="text-[9px] font-extrabold text-slate-650 tracking-wider">
                  VIDEO TRACK
                </span>
              </div>

              {/* Captions blocks visual sequence */}
              <div className="absolute left-0 right-0 top-11 bottom-3 relative">
                {captions.map((seg, idx) => {
                  const left = (seg.start / (duration || 1)) * 100;
                  const width = ((seg.end - seg.start) / (duration || 1)) * 100;
                  const isHighlighted = selectedSegmentIdx === idx;

                  return (
                    <div
                      key={idx}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedSegmentIdx(idx);
                        handleSeek(seg.start);
                      }}
                      className={`absolute h-7 rounded-md border flex items-center justify-between px-2 text-[9px] font-extrabold transition-all group overflow-hidden ${
                        isHighlighted
                          ? "bg-primary/20 border-primary text-primary shadow-md shadow-primary/10"
                          : "bg-slate-900/70 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                      }}
                    >
                      {/* Left Boundary resize drag handle */}
                      <div
                        onMouseDown={(e) =>
                          handleTimelineResize(e, idx, "start")
                        }
                        className="absolute left-0 top-0 bottom-0 w-1 bg-yellow-500 opacity-0 group-hover:opacity-100 cursor-ew-resize transition-opacity"
                      />

                      <span className="truncate flex-1 select-none pr-1 pl-1">
                        {seg.text}
                      </span>

                      {/* Right Boundary resize drag handle */}
                      <div
                        onMouseDown={(e) => handleTimelineResize(e, idx, "end")}
                        className="absolute right-0 top-0 bottom-0 w-1 bg-yellow-500 opacity-0 group-hover:opacity-100 cursor-ew-resize transition-opacity"
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Preview;
