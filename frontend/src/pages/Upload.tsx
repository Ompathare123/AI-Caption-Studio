import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { useApp } from "../context/AppContext";
import { useToast } from "../context/ToastContext";
import { apiService } from "../services/api";
import Layout from "../components/Layout";
import { CloudArrowUpIcon, FilmIcon } from "@heroicons/react/24/outline";

const Upload: React.FC = () => {
  const navigate = useNavigate();
  const { setCurrentVideo, saveVideoToRecent } = useApp();
  const { showToast } = useToast();

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const handleUploadSubmit = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);
    showToast("Starting video upload...", "info");

    try {
      const metadata = await apiService.uploadVideo(file, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setProgress(percentCompleted);
      });

      showToast("Video upload successful!", "success");
      setCurrentVideo(metadata);
      saveVideoToRecent(metadata);

      // Transition to processing pipeline page
      navigate("/processing");
    } catch (e: any) {
      console.error(e);
      const errMsg = e.response?.data?.detail || "Failed to upload video.";
      showToast(errMsg, "error");
    } finally {
      setUploading(false);
    }
  };

  const formatSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <Layout>
      <div className="max-w-xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">
            Upload Project Video
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Select a video file to generate speech transcription overlays.
          </p>
        </div>

        {/* Dropzone Container */}
        <div
          {...getRootProps()}
          className={`glass-card border-2 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all duration-300 flex flex-col items-center gap-4 ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-slate-800 hover:border-slate-700"
          } ${uploading ? "pointer-events-none opacity-50" : ""}`}
        >
          <input {...getInputProps()} />
          <div className="w-16 h-16 rounded-full bg-slate-900 flex items-center justify-center text-slate-400">
            <CloudArrowUpIcon className="w-8 h-8 text-primary" />
          </div>

          <div>
            <p className="font-bold text-slate-200">
              {isDragActive
                ? "Drop your video file here"
                : "Drag & drop your video file"}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Supports MP4, MOV, AVI, MKV, or WebM formats up to 2GB.
            </p>
          </div>
        </div>

        {/* Selected File Details */}
        {file && (
          <div className="glass-card p-5 rounded-2xl border border-slate-900 flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-slate-900 text-primary">
                <FilmIcon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm text-slate-200 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {formatSize(file.size)}
                </p>
              </div>
            </div>

            {/* Progress Bar UI */}
            {uploading && (
              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-xs font-bold text-slate-400">
                  <span>Uploading video chunks...</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-200"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {!uploading && (
              <button
                onClick={handleUploadSubmit}
                className="w-full py-3.5 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/10 transition-all cursor-pointer select-none"
              >
                Upload and Process Video
              </button>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Upload;
