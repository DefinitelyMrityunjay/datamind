import {
  BarChart, Bar,
  LineChart, Line,
  ScatterChart, Scatter,
  PieChart, Pie, Cell,
  ResponsiveContainer,
  XAxis, YAxis, CartesianGrid,
  Tooltip, Legend
} from "recharts";

// Colour palette for pie slices and bars
const COLORS = [
  "#6366f1", "#22c55e", "#f59e0b", "#ef4444",
  "#3b82f6", "#ec4899", "#14b8a6", "#f97316"
];

// ── Individual chart renderers ──────────────────────

function BarChartCard({ rec, data }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey={rec.x}
          tick={{ fontSize: 11 }}
          angle={-35}
          textAnchor="end"
          interval={0}
        />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey={rec.y} fill={COLORS[0]} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function LineChartCard({ rec, data }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey={rec.x}
          tick={{ fontSize: 11 }}
          angle={-35}
          textAnchor="end"
          interval={Math.floor(data.length / 8)}
        />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey={rec.y}
          stroke={COLORS[0]}
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function ScatterChartCard({ rec, data }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <ScatterChart margin={{ top: 5, right: 20, left: 0, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey={rec.x} name={rec.x} tick={{ fontSize: 11 }} />
        <YAxis dataKey={rec.y} name={rec.y} tick={{ fontSize: 11 }} />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        <Scatter data={data} fill={COLORS[2]} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

function PieChartCard({ rec, data }) {
  // For pie charts, count occurrences of each category value
  const counts = data.reduce((acc, row) => {
    const key = String(row[rec.x] ?? "Unknown");
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={pieData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={90}
          label={({ name, percent }) =>
            `${name} (${(percent * 100).toFixed(0)}%)`
          }
          labelLine={false}
        >
          {pieData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

function HistogramCard({ rec, data }) {
  // Build buckets from raw numeric values
  const values = data
    .map((row) => parseFloat(row[rec.x]))
    .filter((v) => !isNaN(v));

  if (values.length === 0) return <p className="text-sm text-gray-400">No data</p>;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const bucketCount = Math.min(10, Math.ceil(Math.sqrt(values.length)));
  const bucketSize = (max - min) / bucketCount || 1;

  const buckets = Array.from({ length: bucketCount }, (_, i) => ({
    range: `${(min + i * bucketSize).toFixed(1)}`,
    count: 0,
  }));

  values.forEach((v) => {
    const i = Math.min(
      Math.floor((v - min) / bucketSize),
      bucketCount - 1
    );
    buckets[i].count += 1;
  });

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={buckets} margin={{ top: 5, right: 20, left: 0, bottom: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="range"
          tick={{ fontSize: 10 }}
          angle={-30}
          textAnchor="end"
        />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="count" fill={COLORS[4]} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function HeatmapCard({ data }) {
  // Simple correlation table — Recharts doesn't have a native heatmap
  // so we render a colour-coded grid manually
  const numericKeys = Object.keys(data[0] || {}).filter(
    (k) => !isNaN(parseFloat(data[0][k]))
  );

  if (numericKeys.length < 2) {
    return <p className="text-sm text-gray-400">Not enough numeric columns.</p>;
  }

  // Pearson correlation between two arrays
  const corr = (a, b) => {
    const n = a.length;
    const meanA = a.reduce((s, v) => s + v, 0) / n;
    const meanB = b.reduce((s, v) => s + v, 0) / n;
    const num = a.reduce((s, v, i) => s + (v - meanA) * (b[i] - meanB), 0);
    const den = Math.sqrt(
      a.reduce((s, v) => s + (v - meanA) ** 2, 0) *
        b.reduce((s, v) => s + (v - meanB) ** 2, 0)
    );
    return den === 0 ? 0 : num / den;
  };

  const getColor = (v) => {
    if (v > 0.7) return "bg-green-200 text-green-900";
    if (v > 0.3) return "bg-green-100 text-green-800";
    if (v < -0.7) return "bg-red-200 text-red-900";
    if (v < -0.3) return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-600";
  };

  const cols = numericKeys.slice(0, 6); // cap at 6 to avoid overflow

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full border-collapse">
        <thead>
          <tr>
            <th className="p-1" />
            {cols.map((c) => (
              <th key={c} className="p-1 text-gray-500 font-medium truncate max-w-[60px]">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cols.map((rowCol) => {
            const rowVals = data.map((r) => parseFloat(r[rowCol])).filter((v) => !isNaN(v));
            return (
              <tr key={rowCol}>
                <td className="p-1 text-gray-500 font-medium truncate max-w-[60px]">
                  {rowCol}
                </td>
                {cols.map((colCol) => {
                  const colVals = data.map((r) => parseFloat(r[colCol])).filter((v) => !isNaN(v));
                  const len = Math.min(rowVals.length, colVals.length);
                  const r = corr(rowVals.slice(0, len), colVals.slice(0, len));
                  return (
                    <td
                      key={colCol}
                      className={`p-1 text-center rounded ${getColor(r)}`}
                    >
                      {r.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── Main ChartGrid component ────────────────────────

export default function ChartGrid({ recommendations = [], data = [] }) {
  if (!recommendations.length) {
    return (
      <p className="text-sm text-gray-400 text-center py-8">
        No chart recommendations available.
      </p>
    );
  }

  if (!data.length) {
    return (
      <p className="text-sm text-gray-400 text-center py-8">
        No data to display charts for.
      </p>
    );
  }

  const renderChart = (rec) => {
    switch (rec.chart_type) {
      case "bar":       return <BarChartCard rec={rec} data={data} />;
      case "line":      return <LineChartCard rec={rec} data={data} />;
      case "scatter":   return <ScatterChartCard rec={rec} data={data} />;
      case "pie":       return <PieChartCard rec={rec} data={data} />;
      case "histogram": return <HistogramCard rec={rec} data={data} />;
      case "heatmap":   return <HeatmapCard data={data} />;
      default:          return <p className="text-sm text-gray-400">Unsupported chart type.</p>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold text-gray-700">
          AI-Selected Charts
        </h2>
        <span className="text-xs bg-indigo-50 text-indigo-600 border border-indigo-100 px-2 py-0.5 rounded-full">
          {recommendations.length} charts
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec, i) => (
          <div
            key={i}
            className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm"
          >
            {/* Card header */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-sm font-medium text-gray-800 leading-tight">
                  {rec.title}
                </h3>
                <span className="text-[10px] font-mono bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full shrink-0 ml-2">
                  {rec.chart_type}
                </span>
              </div>
              <p className="text-xs text-gray-400 leading-snug">{rec.reason}</p>
            </div>

            {/* Chart */}
            {renderChart(rec)}
          </div>
        ))}
      </div>
    </div>
  );
}