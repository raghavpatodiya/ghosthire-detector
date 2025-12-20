from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.fraud_rules import run_all_rules

app = Flask(__name__)
CORS(app)  # allow React frontend calls

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    job_text = data.get("job_text", "").strip()

    if not job_text:
        return jsonify({
            "error": "job_text is required"
        }), 400

    result = run_all_rules(job_text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)