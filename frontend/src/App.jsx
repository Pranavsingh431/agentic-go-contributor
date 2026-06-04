import { useState, useRef, useEffect } from 'react';
import ResultsPanel from './ResultsPanel.jsx';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function extractDiff(raw) {
  if (!raw) return '';
  return raw
    .split('\n')
    .filter(line =>
      line.startsWith('---') ||
      line.startsWith('+++') ||
      line.startsWith('@@') ||
      line.startsWith('+') ||
      line.startsWith('-') ||
      line.startsWith(' ')
    )
    .join('\n');
}

function LogPanel({ logs }) {
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="log-panel">
      {logs.map((entry, i) => (
        <div key={i} className={`log-line log-${entry.status}`}>
          {entry.status === 'done' && '✓ '}
          {entry.status === 'running' && '⟳ '}
          {entry.status === 'error' && '✗ '}
          Step {entry.step}/6 — {entry.label}
          {entry.status === 'error' && entry.data?.error && (
            <span className="log-error-detail"> ({entry.data.error})</span>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

export default function App() {
  const [issueUrl, setIssueUrl] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleRun() {
    setLogs([]);
    setResult(null);
    setLoading(true);

    try {
      const resp = await fetch(`${API_BASE}/run/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue_url: issueUrl, repo_url: repoUrl }),
      });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop();
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          const json = JSON.parse(line.slice(5).trim());
          setLogs(prev => [...prev, json]);
          if (json.label === 'Complete' && json.status === 'done') {
            const data = json.data;
            if (data?.patch) data.patch = extractDiff(data.patch);
            setResult(data);
          }
        }
      }
    } catch (err) {
      setLogs(prev => [
        ...prev,
        { step: 0, label: `Agent error: ${err.message}`, status: 'error', data: {} },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Agentic Go Contributor</h1>

      <div className="inputs-row">
        <input
          id="issue-url"
          type="text"
          placeholder="https://github.com/spf13/cobra/issues/123"
          value={issueUrl}
          onChange={e => setIssueUrl(e.target.value)}
        />
        <input
          id="repo-url"
          type="text"
          placeholder="https://github.com/spf13/cobra"
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
        />
        <button id="run-btn" onClick={handleRun} disabled={loading || !issueUrl || !repoUrl}>
          {loading ? 'Running…' : 'Run Agent'}
        </button>
      </div>

      <LogPanel logs={logs} />
      <ResultsPanel result={result} />
      <footer style={{ color: '#666', fontSize: '12px', marginTop: '32px' }}>
        Powered by Claude via OpenRouter · spf13/cobra
      </footer>
    </div>
  );
}
