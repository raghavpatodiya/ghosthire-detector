from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.analysis_engine import run_all_rules
from analyzer.ingestion.url_fetcher import fetch_url_content
from analyzer.ingestion.jd_extractor import extract_job_description
from analyzer.ingestion.normalizer import normalize_job_description
from analyzer.parsing.jd_parser import parse_jd
import os
from utils.loc_counter import count_loc

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
    supports_credentials=True,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"]
)

# ===== Debug raw JD dump config =====
DEBUG_DUMP_RAW_JD = True
DEBUG_RAW_JD_PATH = "debug/raw_jd.txt"
# ===================================


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}

    job_text = (data.get("job_text") or "").strip()
    job_url = (data.get("job_url") or "").strip()

    # -------- Case 1: JD pasted directly --------
    if job_text:
        raw_jd_text = job_text

        if DEBUG_DUMP_RAW_JD:
            try:
                with open(DEBUG_RAW_JD_PATH, "w", encoding="utf-8") as f:
                    f.write(raw_jd_text)
            except Exception:
                pass

        jd_context = parse_jd(raw_jd_text)

        if jd_context is None:
            return jsonify({
                "error": "Failed to parse job description"
            }), 400

        return jsonify(run_all_rules(jd_context))

    # -------- Case 2: JD fetched via URL --------
    if job_url:
        try:
            html = fetch_url_content(job_url)
            extracted_text = extract_job_description(html)
            normalized_text = normalize_job_description(extracted_text)

            if not normalized_text:
                return jsonify({
                    "error": "Unable to extract job description from the provided URL"
                }), 400

            raw_jd_text = normalized_text

            if DEBUG_DUMP_RAW_JD:
                try:
                    with open(DEBUG_RAW_JD_PATH, "w", encoding="utf-8") as f:
                        f.write(raw_jd_text)
                except Exception:
                    pass

            jd_context = parse_jd(raw_jd_text)

            if jd_context is None:
                return jsonify({
                    "error": "Failed to parse extracted job description"
                }), 400

            return jsonify(run_all_rules(jd_context))

        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 400

    # -------- Case 3: Invalid input --------

    return jsonify({
        "error": "Either job_text or job_url is required"
    }), 400


@app.route("/loc", methods=["GET"])
def loc_count():
    try:
        # Use __file__ to get paths relative to app.py location, not cwd
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        
        backend_path = backend_dir
        frontend_path = os.path.join(project_root, "frontend", "ghosthire-ui")

        backend_loc = count_loc(backend_path)
        frontend_loc = count_loc(frontend_path)

        return jsonify({
            "backend_loc": backend_loc,
            "frontend_loc": frontend_loc,
            "total_loc": backend_loc + frontend_loc
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)