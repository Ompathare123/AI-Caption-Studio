import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService } from "../services/api";
import Layout from "../components/Layout";
import { CheckCircleIcon } from "@heroicons/react/24/solid";
import { CommandLineIcon } from "@heroicons/react/24/outline";

interface Step {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
}

const Processing: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentVideo,
    setCurrentAudio,
    setCurrentTranscription,
    setCurrentAlignment,
    setCurrentSubtitle,
  } = useApp();
  const { showToast } = useToast();

  const [steps, setSteps] = useState<Step[]>([
    { id: "upload", name: "Upload Video", status: "completed" },
    { id: "extract", name: "Extract Audio", status: "pending" },
    { id: "transcribe", name: "Transcribe Audio", status: "pending" },
    { id: "align", name: "Alignment (Word-Level)", status: "pending" },
    { id: "subtitle", name: "Subtitle Generation", status: "pending" },
  ]);

  const [logs, setLogs] = useState<string[]>([]);
  const [estimatedSeconds, setEstimatedSeconds] = useState(30);
  const logEndRef = useRef<HTMLDivElement>(null);
  const processingRef = useRef(false);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`]);
  };

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  // Estimated countdown timer
  useEffect(() => {
    const activeRunning = steps.some((s) => s.status === "running");
    if (!activeRunning || estimatedSeconds <= 0) return;

    const timer = setInterval(() => {
      setEstimatedSeconds((prev) => Math.max(1, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [steps, estimatedSeconds]);

  useEffect(() => {
    if (!currentVideo) {
      showToast("No active video session found. Redirecting...", "warning");
      navigate("/upload");
      return;
    }

    if (processingRef.current) return;
    processingRef.current = true;

    // Run pipeline sequence
    const executePipeline = async () => {
      // Initialize estimated seconds based on video duration
      const duration = currentVideo.duration || 10;
      setEstimatedSeconds(Math.ceil(duration * 1.5 + 5));

      addLog(`Pipeline initialized for video file: ${currentVideo.filename}`);
      addLog(`Video duration: ${duration.toFixed(2)}s`);

      let audioId = "";
      let transcriptId = "";
      let alignmentId = "";

      // Step 1: Extract Audio
      try {
        updateStepStatus("extract", "running");
        addLog("Extracting audio PCM mono channels using FFmpeg...");
        const audioData = await apiService.extractAudio(currentVideo.id);
        audioId = audioData.id;
        setCurrentAudio(audioData);
        addLog(`Audio isolation completed successfully. Audio ID: ${audioId}`);
        updateStepStatus("extract", "completed");
      } catch (e: any) {
        handleStepFailure(
          "extract",
          "Audio extraction failed",
          e.response?.data?.detail
        );
        return;
      }

      // Step 2: Transcribe
      try {
        updateStepStatus("transcribe", "running");
        addLog("Initializing speech recognition transcription models...");
        addLog("Processing speech with Faster-Whisper ASR models...");
        const transcriptData = await apiService.transcribeAudio(audioId);
        transcriptId = transcriptData.id;
        setCurrentTranscription(transcriptData);
        addLog(`ASR Speech-to-Text completed. Transcribed: "${transcriptData.text.substring(0, 50)}..."`);
        updateStepStatus("transcribe", "completed");
      } catch (e: any) {
        handleStepFailure(
          "transcribe",
          "ASR Transcription failed",
          e.response?.data?.detail
        );
        return;
      }

      // Step 3: Align
      try {
        updateStepStatus("align", "running");
        addLog("Downloading/Initializing WhisperX phoneme alignment models...");
        addLog("Generating word boundary timestamps alignment grids...");
        const alignmentData = await apiService.alignTranscript(
          audioId,
          transcriptId
        );
        alignmentId = alignmentData.id;
        setCurrentAlignment(alignmentData);
        addLog(`Word alignments successfully generated. Alignment ID: ${alignmentId}`);
        updateStepStatus("align", "completed");
      } catch (e: any) {
        handleStepFailure(
          "align",
          "Phoneme Alignment failed",
          e.response?.data?.detail
        );
        return;
      }

      // Step 4: Subtitle Generate
      try {
        updateStepStatus("subtitle", "running");
        addLog("Compiling alignment chunks into segments lists...");
        addLog("Splitting lines and exporting SRT, ASS, JSON file formats...");
        const subData = await apiService.generateSubtitles(alignmentId, "json");
        setCurrentSubtitle(subData);
        addLog("Subtitles generated successfully in output folders.");
        updateStepStatus("subtitle", "completed");
      } catch (e: any) {
        handleStepFailure(
          "subtitle",
          "Subtitle generation failed",
          e.response?.data?.detail
        );
        return;
      }

      showToast("Speech alignment pipeline completed!", "success");
      addLog("Redirecting to caption previews page in 2 seconds...");
      setTimeout(() => {
        navigate("/preview");
      }, 2000);
    };

    executePipeline();
  }, [currentVideo]);

  const updateStepStatus = (id: string, status: Step["status"]) => {
    setSteps((prev) =>
      prev.map((step) => (step.id === id ? { ...step, status } : step))
    );
  };

  const handleStepFailure = (id: string, logMsg: string, detail: string) => {
    updateStepStatus(id, "failed");
    addLog(`ERROR: ${logMsg}. Detail: ${detail || "Unknown internal error"}`);
    showToast(`${logMsg}. Please check console logs.`, "error");
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">
            Processing Speech Pipelines
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Running word alignment, speech to text, and timestamps compilation.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          {/* Stepper Status Left */}
          <div className="md:col-span-1 glass-card p-6 rounded-2xl border border-slate-900 flex flex-col gap-4">
            <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wide">
              Pipeline Steps
            </h3>
            <div className="flex flex-col gap-4">
              {steps.map((step) => (
                <div key={step.id} className="flex items-center gap-3">
                  {step.status === "completed" && (
                    <CheckCircleIcon className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                  )}
                  {step.status === "running" && (
                    <div className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin flex-shrink-0"></div>
                  )}
                  {step.status === "pending" && (
                    <div className="w-5 h-5 rounded-full border border-slate-800 flex-shrink-0"></div>
                  )}
                  {step.status === "failed" && (
                    <span className="w-5 h-5 rounded-full bg-red-500/20 text-red-500 font-bold flex items-center justify-center text-xs flex-shrink-0">
                      ✕
                    </span>
                  )}
                  <span
                    className={`text-sm font-semibold ${
                      step.status === "completed"
                        ? "text-slate-300"
                        : step.status === "running"
                          ? "text-primary font-extrabold"
                          : step.status === "failed"
                            ? "text-red-500"
                            : "text-slate-500"
                    }`}
                  >
                    {step.name}
                  </span>
                </div>
              ))}
            </div>

            {/* Countdown timer */}
            {steps.some((s) => s.status === "running") && (
              <div className="mt-4 pt-4 border-t border-slate-900 text-center">
                <p className="text-xs text-slate-500">Estimated remaining</p>
                <p className="text-xl font-bold text-slate-300 mt-1">
                  ~{estimatedSeconds}s
                </p>
              </div>
            )}
          </div>

          {/* Logs terminal Console Right */}
          <div className="md:col-span-2 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 select-none">
              <CommandLineIcon className="w-4 h-4 text-primary" />
              <span>Console Logs Output</span>
            </div>
            <div className="bg-black/80 rounded-2xl border border-slate-900 p-5 font-mono text-xs text-emerald-400 h-64 overflow-y-auto flex flex-col gap-1.5 shadow-inner">
              {logs.map((log, idx) => (
                <div key={idx} className="whitespace-pre-wrap leading-relaxed">
                  {log}
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Processing;
