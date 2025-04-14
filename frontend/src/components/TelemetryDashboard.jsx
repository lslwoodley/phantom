import React, { useEffect, useState } from "react";

const TelemetryDashboard = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");

    ws.onmessage = (event) => {
      const log = JSON.parse(event.data);
      setLogs((prev) => [log, ...prev.slice(0, 99)]); // Keep last 100
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Phantom Route Evaluation Logs</h2>
      <table className="table-auto w-full text-sm border">
        <thead>
          <tr className="bg-gray-100">
            <th className="px-2 py-1 border">Time</th>
            <th className="px-2 py-1 border">Source</th>
            <th className="px-2 py-1 border">Input</th>
            <th className="px-2 py-1 border">Decision</th>
            <th className="px-2 py-1 border">LLM</th>
            <th className="px-2 py-1 border">Score</th>
            <th className="px-2 py-1 border">Fallback</th>
            <th className="px-2 py-1 border">LightRAG</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, idx) => (
            <tr key={idx} className="border-b">
              <td className="px-2 py-1 border">{new Date(log.timestamp).toLocaleTimeString()}</td>
              <td className="px-2 py-1 border">{log.source}</td>
              <td className="px-2 py-1 border">{log.input}</td>
              <td className="px-2 py-1 border">{log.decision}</td>
              <td className="px-2 py-1 border">{log.llm}</td>
              <td className="px-2 py-1 border text-right">{(log.score * 100).toFixed(1)}%</td>
              <td className="px-2 py-1 border text-center">{log.fallback ? "✅" : ""}</td>
              <td className="px-2 py-1 border text-center">{log.lightRAG ? "" : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TelemetryDashboard;
