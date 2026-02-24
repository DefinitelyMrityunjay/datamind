import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getDashboard } from "../api/client";
import MetricCard from "../components/MetricCard";
import BarChart from "../components/BarChart";
import LineChart from "../components/LineChart";
import DataTable from "../components/DataTable";
import InsightsCard from "../components/InsightsCard";

export default function Dashboard() {
  const { tableName } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboard(tableName)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [tableName]);

  if (loading) return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin text-5xl mb-4">⚙️</div>
        <p className="text-gray-400 text-lg">Building your dashboard...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <p className="text-red-400">❌ {error}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 px-6 py-8">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">🧠 AnalyzeIQ</h1>
          <p className="text-gray-400 mt-1">
            Table: <span className="text-indigo-400 font-mono">{tableName}</span>
          </p>
        </div>
        <button
          onClick={() => navigate("/")}
          className="bg-gray-800 hover:bg-gray-700 text-white px-5 py-2 rounded-xl border border-gray-700 transition-all"
        >
          ← Upload New File
        </button>
      </div>

      {/* Metrics */}
      {data.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {Object.entries(data.metrics).slice(0, 4).map(([key, val]) => (
            <MetricCard
              key={key}
              label={key.replace(/_/g, " ").toUpperCase()}
              value={val.sum}
              avg={val.mean}
            />
          ))}
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {data.bar_chart && (
          <BarChart
            data={data.bar_chart}
            xLabel={data.bar_chart.x_label}
            yLabel={data.bar_chart.y_label}
          />
        )}
        {data.line_chart && (
          <LineChart
            data={data.line_chart}
            xLabel={data.line_chart.x_label}
            yLabel={data.line_chart.y_label}
          />
        )}
      </div>

      {/* AI Insights */}
      <div className="mb-8">
        <InsightsCard insights={data.insights} />
      </div>

      {/* Data Table */}
      <DataTable data={data.raw_data} />

    </div>
  );
}