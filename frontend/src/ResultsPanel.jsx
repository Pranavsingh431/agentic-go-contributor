function CheckBlock({ label, check }) {
  const ok = check?.returncode === 0;
  return (
    <div>
      <strong>{label}</strong>
      <pre className={ok ? 'check-ok' : 'check-fail'}>
        {check?.stdout || '(no output)'}
      </pre>
    </div>
  );
}

export default function ResultsPanel({ result }) {
  if (!result) return null;
  return (
    <div className="results-panel">
      <h2>Results</h2>
      <section>
        <h3>PR Title</h3>
        <p>{result.pr_title || '—'}</p>
      </section>
      <section>
        <h3>PR Body</h3>
        <pre>{result.pr_body || '—'}</pre>
      </section>
      <section>
        <h3>Diff</h3>
        <pre className="diff-block">{result.patch || '(no diff generated)'}</pre>
      </section>
      <section>
        <h3>Go Checks</h3>
        <CheckBlock label="go vet" check={result.checks?.vet} />
        <CheckBlock label="go test" check={result.checks?.test} />
      </section>
    </div>
  );
}
