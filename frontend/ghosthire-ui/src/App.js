import { useState } from "react";
import "./App.css";

function App() {
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const analyzeJob = async () => {
    setError("");
    setResult(null);

    if (!jobText.trim()) {
      setError("Please enter job description");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_text: jobText })
      });

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        setLoading(false);
        setError("Invalid response from server");
        return;
      }

      setLoading(false);

      if (!response.ok) {
        setError(data.error || "Something went wrong");
      } else {
        setResult(data);
      }
    } catch (error) {
      setLoading(false);
      setError("Backend not reachable");
    }
  };

  const skills = result?.insights?.skills?.skills_found || [];

  const riskLabel =
    result?.rule_score > 0.7
      ? "HIGH RISK"
      : result?.rule_score > 0.4
      ? "MEDIUM RISK"
      : "LOW RISK";

  const riskClass =
    result?.rule_score > 0.7
      ? "risk-high"
      : result?.rule_score > 0.4
      ? "risk-medium"
      : "risk-low";

  return (
    <div className="app">
      <h2>GhostHire Detector</h2>

      <textarea
        rows="12"
        placeholder="Paste job description here..."
        value={jobText}
        onChange={(e) => setJobText(e.target.value)}
      />

      <p className={`counter ${jobText.length < 50 ? "warn" : ""}`}>
        {jobText.length} characters
        {jobText.length < 50 && " (too short to analyze properly)"}
      </p>

      <button onClick={analyzeJob} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <span className={`status-chip ${riskClass}`}>
            {riskLabel}
          </span>

          <ul>
            {(result.reasons || []).map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>

          {skills.length > 0 && (
            <>
              <h4>Skills Detected</h4>
              <div className="skills">
                {skills.map((skill, i) => (
                  <span key={i} className="skill-chip">
                    {skill}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;