import { useState } from "react";

function JDUrlInput({ onAnalyze, loading, error }) {
  const [jobUrl, setJobUrl] = useState("");

  const handleAnalyze = () => {
    if (!jobUrl.trim()) return;
    onAnalyze({ job_url: jobUrl });
  };

  return (
    <>
      <input
        type="url"
        placeholder="Paste job posting URL here..."
        value={jobUrl}
        onChange={(e) => setJobUrl(e.target.value)}
        style={{
          width: "100%",
          maxWidth: "900px",
          padding: "12px 16px",
          borderRadius: "10px",
          border: "1px solid #1e293b",
          background: "#020617",
          color: "#e5e7eb",
          outline: "none",
        }}
      />

      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="error">{error}</p>}
    </>
  );
}

export default JDUrlInput;