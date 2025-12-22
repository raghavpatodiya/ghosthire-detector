from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.analysis_engine import run_all_rules
from analyzer.ingestion.url_fetcher import fetch_url_content
from analyzer.ingestion.jd_extractor import extract_job_description
from analyzer.ingestion.normalizer import normalize_job_description

app = Flask(__name__)
CORS(app)  # allow React frontend calls


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    job_text = (data.get("job_text") or "").strip()
    job_url = (data.get("job_url") or "").strip()

    # Case 1: job text provided
    if job_text:
        return jsonify(run_all_rules(job_text))

    # Case 2: job URL provided
    if job_url:
        try:
            html = fetch_url_content(job_url)
            extracted_text = extract_job_description(html)
            normalized_text = normalize_job_description(extracted_text)

            if not normalized_text:
                return jsonify({
                    "error": "Unable to extract job description from the provided URL"
                }), 400

            return jsonify(run_all_rules(normalized_text))

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 400

    # Case 3: nothing provided
    return jsonify({
        "error": "Either job_text or job_url is required"
    }), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)