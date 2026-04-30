import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../api/client";

const FILE_TYPES = [
  { ext: "CSV",  color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
  { ext: "XLSX", color: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
  { ext: "PDF",  color: "bg-rose-500/15 text-rose-400 border-rose-500/30" },
  { ext: "PNG",  color: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  { ext: "JPG",  color: "bg-purple-500/15 text-purple-400 border-purple-500/30" },
];

export default function Upload() {
  const [dragging, setDragging]   = useState(false);
  const [loading,  setLoading]    = useState(false);
  const [progress, setProgress]   = useState(0);
  const [fileName, setFileName]   = useState(null);
  const [error,    setError]      = useState(null);
  const fileRef  = useRef(null);
  const navigate = useNavigate();

  /* ── fake progress bar while awaiting API ── */
  const startFakeProgress = () => {
    setProgress(0);
    const id = setInterval(() => {
      setProgress((p) => {
        if (p >= 85) { clearInterval(id); return p; }
        return p + Math.random() * 8;
      });
    }, 280);
    return id;
  };

  const handleFile = async (file) => {
    setFileName(file.name);
    setLoading(true);
    setError(null);
    const pid = startFakeProgress();
    try {
      const data = await uploadFile(file);
      clearInterval(pid);
      setProgress(100);
      setTimeout(() => navigate(`/dashboard/${data.table_name}`, { state: data }), 400);
    } catch (err) {
      clearInterval(pid);
      setProgress(0);
      setLoading(false);
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onFileInput = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="min-h-screen bg-[#111111] text-white flex flex-col">

      {/* ── Navbar ── */}
      <nav className="flex items-center justify-between px-10 py-5">
        <button
          onClick={() => navigate("/")}
          className="text-xl font-bold tracking-tight hover:opacity-80 transition"
        >
          datamind.
        </button>
        <div className="flex items-center gap-4">
          <button className="text-gray-400 hover:text-white text-sm transition">Sign up</button>
          <button className="bg-[#c4b5fd] hover:bg-[#a78bfa] text-gray-900 font-medium text-sm px-5 py-2 rounded-full transition">
            Log in
          </button>
        </div>
      </nav>

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 pb-20 relative overflow-hidden">

        {/* Ambient glow */}
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="w-[600px] h-[600px] rounded-full bg-violet-600/10 blur-[120px]" />
        </div>

        {/* Header text */}
        <div className="text-center mb-10 relative z-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-violet-400 mb-4 flex items-center justify-center gap-2">
            <span className="w-5 h-px bg-violet-400/60" />
            Step 1 of 1
            <span className="w-5 h-px bg-violet-400/60" />
          </p>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">
            Upload your data
          </h1>
          <p className="text-gray-400 text-base max-w-sm mx-auto leading-relaxed">
            Drop any file and we'll turn it into a live, queryable dashboard in seconds.
          </p>
        </div>

        {/* File-type pills */}
        <div className="flex items-center gap-2 mb-8 flex-wrap justify-center relative z-10">
          {FILE_TYPES.map((t) => (
            <span
              key={t.ext}
              className={`text-xs font-semibold px-3 py-1 rounded-full border ${t.color}`}
            >
              {t.ext}
            </span>
          ))}
        </div>

        {/* Drop zone */}
        <div
          className={`relative z-10 w-full max-w-xl rounded-3xl border-2 border-dashed p-1 transition-all duration-300 cursor-pointer
            ${dragging
              ? "border-violet-500 shadow-[0_0_40px_rgba(139,92,246,0.25)]"
              : "border-white/10 hover:border-white/25 hover:shadow-[0_0_30px_rgba(139,92,246,0.12)]"
            }`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => !loading && fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            onChange={onFileInput}
            accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg"
          />

          <div className="bg-[#1a1a1a] rounded-[22px] px-8 py-12 text-center">
            {loading ? (
              /* ── Loading state ── */
              <div className="flex flex-col items-center gap-5">
                <div className="relative w-16 h-16">
                  <svg className="absolute inset-0 animate-spin" viewBox="0 0 64 64" fill="none">
                    <circle cx="32" cy="32" r="28" stroke="#2e2e2e" strokeWidth="4" />
                    <circle
                      cx="32" cy="32" r="28"
                      stroke="#8b5cf6" strokeWidth="4"
                      strokeDasharray="44 132"
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-xl">⚙️</span>
                </div>

                <div className="w-full max-w-xs">
                  <div className="flex justify-between text-xs text-gray-500 mb-2">
                    <span className="truncate max-w-[200px] text-gray-300">{fileName}</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                <p className="text-gray-400 text-sm">Analyzing your data…</p>
              </div>
            ) : (
              /* ── Idle state ── */
              <>
                {/* Icon circle */}
                <div className="mx-auto w-20 h-20 rounded-2xl bg-white/5 border border-white/8 flex items-center justify-center mb-6 group-hover:bg-white/8 transition">
                  <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                    <path d="M18 4v20M10 12l8-8 8 8" stroke="#8b5cf6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M6 28h24" stroke="#6b7280" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>

                <p className="text-white text-lg font-semibold mb-2">
                  {dragging ? "Release to upload" : "Drag & drop your file here"}
                </p>
                <p className="text-gray-500 text-sm mb-8">
                  or click anywhere to browse from your computer
                </p>

                <button
                  className="bg-[#c4b5fd] hover:bg-[#a78bfa] text-gray-900 font-semibold px-7 py-2.5 rounded-full transition text-sm"
                  onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}
                >
                  Choose file
                </button>
              </>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="relative z-10 mt-5 max-w-xl w-full bg-red-950/60 border border-red-500/40 text-red-300 px-5 py-4 rounded-2xl text-sm flex items-start gap-3">
            <span className="mt-0.5 shrink-0">✕</span>
            <span>{error}</span>
          </div>
        )}

        {/* Bottom hint */}
        {!loading && (
          <p className="relative z-10 mt-8 text-gray-600 text-xs text-center max-w-xs">
            Your data is processed locally and never shared with third parties.
          </p>
        )}
      </div>
    </div>
  );
}
