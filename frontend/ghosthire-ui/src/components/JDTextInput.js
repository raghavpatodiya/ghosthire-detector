import { useState } from "react";

function JDTextInput({ onAnalyze, loading, error }) {
  const [jobText, setJobText] = useState("");

  const handleAnalyze = () => {
    if (!jobText.trim()) return;
    onAnalyze({ job_text: jobText });
  };

  return (
    <>
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

      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="error">{error}</p>}
    </>
  );
}

export default JDTextInput;