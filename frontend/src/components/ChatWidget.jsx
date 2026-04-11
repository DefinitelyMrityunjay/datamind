import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function ChatWidget({ tableName }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! Ask me anything about your data. For example: 'Show me the top 5 rows' or 'What is the average value of each column?'",
      sql: null,
      data: null,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", text: input, sql: null, data: null };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/chat", {
        question: input,
        table_name: tableName,
      });

      const result = response.data;

      if (result.success) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `Found ${result.data.row_count} result(s).`,
            sql: result.sql,
            data: result.data,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `Sorry, I couldn't answer that. Error: ${result.error}`,
            sql: result.sql,
            data: null,
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Network error — make sure the backend is running.",
          sql: null,
          data: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-96 border border-gray-200 rounded-2xl bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100 bg-gray-50">
        <h2 className="text-sm font-semibold text-gray-700">Ask your data</h2>
        <p className="text-xs text-gray-400 mt-0.5">
          Table: <span className="font-mono">{tableName || "not selected"}</span>
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] space-y-2`}>
              {/* Bubble */}
              <div
                className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-tr-sm"
                    : "bg-gray-100 text-gray-800 rounded-tl-sm"
                }`}
              >
                {msg.text}
              </div>

              {/* SQL block */}
              {msg.sql && (
                <div className="bg-gray-900 text-green-400 text-xs font-mono rounded-xl px-4 py-3 overflow-x-auto">
                  <p className="text-gray-500 text-[10px] mb-1 uppercase tracking-wider">Generated SQL</p>
                  <pre className="whitespace-pre-wrap">{msg.sql}</pre>
                </div>
              )}

              {/* Results table */}
              {msg.data && msg.data.rows.length > 0 && (
                <div className="overflow-x-auto rounded-xl border border-gray-200">
                  <table className="text-xs w-full">
                    <thead className="bg-gray-50 text-gray-500 uppercase tracking-wide">
                      <tr>
                        {msg.data.columns.map((col) => (
                          <th key={col} className="px-3 py-2 text-left font-medium border-b border-gray-200">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {msg.data.rows.map((row, ri) => (
                        <tr key={ri} className="hover:bg-gray-50">
                          {msg.data.columns.map((col) => (
                            <td key={col} className="px-3 py-2 text-gray-700 max-w-50 truncate">
                              {row[col] === null ? (
                                <span className="text-gray-300 italic">null</span>
                              ) : String(row[col])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="text-[10px] text-gray-400 px-3 py-1.5 border-t border-gray-100">
                    {msg.data.row_count} row(s) returned
                  </p>
                </div>
              )}

              {msg.data && msg.data.rows.length === 0 && (
                <p className="text-xs text-gray-400 px-1">No rows matched your query.</p>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 flex items-end gap-2">
        <textarea
          className="flex-1 resize-none rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-10 max-h-30"
          placeholder="Ask a question about your data..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={!tableName || loading}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || loading || !tableName}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-xl px-4 py-2 text-sm font-medium transition-colors shrink-0"
        >
          Send
        </button>
      </div>
    </div>
  );
}