import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getDashboard } from "../api/client";
import MetricCard from "../components/MetricCard";
import BarChart from "../components/BarChart";
import LineChart from "../components/LineChart";
import DataTable from "../components/DataTable";
import InsightsCard from "../components/InsightsCard";
import ChatWidget from "../components/ChatWidget";
import ChartGrid from "../components/ChartGrid";
import Navbar from "../components/Navbar";


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
    <div className="loading-overlay">
      <div style={{ textAlign: "center" }}>
        <div className="loading-spinner" style={{ margin: "0 auto 16px" }} />
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>Building your dashboard…</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="loading-overlay">
      <p style={{ color: "#fca5a5" }}>❌ {error}</p>
    </div>
  );

  return (
    <div style={{ background: "var(--bg-primary)", minHeight: "100vh" }}>
      <Navbar />

      <div className="dashboard-page">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">datamind.</h1>
            <p className="dashboard-subtitle">
              Table: <span className="table-name-badge">{tableName}</span>
            </p>
          </div>
          <button
            id="upload-new-btn"
            className="btn-back"
            onClick={() => navigate("/")}
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

        {/* AI Chart Recommendations */}
        {data.chart_recommendations && (
          <ChartGrid
            recommendations={data.chart_recommendations}
            data={data.raw_data}
          />
        )}

        {/* AI Insights */}
        <div className="mb-8">
          <InsightsCard insights={data.insights} />
        </div>

        {/* Data Table */}
        <DataTable data={data.raw_data} />

        <ChatWidget tableName={tableName} />
      </div>
    </div>
  );
}