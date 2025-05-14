// frontend/src/components/TelemetryDashboard.tsx

import React, { useEffect, useState } from "react";
import styles from "./TelemetryDashboard.module.css";
import { fetchTelemetryLogs } from "../api/api"; // calls /telemetry_query
import { TelemetryEvent } from "../api/models";

const TelemetryDashboard = () => {
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [userId, setUserId] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [days, setDays] = useState<number>(7);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTelemetryLogs({ user_id: userId, status, days })
      .then((response) => setEvents(response.results))
      .catch((err) => setError("PostgreSQL unavailable or error occurred"));
  }, [userId, status, days]);

  return (
    <div className={styles.panel}>
      <h2>📊 Telemetry Logs</h2>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Filter by User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All Status</option>
          <option value="success">✅ Success</option>
          <option value="error">❌ Error</option>
        </select>
        <input
          type="number"
          min={1}
          max={30}
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        />
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.table}>
        <table>
          <thead>
            <tr>
              <th>⏱ Time</th>
              <th>👤 User</th>
              <th>📝 Query</th>
              <th>🔁 Source</th>
              <th>📦 Mode</th>
              <th>✅ Status</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id}>
                <td>{new Date(e.timestamp).toLocaleString()}</td>
                <td>{e.user_id}</td>
                <td>{e.query.slice(0, 50)}</td>
                <td>{e.source}</td>
                <td>{e.retrieval_mode}</td>
                <td>{e.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {events.length === 0 && !error && (
          <div className={styles.nodata}>No telemetry found</div>
        )}
      </div>
    </div>
  );
};

export default TelemetryDashboard;
