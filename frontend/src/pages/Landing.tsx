import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  SparklesIcon,
  PaintBrushIcon,
  BoltIcon,
  ArrowRightIcon,
} from "@heroicons/react/24/outline";

const Landing: React.FC = () => {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex flex-col items-center overflow-hidden">
      {/* Background Neon Glows */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-accent/10 rounded-full blur-[100px] pointer-events-none"></div>

      {/* Hero Section */}
      <section className="relative max-w-5xl mx-auto px-6 pt-24 pb-16 text-center z-10 flex flex-col items-center">
        {/* Glow Tag */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs font-bold mb-8 hover:bg-primary/10 transition-colors select-none"
        >
          <SparklesIcon className="w-4 h-4 animate-pulse" />
          <span>Automated Word-Level Timestamps Alignments</span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6"
        >
          Create Styled & Animated{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-indigo-400 to-accent">
            Social Captions
          </span>{" "}
          In Seconds
        </motion.h1>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-slate-400 text-lg md:text-xl max-w-2xl leading-relaxed mb-10"
        >
          Upload your video, automatically transcribe with Faster-Whisper, align
          timestamps, customize premium styles (TikTok/Hormozi), and export
          rendering-ready captioned videos.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <button
            onClick={handleStart}
            className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/20 transition-all cursor-pointer group"
          >
            <span>Get Started Free</span>
            <ArrowRightIcon className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-6 py-20 z-10 w-full">
        <h2 className="text-2xl md:text-3xl font-extrabold text-center mb-12">
          Designed for Short-Form Creators
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4 border border-slate-900">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-inner">
              <BoltIcon className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-slate-100">
              Fast Speech Isolation
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Faster-Whisper and WhisperX alignment processing run locally
              inside the backend to extract word boundaries.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4 border border-slate-900">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent shadow-inner">
              <PaintBrushIcon className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-slate-100">
              Style Customizations
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Tweak size, outline stroke weight, drop shadow offsets, rounded
              borders padding, font face files, and active colors.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4 border border-slate-900">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 shadow-inner">
              <SparklesIcon className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-slate-100">
              Dynamic Presets
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Select pop highlights, rotation spins, vertical slide transitions,
              bounce offsets, and letters opacity fade fades.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
