"use client";

import { FormEvent, useEffect, useState } from "react";
import styles from "./page.module.css";

type StatusResponse = {
  status: string;
  music_agent_ready?: boolean;
  spotify_connected?: boolean;
  spotify_auth_mode?: string | null;
  playback_backend?: string;
  current_track?: {
    status?: string;
    name?: string;
    artist?: string;
  };
};

type CommandResponse = {
  status: string;
  message: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [command, setCommand] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/status`);
      if (!response.ok) {
        throw new Error(`Status API failed with ${response.status}`);
      }
      const payload: StatusResponse = await response.json();
      setStatus(payload);
      setError("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Status API failed";
      setError(message);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const runCommand = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!command.trim()) {
      setError("Please enter a command.");
      return;
    }

    setLoading(true);
    setError("");
    setResult("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/command`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command.trim() }),
      });

      const payload = (await response.json()) as CommandResponse | { detail?: string };
      if (!response.ok) {
        const message = "detail" in payload ? payload.detail : "Command failed";
        throw new Error(message);
      }

      setResult((payload as CommandResponse).message);
      await fetchStatus();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Command failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.header}>
          <h1>Intelligent Music Agent</h1>
          <p>Web-first UI powered by Next.js + FastAPI + Spotify API.</p>
          <p className={styles.meta}>Backend: {API_BASE_URL}</p>
        </header>

        <section className={styles.card}>
          <div className={styles.statusHeader}>
            <h2>Backend Status</h2>
            <button type="button" onClick={fetchStatus} className={styles.secondaryButton}>
              Refresh
            </button>
          </div>
          <pre className={styles.pre}>
            {JSON.stringify(status ?? { status: "loading" }, null, 2)}
          </pre>
        </section>

        <section className={styles.card}>
          <h2>Run Command</h2>
          <form className={styles.form} onSubmit={runCommand}>
            <input
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              placeholder="e.g. what's playing"
              className={styles.input}
            />
            <button type="submit" className={styles.primaryButton} disabled={loading}>
              {loading ? "Running..." : "Send"}
            </button>
          </form>
          <p className={styles.examples}>
            Try: <code>what&apos;s playing</code>, <code>play high hopes pink floyd</code>,{" "}
            <code>sync</code>, <code>lyrics</code>
          </p>
        </section>

        {(result || error) && (
          <section className={styles.card}>
            <h2>Response</h2>
            {error ? <p className={styles.error}>{error}</p> : <pre className={styles.pre}>{result}</pre>}
          </section>
        )}
      </main>
    </div>
  );
}
