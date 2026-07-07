import React from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="flex flex-col items-center justify-center gap-4 text-center py-20 select-none">
        <h1 className="text-6xl font-extrabold text-primary">404</h1>
        <h2 className="text-xl font-bold text-slate-200">Page Not Found</h2>
        <p className="text-slate-400 text-sm max-w-sm mt-1 mx-auto leading-relaxed">
          The requested page route could not be found or has been moved.
        </p>
        <button
          onClick={() => navigate("/dashboard")}
          className="mt-4 px-6 py-3 rounded-xl font-bold bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/10 transition-all cursor-pointer"
        >
          Back to Dashboard
        </button>
      </div>
    </Layout>
  );
};

export default NotFound;
