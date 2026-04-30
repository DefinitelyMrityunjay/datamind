import { useNavigate } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const barData = [
  { name: "Jan", value: 400 },
  { name: "Feb", value: 300 },
  { name: "Mar", value: 600 },
  { name: "Apr", value: 800 },
  { name: "May", value: 500 },
];

const pieData = [
  { name: "North", value: 400 },
  { name: "South", value: 300 },
  { name: "East", value: 200 },
  { name: "West", value: 100 },
];

const COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444"];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white flex flex-col">

      {/* ── Navbar ── */}
      <nav className="flex items-center justify-between px-10 py-5">
        <span className="text-xl font-bold tracking-tight">datamind.</span>
        <div className="flex items-center gap-4">
          <button className="text-gray-300 hover:text-white text-sm transition">
            Sign up
          </button>
          <button className="bg-[#c4b5fd] hover:bg-[#a78bfa] text-gray-900 font-medium text-sm px-5 py-2 rounded-full transition">
            Log in
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <div className="flex flex-col items-center justify-center text-center px-4 pt-16 pb-10 w-full">
        <h1 className="text-6xl font-extrabold tracking-tight mb-5">
          datamind.
        </h1>
        <p className="text-gray-400 text-lg max-w-xl mb-10">
          Upload any data file and get instant AI-powered insights, charts, and
          answers — no analyst needed.
        </p>

        {/* CTA Buttons */}
        <div className="flex gap-4 mb-16">
          <button
            onClick={() => navigate("/upload")}
            className="bg-[#c4b5fd] hover:bg-[#a78bfa] text-gray-900 font-semibold px-8 py-3 rounded-full transition text-sm"
          >
            Get started
          </button>
          <a
            href="https://github.com/DefinitelyMrityunjay/datamind/tree/main#readme"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-gray-600 hover:border-gray-400 text-gray-300 hover:text-white px-8 py-3 rounded-full transition text-sm"
          >
            See how it works
          </a>
        </div>

        {/* ── Dashboard Mockup ── */}
        <div className="w-full max-w-3xl bg-[#242424] rounded-3xl border border-gray-700/50 p-6 shadow-2xl">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="ml-3 text-gray-500 text-xs font-mono">
              datamind.app/dashboard
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              { label: "Total Revenue", value: "$24,500", delta: "+12%" },
              { label: "Total Sales", value: "1,025", delta: "+8%" },
              { label: "Avg Order", value: "$238", delta: "+3%" },
            ].map((m) => (
              <div key={m.label} className="bg-[#2e2e2e] rounded-xl p-4 border border-gray-700/50">
                <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                <p className="text-white text-xl font-bold">{m.value}</p>
                <p className="text-green-400 text-xs mt-1">{m.delta}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#2e2e2e] rounded-xl p-4 border border-gray-700/50">
              <p className="text-gray-400 text-xs mb-3">Monthly Revenue</p>
              <ResponsiveContainer width="100%" height={140}>
                <BarChart data={barData}>
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} />
                  <YAxis hide />
                  <Tooltip contentStyle={{ backgroundColor: "#1F2937", border: "none", borderRadius: "8px", fontSize: "12px" }} />
                  <Bar dataKey="value" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-[#2e2e2e] rounded-xl p-4 border border-gray-700/50">
              <p className="text-gray-400 text-xs mb-3">Sales by Region</p>
              <div className="flex items-center justify-between">
                <ResponsiveContainer width="60%" height={140}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value" strokeWidth={0}>
                      {pieData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-col gap-2">
                  {pieData.map((entry, i) => (
                    <div key={entry.name} className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                      <span className="text-gray-400 text-xs">{entry.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl px-4 py-3 flex items-start gap-3">
            <span className="text-lg">🤖</span>
            <p className="text-indigo-300 text-xs leading-relaxed">
              <strong>AI Insight:</strong> April had the highest revenue at $800,
              outperforming the average by 37%. North region leads all segments at 40% share.
            </p>
          </div>
        </div>
      </div>

      {/* ── Features Section ── */}
      <div className="w-full px-16 mt-24 mb-24">
        <div className="max-w-6xl mx-auto grid grid-cols-2 gap-16 items-center">

          {/* Left — Feature list */}
          <div className="flex flex-col gap-10">
            {[
              {
                icon: "📂",
                color: "bg-blue-500/20",
                title: "Any format, instantly",
                desc: "Upload CSV, Excel, PDF, or images. DataMind reads and understands all of them automatically."
              },
              {
                icon: "🗄️",
                color: "bg-purple-500/20",
                title: "Live database, zero setup",
                desc: "Every upload is stored in a real PostgreSQL database. Query your data anytime, no configuration needed."
              },
              {
                icon: "🤖",
                color: "bg-green-500/20",
                title: "AI that thinks like an analyst",
                desc: "Get instant written insights, trends, and business recommendations powered by AI — in seconds."
              },
            ].map((f) => (
              <div key={f.title} className="flex items-start gap-5">
                <div className={`${f.color} rounded-2xl p-4 text-2xl shrink-0`}>
                  {f.icon}
                </div>
                <div>
                  <h3 className="text-white font-semibold text-lg mb-1">{f.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Right — Chat mockup card */}
          <div className="bg-[#b8f0e0] rounded-3xl p-8 flex items-center justify-center min-h-[500px]">
            <div className="bg-[#1e1e1e] rounded-2xl p-6 w-full shadow-2xl">
              <div className="flex items-center justify-between mb-5">
                <span className="text-white font-semibold text-sm">DataMind</span>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-500" />
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-500" />
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-500" />
                </div>
              </div>

              <p className="text-white font-bold text-lg mb-5">Ask your data anything ✦</p>

              <div className="flex flex-col gap-3 mb-5">
                <div className="bg-[#2e2e2e] rounded-xl px-4 py-3 text-gray-300 text-xs">
                  Show me top 5 products by revenue
                </div>
                <div className="bg-indigo-600/30 border border-indigo-500/30 rounded-xl px-4 py-3 text-indigo-200 text-xs">
                  SELECT product_name, SUM(revenue) FROM data ORDER BY 2 DESC LIMIT 5
                </div>
                <div className="bg-[#2e2e2e] rounded-xl px-4 py-3 text-gray-300 text-xs">
                  Which region has the lowest sales?
                </div>
                <div className="bg-indigo-600/30 border border-indigo-500/30 rounded-xl px-4 py-3 text-indigo-200 text-xs">
                  SELECT region, SUM(sales) FROM data GROUP BY region ORDER BY 2 ASC LIMIT 1
                </div>
              </div>

              <div className="flex items-center gap-2 bg-[#2e2e2e] rounded-xl px-4 py-3">
                <span className="text-gray-500 text-xs flex-1">Ask a question in plain English...</span>
                <div className="bg-[#c4b5fd] rounded-lg p-1.5">
                  <span className="text-gray-900 text-xs font-bold">↑</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}