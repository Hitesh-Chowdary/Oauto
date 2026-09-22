from flask import Flask, request, jsonify, render_template_string
import os
from extractor_hybrid import extract_hybrid, format_hybrid_output

app = Flask(__name__)

# Load the single-file mobile HTML UI
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")

@app.route("/")
def home():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/api/extract", methods=["POST"])
def api_extract():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    
    main_doc, patches, kb_subdocs, mos_counts = extract_hybrid(text)
    full_report = format_hybrid_output(main_doc, patches, kb_subdocs, mos_counts)
    
    mos_formatted_list = [f"{doc}({count})" for doc, count in mos_counts.items()]
    
    return jsonify({
        "mainDoc": main_doc,
        "patches": patches,
        "patchesFormatted": ", ".join(patches) if patches else "None found",
        "patchesCount": len(patches),
        "kbSubdocs": kb_subdocs,
        "kbFormatted": "  ".join(kb_subdocs) if kb_subdocs else "None found",
        "kbCount": len(kb_subdocs),
        "mosSubdocsCounts": mos_counts,
        "mosFormatted": ", ".join(mos_formatted_list) if mos_formatted_list else "None found",
        "mosUniqueCount": len(mos_counts),
        "mosTotalCount": sum(mos_counts.values()),
        "fullReport": full_report
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
