import { useEffect, useState } from "react";

interface Health {
  status: string;
  telefony: string;
  db: string;
  redis: string;
}

type ConnectionState = "ok" | "lost" | "idle";

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [conn, setConn] = useState<ConnectionState>("idle");
  const [log, setLog] = useState<string[]>([]);

  // проверяем живость бэкенда
  useEffect(() => {
    fetch("/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  // подписка на SSE dialer'а
  useEffect(() => {
    const es = new EventSource("/dialer/events?ext=101");
    es.onopen = () => setConn("ok");
    es.onerror = () => setConn("lost");
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      setLog((prev) => [JSON.stringify(ev), ...prev].slice(0, 20));
    };
    return () => es.close();
  }, []);

  const start = () => fetch("/dialer/1/start?ext=101", { method: "POST" });

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24 }}>
      <h1 style={{ fontSize: 20 }}>CRM-CC · каркас экрана оператора</h1>

      <p>
        Бэкенд:{" "}
        {health
          ? `${health.status} (db: ${health.db}, redis: ${health.redis}, telefony: ${health.telefony})`
          : "недоступен"}
      </p>
      <p>
        SSE:{" "}
        {conn === "ok" ? "● подключено" : conn === "lost" ? "● потеряно" : "—"}
      </p>

      <button onClick={start}>Старт обзвона (мок)</button>

      <h3 style={{ marginBottom: 4 }}>События dialer'а:</h3>
      <pre style={{ fontSize: 12, background: "#f4f4f5", padding: 12, borderRadius: 8 }}>
        {log.length ? log.join("\n") : "— ожидание событий —"}
      </pre>
    </div>
  );
}
