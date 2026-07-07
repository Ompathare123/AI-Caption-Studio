import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  HomeIcon,
  ArrowUpTrayIcon,
  FilmIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: HomeIcon },
    { name: "Upload Video", path: "/upload", icon: ArrowUpTrayIcon },
    { name: "Caption Preview", path: "/preview", icon: FilmIcon },
    { name: "Settings", path: "/settings", icon: Cog6ToothIcon },
  ];

  const handleLogoClick = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#030712] text-slate-100">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full glass-nav flex items-center justify-between px-6 py-4">
        <div
          className="flex items-center gap-3 cursor-pointer select-none"
          onClick={handleLogoClick}
        >
          {/* Studio Neon Logo */}
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold text-white shadow-lg shadow-primary/20">
            AI
          </div>
          <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-100 to-slate-400">
            Caption Studio
          </span>
        </div>

        {/* Desktop top bar status indicators */}
        <div className="hidden md:flex items-center gap-4 text-xs font-semibold text-slate-400">
          <span>Version 1.0.0</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-emerald-500">FastAPI backend online</span>
        </div>

        {/* Mobile menu toggler */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-1.5 rounded-lg border border-slate-800 hover:bg-slate-900 transition-colors cursor-pointer"
        >
          {mobileMenuOpen ? (
            <XMarkIcon className="w-6 h-6" />
          ) : (
            <Bars3Icon className="w-6 h-6" />
          )}
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar (Desktop) */}
        <aside className="hidden md:flex flex-col w-64 border-r border-slate-950 bg-[#030712]/50 p-4 gap-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 group ${
                  isActive
                    ? "bg-primary/10 text-primary border-l-4 border-primary shadow-sm shadow-primary/5"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                }`}
              >
                <Icon
                  className={`w-5 h-5 transition-transform group-hover:scale-105 ${
                    isActive
                      ? "text-primary"
                      : "text-slate-400 group-hover:text-slate-300"
                  }`}
                />
                {item.name}
              </Link>
            );
          })}
        </aside>

        {/* Mobile menu container */}
        {mobileMenuOpen && (
          <div className="absolute inset-x-0 top-[69px] bottom-0 z-30 bg-[#030712] flex flex-col p-6 gap-3 md:hidden">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-4 rounded-xl text-base font-bold ${
                    isActive
                      ? "bg-primary/10 text-primary border-l-4 border-primary"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-6 h-6" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        )}

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-gradient-to-b from-[#030712] to-[#070b19]">
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="py-4 px-6 border-t border-slate-950 text-center text-xs text-slate-600 flex flex-col md:flex-row items-center justify-between gap-2 bg-[#030712]">
        <span>© 2026 AI Caption Studio. All rights reserved.</span>
        <div className="flex gap-4">
          <a href="#" className="hover:text-slate-400 transition-colors">
            Terms
          </a>
          <a href="#" className="hover:text-slate-400 transition-colors">
            Privacy Policy
          </a>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
