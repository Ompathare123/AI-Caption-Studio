import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService, type RenderStatusResponse } from "../services/api";
import Layout from "../components/Layout";
import {
  ArrowDownTrayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

const Export: React.FC = () => {
  const navigate = useNavigate();
  const { renderId, currentSubtitle } = useApp();
  const { showToast } = useToast();

  const [status, setStatus] = useState<RenderStatusResponse | null>(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (!renderId) {
      showToast("No active rendering task tracking session found.", "warning");
      navigate("/dashboard");
      return;
    }

    setPolling(true);

    const checkStatus = async () => {
      try {
        const res = await apiService.getRenderStatus(renderId);
        setStatus(res);

        if (res.status === "completed" || res.status === "failed") {
          setPolling(false);
          if (res.status === "completed") {
            showToast("Video render completed!", "success");
          } else {
            showToast("Video render failed.", "error");
          }
        }
      } catch (e) {
        console.error(e);
        setPolling(false);
        showToast("Failed to retrieve render status.", "error");
      }
    };

    // Immediate check
    checkStatus();

    // Poll every 2 seconds
    const interval = setInterval(() => {
      if (polling) {
        checkStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [renderId, polling]);

  const handleDownloadVideo = () => {
    if (!status?.output_path) return;
    const downloadUrl = apiService.getMediaUrl(status.output_path);
    window.open(downloadUrl, "_blank");
  };

  const handleDownloadSubtitles = (format: "srt" | "ass" | "json") => {
    if (!currentSubtitle) return;
    const path = currentSubtitle.subtitle_files[format];
    const downloadUrl = apiService.getMediaUrl(path);
    window.open(downloadUrl, "_blank");
  };

  return (
    <Layout>
      <div className="max-w-xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">
            Export & Download
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Re-muxing final audio layers and rendering styled subtitle overlays.
          </p>
        </div>

        {/* Polling / Progress Card */}
        {status &&
          (status.status === "processing" || status.status === "rendering") && (
            <div className="glass-card p-6 rounded-3xl border border-slate-900 flex flex-col gap-6 text-center">
              <div className="flex flex-col items-center gap-2 select-none">
                <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin flex items-center justify-center"></div>
                <h3 className="font-bold text-slate-200 mt-2">
                  Rendering Styled Captions...
                </h3>
                <p className="text-xs text-slate-500">
                  This takes a few moments depending on video size.
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-xs font-bold text-slate-400">
                  <span>Drawing frame buffers...</span>
                  <span>{status.progress}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

        {/* Success Card */}
        {status && status.status === "completed" && (
          <div className="glass-card p-6 rounded-3xl border border-slate-900 flex flex-col gap-6">
            <div className="flex items-center gap-4">
              <CheckCircleIcon className="w-12 h-12 text-emerald-500 flex-shrink-0" />
              <div>
                <h3 className="font-bold text-lg text-slate-100">
                  Render Successful!
                </h3>
                <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                  Styled captions are merged frame-accurately with the original
                  audio track.
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <button
                onClick={handleDownloadVideo}
                className="w-full py-4 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 cursor-pointer select-none"
              >
                <ArrowDownTrayIcon className="w-5 h-5" />
                <span>Download Captioned Video</span>
              </button>

              <div className="grid grid-cols-3 gap-2 mt-2">
                <button
                  onClick={() => handleDownloadSubtitles("srt")}
                  className="py-2.5 rounded-lg text-xs font-bold bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 cursor-pointer flex items-center justify-center gap-1.5 select-none"
                >
                  <ArrowDownTrayIcon className="w-3.5 h-3.5" />
                  <span>SRT</span>
                </button>

                <button
                  onClick={() => handleDownloadSubtitles("ass")}
                  className="py-2.5 rounded-lg text-xs font-bold bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 cursor-pointer flex items-center justify-center gap-1.5 select-none"
                >
                  <ArrowDownTrayIcon className="w-3.5 h-3.5" />
                  <span>ASS</span>
                </button>

                <button
                  onClick={() => handleDownloadSubtitles("json")}
                  className="py-2.5 rounded-lg text-xs font-bold bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 cursor-pointer flex items-center justify-center gap-1.5 select-none"
                >
                  <ArrowDownTrayIcon className="w-3.5 h-3.5" />
                  <span>JSON</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Failure Card */}
        {status && status.status === "failed" && (
          <div className="glass-card p-6 rounded-3xl border border-red-900/30 bg-red-950/5 flex flex-col gap-6 text-center">
            <div className="flex flex-col items-center gap-2 select-none">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-500" />
              <h3 className="font-bold text-red-500 mt-2">
                Video Rendering Failed
              </h3>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                {status.error_message ||
                  "An unexpected error occurred during frame encoding."}
              </p>
            </div>

            <button
              onClick={() => setPolling(true)}
              className="py-3 rounded-xl font-bold bg-slate-900 text-slate-300 border border-slate-800 hover:text-slate-100 flex items-center justify-center gap-2 cursor-pointer select-none"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>Retry Querying Status</span>
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Export;
