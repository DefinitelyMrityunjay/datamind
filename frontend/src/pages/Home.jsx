import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../api/client";

export default function Home() {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFile = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const data = await uploadFile(file);
      navigate(`/dashboard/${data.table_name}`, { state: data });
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Try again.");
    } finally {
      setLoading(false);
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
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center px-4">

      {/* Logo */}
      <div className="mb-10 text-center">
        <h1 className="text-5xl font-bold text-white mb-3">DataMind</h1>
        <p className="text-gray-400 text-lg">
          Upload any data file and get instant AI-powered insights
        </p>
      </div>

      {/* Upload Box */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`w-full max-w-lg border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer
          ${dragging ? "border-indigo-500 bg-indigo-500/10" : "border-gray-600 bg-gray-800 hover:border-indigo-400"}`}
      >
        <div className="text-5xl mb-4">📂</div>
        <p className="text-white text-lg font-medium mb-2">
          Drag & drop your file here
        </p>
        <p className="text-gray-400 text-sm mb-6">
          Supports CSV, Excel, PDF, PNG, JPG
        </p>
        <label className="cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-medium transition-all">
          Browse Files
          <input type="file" className="hidden" onChange={onFileInput}
            accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg" />
        </label>
      </div>

      {/* Loading */}
      {loading && (
        <div className="mt-8 text-center">
          <div className="animate-spin text-4xl mb-3">⚙️</div>
          <p className="text-gray-400">Processing your file...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-6 bg-red-900/50 border border-red-500 text-red-300 px-6 py-4 rounded-xl max-w-lg w-full">
          ❌ {error}
        </div>
      )}

      {/* Features */}
      <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl w-full">
        {[
          { icon: "📥", label: "Any File Format" },
          { icon: "🗄️", label: "Live Database" },
          { icon: "📊", label: "Auto Charts" },
          { icon: "🤖", label: "AI Insights" },
        ].map((f) => (
          <div key={f.label} className="bg-gray-800 rounded-xl p-4 text-center border border-gray-700">
            <div className="text-2xl mb-2">{f.icon}</div>
            <p className="text-gray-300 text-sm">{f.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}