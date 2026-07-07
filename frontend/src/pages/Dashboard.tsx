import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiService } from "../services/api";
import type { ProjectResponse } from "../services/api";
import Layout from "../components/Layout";
import {
  ArrowUpTrayIcon,
  FilmIcon,
  StarIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  PencilIcon,
  MagnifyingGlassIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { StarIcon as StarSolid } from "@heroicons/react/24/solid";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { setProjectId, setCurrentVideo } = useApp();
  const { currentUser, logout } = useAuth();
  const { showToast } = useToast();

  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterFavorite, setFilterFavorite] = useState(false);
  const [sortBy, setSortBy] = useState<"name" | "created" | "updated">("updated");

  const fetchProjects = async () => {
    try {
      const list = await apiService.listProjects();
      setProjects(list);
    } catch (e) {
      console.error(e);
      showToast("Failed to retrieve projects list.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleUploadClick = () => {
    // Clear project context when starting new uploads
    setProjectId("");
    setCurrentVideo(null);
    navigate("/upload");
  };

  const handleProjectSelect = (project: ProjectResponse) => {
    setProjectId(project.id);
    // Construct fake VideoMetadata to satisfy AppContext requirements
    setCurrentVideo({
      id: project.video_id,
      filename: project.name,
      size: 0,
      duration: 10.0,
      status: "completed",
    });
    navigate("/preview");
  };

  const handleRename = async (e: React.MouseEvent, project: ProjectResponse) => {
    e.stopPropagation();
    const newName = prompt("Enter new project name:", project.name);
    if (!newName || newName.trim() === "") return;

    try {
      const updated = await apiService.updateProject(project.id, {
        name: newName.trim(),
      });
      setProjects((prev) =>
        prev.map((p) => (p.id === project.id ? updated : p))
      );
      showToast("Project renamed successfully", "success");
    } catch (err) {
      console.error(err);
      showToast("Rename failed", "error");
    }
  };

  const handleFavoriteToggle = async (
    e: React.MouseEvent,
    project: ProjectResponse
  ) => {
    e.stopPropagation();
    try {
      const updated = await apiService.updateProject(project.id, {
        is_favorite: !project.is_favorite,
      });
      setProjects((prev) =>
        prev.map((p) => (p.id === project.id ? updated : p))
      );
    } catch (err) {
      console.error(err);
      showToast("Failed to toggle favorite status", "error");
    }
  };

  const handleDuplicate = async (
    e: React.MouseEvent,
    project: ProjectResponse
  ) => {
    e.stopPropagation();
    try {
      const clone = await apiService.duplicateProject(project.id);
      setProjects((prev) => [clone, ...prev]);
      showToast("Project duplicated successfully", "success");
    } catch (err) {
      console.error(err);
      showToast("Duplication failed", "error");
    }
  };

  const handleDelete = async (e: React.MouseEvent, project: ProjectResponse) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete "${project.name}"?`)) return;

    try {
      await apiService.deleteProject(project.id);
      setProjects((prev) => prev.filter((p) => p.id !== project.id));
      showToast("Project deleted", "success");
    } catch (err) {
      console.error(err);
      showToast("Deletion failed", "error");
    }
  };

  const handleSignOut = async () => {
    await logout();
    showToast("Signed out successfully", "success");
    navigate("/login");
  };

  // Sorting & Filtering
  const processedProjects = projects
    .filter((p) => p.name.toLowerCase().includes(search.toLowerCase()))
    .filter((p) => (filterFavorite ? p.is_favorite : true))
    .sort((a, b) => {
      if (sortBy === "name") {
        return a.name.localeCompare(b.name);
      } else if (sortBy === "created") {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else {
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      }
    });

  return (
    <Layout>
      <div className="flex flex-col gap-8 max-w-5xl mx-auto">
        {/* Welcome Banner */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
              Hello, {currentUser?.name || "Creator"}!
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Upload reels, apply custom caption overlays, and organize your workspaces.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSignOut}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl font-bold bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer text-xs"
            >
              <ArrowRightOnRectangleIcon className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
            <button
              onClick={handleUploadClick}
              className="flex items-center gap-2 px-5 py-3 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/10 transition-all cursor-pointer select-none text-sm"
            >
              <ArrowUpTrayIcon className="w-5 h-5" />
              <span>Upload New Video</span>
            </button>
          </div>
        </div>

        {/* Toolbar: Search, Sort, Filter */}
        <div className="flex flex-col md:flex-row justify-between items-stretch md:items-center gap-4 bg-slate-950/40 p-4 rounded-2xl border border-slate-900/60">
          {/* Search bar */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search projects by name..."
              className="w-full bg-slate-900/40 border border-slate-800 focus:border-primary text-slate-100 rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none transition-all"
            />
          </div>

          {/* Sort & Filter */}
          <div className="flex items-center gap-3">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-slate-900/40 border border-slate-800 text-slate-350 text-xs rounded-xl px-3 py-2.5 outline-none transition-all cursor-pointer font-bold"
            >
              <option value="updated">Sort: Recently Edited</option>
              <option value="created">Sort: Recently Created</option>
              <option value="name">Sort: Alphabetical</option>
            </select>

            <button
              onClick={() => setFilterFavorite((prev) => !prev)}
              className={`flex items-center gap-1.5 px-3 py-2.5 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                filterFavorite
                  ? "bg-amber-500/10 text-amber-500 border-amber-500/20"
                  : "bg-slate-900/40 text-slate-400 border-slate-800 hover:text-slate-200"
              }`}
            >
              {filterFavorite ? (
                <StarSolid className="w-4 h-4 text-amber-500" />
              ) : (
                <StarIcon className="w-4 h-4" />
              )}
              <span>Favorites Only</span>
            </button>
          </div>
        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
          </div>
        )}

        {/* Empty CTA Card */}
        {!loading && processedProjects.length === 0 && (
          <div
            onClick={handleUploadClick}
            className="group glass-card border border-dashed border-slate-800 hover:border-primary/50 p-16 rounded-3xl flex flex-col items-center justify-center gap-4 text-center cursor-pointer transition-all duration-300 hover:shadow-lg hover:shadow-primary/5"
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/5 group-hover:bg-primary/10 flex items-center justify-center text-slate-400 group-hover:text-primary transition-all duration-300">
              <ArrowUpTrayIcon className="w-8 h-8 group-hover:scale-110 transition-transform" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-200">
                {search ? "No Projects Found" : "Start by Uploading a Video"}
              </h3>
              <p className="text-slate-400 text-sm max-w-sm mt-1 mx-auto">
                {search
                  ? "Try resetting search query input terms."
                  : "Upload dynamic captions workflows and start organizing workspaces."}
              </p>
            </div>
          </div>
        )}

        {/* Projects Grid */}
        {!loading && processedProjects.length > 0 && (
          <div className="flex flex-col gap-4">
            <div className="grid md:grid-cols-2 gap-4">
              {processedProjects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => handleProjectSelect(project)}
                  className="glass-card p-5 rounded-2xl border border-slate-900 hover:border-slate-800 flex items-start gap-4 cursor-pointer transition-all duration-200 hover:translate-y-[-2px] hover:shadow-md"
                >
                  <div className="w-12 h-12 rounded-xl bg-slate-900/60 flex items-center justify-center text-primary shadow-inner">
                    <FilmIcon className="w-6 h-6" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-250 truncate text-sm">
                        {project.name}
                      </h4>
                      {project.is_favorite && (
                        <StarSolid className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                      )}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      Edited: {new Date(project.updated_at).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Actions Toolbar on Card */}
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={(e) => handleFavoriteToggle(e, project)}
                      className="p-1.5 rounded hover:bg-slate-900 text-slate-500 hover:text-amber-500 transition-all cursor-pointer"
                      title="Favorite"
                    >
                      {project.is_favorite ? (
                        <StarSolid className="w-4 h-4 text-amber-500" />
                      ) : (
                        <StarIcon className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      onClick={(e) => handleRename(e, project)}
                      className="p-1.5 rounded hover:bg-slate-900 text-slate-500 hover:text-primary transition-all cursor-pointer"
                      title="Rename"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => handleDuplicate(e, project)}
                      className="p-1.5 rounded hover:bg-slate-900 text-slate-500 hover:text-slate-350 transition-all cursor-pointer"
                      title="Duplicate"
                    >
                      <DocumentDuplicateIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(e, project)}
                      className="p-1.5 rounded hover:bg-slate-900 text-slate-500 hover:text-red-500 transition-all cursor-pointer"
                      title="Delete"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
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
