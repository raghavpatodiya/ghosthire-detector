import { useState, useEffect } from "react";
import "./App.css";

import LandingOptions from "./components/LandingOptions";
import JDTextInput from "./components/JDTextInput";
import JDUrlInput from "./components/JDUrlInput";
import Odometer from "./components/Odometer";

function App() {
  const [inputMode, setInputMode] = useState(null); // null | "text" | "url"
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locData, setLocData] = useState({ backend_loc: 0, frontend_loc: 0, total_loc: 0 });

  const analyzeJob = async (payload) => {
    setError("");
    setResult(null);

    // Normalize payload for backend
    const body = {};

    if (payload?.job_text) body.job_text = payload.job_text;
    if (payload?.job_url) body.job_url = payload.job_url;

    // Fallback support for { text, url }
    if (payload?.text) body.job_text = payload.text;
    if (payload?.url) body.job_url = payload.url;

    if (!body.job_text && !body.job_url) {
      setError("Please provide job description or URL");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      let data;
      try {
        data = await response.json();
      } catch {
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
    } catch {
      setLoading(false);
      setError("Backend not reachable");
    }
  };

  const fetchLoc = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/loc");
      const data = await res.json();
      if (res.ok) {
        setLocData(data);
      }
    } catch (e) {
      // silently fail — odometer is non-critical
    }
  };

  useEffect(() => {
    fetchLoc();                 // initial load
    const interval = setInterval(fetchLoc, 10000); // every 10 seconds
    return () => clearInterval(interval);
  }, []);

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
      <p style={{ opacity: 0.7, marginTop: "4px" }}>
        1 LOC at a time to improve it — currently at...
      </p>
      <Odometer value={locData.total_loc} />
      

      {inputMode !== null && (
        <button
          style={{ alignSelf: "flex-start", marginBottom: "20px" }}
          onClick={() => {
            setInputMode(null);
            setResult(null);
            setError("");
          }}
        >
          ← Change input method
        </button>
      )}

      {inputMode === null && (
        <LandingOptions onSelect={setInputMode} />
      )}

      {inputMode === "text" && (
        <JDTextInput
          onAnalyze={analyzeJob}
          loading={loading}
          error={error}
        />
      )}

      {inputMode === "url" && (
        <JDUrlInput
          onAnalyze={analyzeJob}
          loading={loading}
          error={error}
        />
      )}

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