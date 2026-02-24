export default function MetricCard({ label, value, avg }) {
  return (
    <div className="bg-gray-800 rounded-2xl p-5 border border-gray-700">
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-white text-2xl font-bold">
        {Number(value).toLocaleString()}
      </p>
      <p className="text-gray-500 text-xs mt-1">avg: {Number(avg).toLocaleString()}</p>
    </div>
  );
}