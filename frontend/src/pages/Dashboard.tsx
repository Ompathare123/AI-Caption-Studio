import React from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import Layout from "../components/Layout";
import {
  ArrowUpTrayIcon,
  FilmIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { recentVideos, setCurrentVideo } = useApp();

  const handleUploadClick = () => {
    navigate("/upload");
  };

  const handleVideoSelect = (video: any) => {
    setCurrentVideo(video);
    navigate("/preview");
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <Layout>
      <div className="flex flex-col gap-8 max-w-5xl mx-auto">
        {/* Welcome Banner */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
              Welcome to Studio Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Upload videos, edit dynamic word aligned animations, and export
              styled captioned reels.
            </p>
          </div>

          <button
            onClick={handleUploadClick}
            className="flex items-center gap-2 px-5 py-3 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/10 transition-all cursor-pointer select-none"
          >
            <ArrowUpTrayIcon className="w-5 h-5" />
            <span>Upload New Video</span>
          </button>
        </div>

        {/* New Upload CTA Card */}
        {recentVideos.length === 0 && (
          <div
            onClick={handleUploadClick}
            className="group glass-card border border-dashed border-slate-800 hover:border-primary/50 p-12 rounded-3xl flex flex-col items-center justify-center gap-4 text-center cursor-pointer transition-all duration-300 hover:shadow-lg hover:shadow-primary/5"
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/5 group-hover:bg-primary/10 flex items-center justify-center text-slate-400 group-hover:text-primary transition-all duration-300">
              <ArrowUpTrayIcon className="w-8 h-8 group-hover:scale-110 transition-transform" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-200">
                Start by Uploading a Video
              </h3>
              <p className="text-slate-400 text-sm max-w-sm mt-1 mx-auto">
                Drag and drop your reels, TikToks, or shorts here to
                automatically generate high quality subtitles.
              </p>
            </div>
          </div>
        )}

        {/* Recent Videos Grid */}
        {recentVideos.length > 0 && (
          <div className="flex flex-col gap-4">
            <h2 className="text-lg font-bold text-slate-300 flex items-center gap-2 select-none">
              <FilmIcon className="w-5 h-5 text-primary" />
              <span>Recent Caption Projects</span>
            </h2>

            <div className="grid md:grid-cols-2 gap-4">
              {recentVideos.map((video) => (
                <div
                  key={video.id}
                  onClick={() => handleVideoSelect(video)}
                  className="glass-card p-5 rounded-2xl border border-slate-900 hover:border-slate-800 flex items-start gap-4 cursor-pointer transition-all duration-205 hover:translate-y-[-2px] hover:shadow-md hover:shadow-slate-950"
                >
                  <div className="w-12 h-12 rounded-xl bg-slate-900 flex items-center justify-center text-primary shadow-inner">
                    <FilmIcon className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-slate-200 truncate">
                      {video.filename}
                    </h4>
                    <div className="flex items-center gap-3 text-xs text-slate-500 mt-2">
                      <span className="flex items-center gap-1">
                        <ClockIcon className="w-3.5 h-3.5" />
                        {formatDuration(video.duration)}
                      </span>
                      <span>•</span>
                      <span>{formatSize(video.size)}</span>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2 text-right">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wide">
                      {video.status}
                    </span>
                    <span className="text-[10px] text-slate-600">
                      ID: {video.id.substring(0, 8)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;
