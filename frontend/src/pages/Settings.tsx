import React from "react";
import Layout from "../components/Layout";
import { Cog6ToothIcon } from "@heroicons/react/24/outline";

const Settings: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2 select-none">
            <Cog6ToothIcon className="w-7 h-7 text-primary" />
            <span>Application Settings</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Configure default engine configurations for the studio workspace.
          </p>
        </div>

        <div className="glass-card p-6 rounded-3xl border border-slate-900 flex flex-col gap-6">
          {/* ASR Model Settings */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
              Speech-to-Text Model Size
            </label>
            <select
              defaultValue="base"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-300 focus:outline-none focus:border-primary cursor-pointer"
            >
              <option value="tiny">Tiny (Ultra fast, lower accuracy)</option>
              <option value="base">Base (Fast, moderate accuracy)</option>
              <option value="small">Small (Balanced speed and accuracy)</option>
              <option value="medium">
                Medium (Accurate, requires more RAM)
              </option>
              <option value="large-v3">
                Large V3 (High accuracy, heavy memory load)
              </option>
            </select>
          </div>

          {/* Alignment Model */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
              Alignment Language Model
            </label>
            <input
              type="text"
              readOnly
              value="Wav2Vec2 English (default)"
              className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-500 cursor-not-allowed focus:outline-none"
            />
          </div>

          {/* Export Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Render Quality
              </label>
              <select
                defaultValue="18"
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none cursor-pointer"
              >
                <option value="12">High (CRF 12)</option>
                <option value="18">Balanced (CRF 18)</option>
                <option value="23">Standard (CRF 23)</option>
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Video Codec
              </label>
              <select
                defaultValue="h264"
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none cursor-pointer"
              >
                <option value="h264">H.264 (AVC)</option>
                <option value="hevc">H.265 (HEVC)</option>
                <option value="vp9">VP9 (WebM)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;
