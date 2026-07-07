import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService } from "../services/api";
import Layout from "../components/Layout";
import { CheckCircleIcon, CommandLineIcon } from "@heroicons/react/24/outline";

interface Step {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
}

const Processing: React.FC = () => {
  const navigate = useNavigate();
  const { currentVideo, projectId, setProjectId, setCurrentSubtitle } =
    useApp();
  const { showToast } = useToast();

  const [steps, setSteps] = useState<Step[]>([
    { id: "queued", name: "Job Queued", status: "pending" },
    { id: "extracting_audio", name: "Extract Audio", status: "pending" },
    { id: "transcribing", name: "Transcribing Speech", status: "pending" },
    { id: "aligning", name: "Phonemes Alignment", status: "pending" },
    { id: "subtitle_generation", name: "Subtitle Generation", status: "pending" },
  ]);

  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const processingStartedRef = useRef(false);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`]);
  };

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);



  useEffect(() => {
    if (!currentVideo) {
      showToast("No active video session found. Redirecting...", "warning");
      navigate("/upload");
      return;
    }

    if (processingStartedRef.current) return;
    processingStartedRef.current = true;

    const runBackgroundPipeline = async () => {
      let activeProjectId = projectId;

      // 1. Ensure project exists
      if (!activeProjectId) {
        try {
          addLog("Creating editing project on database...");
          const project = await apiService.createProject(currentVideo.id);
          activeProjectId = project.id;
          setProjectId(project.id);
          addLog(`Project created successfully. Project ID: ${project.id}`);
        } catch (e: any) {
          addLog(`Error: Failed to create project. ${e.message}`);
          showToast("Failed to initialize project.", "error");
          return;
        }
      }

      // 2. Trigger async background job
      let activeJobId = "";
      try {
        addLog("Submitting processing pipeline to Celery queue...");
        const job = await apiService.createJob(activeProjectId);
        activeJobId = job.id;
        setJobId(job.id);
        addLog(`Job queued successfully. Job ID: ${job.id}`);
        setSteps((prev) =>
          prev.map((s) => (s.id === "queued" ? { ...s, status: "completed" } : s))
        );
      } catch (e: any) {
        addLog(`Error: Failed to queue job. ${e.message}`);
        showToast("Queue submission failed.", "error");
        return;
      }

      // 3. Connect to live progress WebSocket channel
      try {
        const wsUrl = apiService.getJobProgressWsUrl(activeJobId);
        addLog(`Opening WebSocket connection: ${wsUrl}`);
        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onopen = () => {
          addLog("WebSocket channel connected. Listening for progress events...");
        };

        socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.error) {
            addLog(`Error: ${data.error}`);
            showToast("Job tracker error.", "error");
            return;
          }

          // Update active progress stats
          setProgress(data.progress);
          addLog(data.current_step);

          // Update step items state machine
          const activeStatus = data.status;
          setSteps((prev) =>
            prev.map((step) => {
              if (step.id === activeStatus) {
                return { ...step, status: "running" };
              }
              // Mark previous steps as completed
              if (
                (activeStatus === "transcribing" && step.id === "extracting_audio") ||
                (activeStatus === "aligning" &&
                  (step.id === "extracting_audio" || step.id === "transcribing")) ||
                (activeStatus === "subtitle_generation" &&
                  (step.id === "extracting_audio" ||
                    step.id === "transcribing" ||
                    step.id === "aligning")) ||
                (activeStatus === "completed" && step.id !== "queued")
              ) {
                return { ...step, status: "completed" };
              }
              if (activeStatus === "failed" && step.status === "running") {
                return { ...step, status: "failed" };
              }
              return step;
            })
          );

          if (activeStatus === "completed") {
            showToast("Speech alignment pipeline completed!", "success");
            addLog("Redirecting to caption workspace in 2 seconds...");
            socket.close();

            // Populate mock subtitle response in context for Preview compatibility
            setCurrentSubtitle({
              id: currentVideo.id,
              subtitle_files: {
                json: `subtitles/subtitles_${currentVideo.id}.json`,
                srt: `subtitles/subtitles_${currentVideo.id}.srt`,
                ass: `subtitles/subtitles_${currentVideo.id}.ass`,
              },
            });

            setTimeout(() => {
              navigate("/preview");
            }, 2000);
          } else if (activeStatus === "failed") {
            showToast("Pipeline task failed.", "error");
            addLog(`CRITICAL: Job execution halted. Reason: ${data.error_message}`);
            socket.close();
          } else if (activeStatus === "cancelled") {
            showToast("Job cancelled by user.", "warning");
            addLog("Job execution cancelled.");
            socket.close();
          }
        };

        socket.onerror = (e) => {
          addLog("WebSocket encountered an error. Reconnecting or polling...");
          console.error(e);
        };

        socket.onclose = () => {
          addLog("WebSocket channel closed.");
        };
      } catch (e: any) {
        addLog(`WebSocket initialization failed: ${e.message}. Polling DB...`);
      }
    };

    runBackgroundPipeline();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [currentVideo]);

  const handleCancelJob = async () => {
    if (!jobId) return;
    try {
      addLog("Sending cancellation request to background worker...");
      await apiService.cancelJob(jobId);
      showToast("Cancellation request sent", "info");
      setSteps((prev) =>
        prev.map((s) => (s.status === "running" ? { ...s, status: "failed" } : s))
      );
    } catch (e: any) {
      console.error(e);
      showToast("Failed to abort job.", "error");
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">
            Background Processing Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Running async Faster-Whisper transcription and alignments.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          {/* Stepper Status Left */}
          <div className="md:col-span-1 glass-card p-6 rounded-2xl border border-slate-900 flex flex-col gap-5">
            <div className="flex justify-between items-center select-none">
              <h3 className="font-bold text-xs text-slate-350 uppercase tracking-wider">
                Pipeline Steps
              </h3>
              {jobId && progress < 100 && (
                <button
                  onClick={handleCancelJob}
                  className="px-2.5 py-1 text-[10px] font-black rounded bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/25 transition-all cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>

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
                    <span className="w-5 h-5 rounded-full bg-red-500/20 text-red-500 font-bold flex items-center justify-center text-[10px] flex-shrink-0 select-none">
                      ✕
                    </span>
                  )}
                  <span
                    className={`text-xs font-bold ${
                      step.status === "completed"
                        ? "text-slate-400"
                        : step.status === "running"
                          ? "text-primary font-extrabold"
                          : step.status === "failed"
                            ? "text-red-500"
                            : "text-slate-600"
                    }`}
                  >
                    {step.name}
                  </span>
                </div>
              ))}
            </div>

            {/* Progress Percentage Display */}
            <div className="mt-2 pt-4 border-t border-slate-900 flex flex-col gap-2">
              <div className="flex justify-between text-xs font-bold text-slate-450 select-none">
                <span>Total Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-950 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Logs terminal Console Right */}
          <div className="md:col-span-2 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 select-none">
              <CommandLineIcon className="w-4 h-4 text-primary" />
              <span>Job Progress Tracker & Logs Output</span>
            </div>
            <div className="bg-black/90 rounded-2xl border border-slate-950 p-5 font-mono text-xs text-emerald-400 h-64 overflow-y-auto flex flex-col gap-1.5 shadow-inner">
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
