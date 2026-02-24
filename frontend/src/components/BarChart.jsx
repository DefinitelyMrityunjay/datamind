import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function BarChart({ data, xLabel, yLabel }) {
  const chartData = data.labels.map((label, i) => ({
    name: label,
    value: data.values[i],
  }));

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h2 className="text-white text-lg font-semibold mb-4">
        📊 {yLabel} by {xLabel}
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <ReBarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
          <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1F2937", border: "none", borderRadius: "8px" }}
            labelStyle={{ color: "#F9FAFB" }}
          />
          <Bar dataKey="value" fill="#6366F1" radius={[4, 4, 0, 0]} />
        </ReBarChart>
      </ResponsiveContainer>
    </div>
  );
}