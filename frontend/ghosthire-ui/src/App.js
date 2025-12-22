import { useState } from "react";
import "./App.css";

import LandingOptions from "./components/LandingOptions";
import JDTextInput from "./components/JDTextInput";
import JDUrlInput from "./components/JDUrlInput";

function App() {
  const [inputMode, setInputMode] = useState(null); // null | "text" | "url"
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const analyzeJob = async (payload) => {
    setError("");
    setResult(null);

    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
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