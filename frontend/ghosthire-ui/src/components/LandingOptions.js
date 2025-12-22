function LandingOptions({ onSelect }) {
    return (
      <div style={{ textAlign: "center", marginTop: "60px" }}>
        <h3>How would you like to analyze the job?</h3>
  
        <div style={{ marginTop: "30px" }}>
          <button onClick={() => onSelect("url")}>
            Paste Job URL
          </button>
        </div>
  
        <div style={{ marginTop: "16px" }}>
          <button onClick={() => onSelect("text")}>
            Continue with Job Description
          </button>
        </div>
      </div>
    );
  }
  
  export default LandingOptions;