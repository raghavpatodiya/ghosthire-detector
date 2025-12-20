import { useState } from "react";

function App() {
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const analyzeJob = async () => {
    setError("");
    setResult(null);

    if (!jobText.trim()) {
      setError("Please enter job description");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_text: jobText })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Something went wrong");
      } else {
        setResult(data);
      }
    } catch {
      setError("Backend not reachable");
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>GhostHire Detector</h2>

      <textarea
        rows="12"
        cols="80"
        placeholder="Paste job description here..."
        value={jobText}
        onChange={(e) => setJobText(e.target.value)}
      />

      <br /><br />
      <button onClick={analyzeJob}>Analyze</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div>
          <h3>Result</h3>
          <p><b>Risk Score:</b> {result.rule_score}</p>
          <ul>
            {result.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;