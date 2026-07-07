import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { showToast } = useToast();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) {
      showToast("Please fill in all fields", "warning");
      return;
    }
    if (password.length < 6) {
      showToast("Password must be at least 6 characters long", "warning");
      return;
    }
    setLoading(true);
    try {
      await register(email, password, name);
      showToast("Account created successfully!", "success");
      navigate("/");
    } catch (err: any) {
      console.error(err);
      showToast(
        err.response?.data?.detail || "Registration failed. Try again.",
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070913] flex items-center justify-center p-4">
      <div className="w-full max-w-md glass-card p-8 rounded-3xl border border-slate-900 shadow-2xl flex flex-col gap-6">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-slate-100 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Get Started
          </h2>
          <p className="text-slate-400 text-sm mt-2 font-medium">
            Create your account to start captioning videos
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="w-full bg-slate-950/80 border border-slate-850 focus:border-primary text-slate-100 rounded-xl px-4 py-3 text-sm transition-all outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full bg-slate-950/80 border border-slate-850 focus:border-primary text-slate-100 rounded-xl px-4 py-3 text-sm transition-all outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="•••••••• (6+ characters)"
              className="w-full bg-slate-950/80 border border-slate-850 focus:border-primary text-slate-100 rounded-xl px-4 py-3 text-sm transition-all outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 bg-gradient-to-r from-primary to-accent hover:from-primary-hover hover:to-accent-hover text-slate-950 font-black rounded-xl text-sm transition-all flex justify-center items-center cursor-pointer shadow-lg disabled:opacity-55 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="w-5 h-5 rounded-full border-2 border-slate-950 border-t-transparent animate-spin"></div>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 font-medium">
          Already have an account?{" "}
          <Link to="/login" className="text-primary font-black hover:underline">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
