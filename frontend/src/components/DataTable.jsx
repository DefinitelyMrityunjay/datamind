export default function DataTable({ data }) {
  if (!data || data.length === 0) return null;
  const headers = Object.keys(data[0]);

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 overflow-auto">
      <h2 className="text-white text-lg font-semibold mb-4">🔍 Data Preview</h2>
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="border-b border-gray-700">
            {headers.map((h) => (
              <th key={h} className="text-gray-400 pb-3 pr-6 font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 10).map((row, i) => (
            <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-700/30">
              {headers.map((h) => (
                <td key={h} className="text-gray-300 py-3 pr-6">
                  {String(row[h])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}