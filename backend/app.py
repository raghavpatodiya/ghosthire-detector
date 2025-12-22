from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.analysis_engine import run_all_rules

app = Flask(__name__)
CORS(app)  # allow React frontend calls


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    job_text = (data.get("job_text") or "").strip()
    job_url = (data.get("job_url") or "").strip()

    # Case 1: job text provided (current flow)
    if job_text:
        result = run_all_rules(job_text)
        return jsonify(result)

    # Case 2: job URL provided (future flow)
    if job_url:
        return jsonify({
            "error": "Job URL analysis is not supported yet"
        }), 400

    # Case 3: nothing provided
    return jsonify({
        "error": "Either job_text or job_url is required"
    }), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)