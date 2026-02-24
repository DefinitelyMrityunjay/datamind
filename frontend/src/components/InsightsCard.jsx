export default function InsightsCard({ insights }) {
  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h2 className="text-white text-lg font-semibold mb-4">🤖 AI Insights</h2>
      <div className="text-gray-300 text-sm whitespace-pre-line leading-relaxed">
        {insights}
      </div>
    </div>
  );
}