from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_html():
    raw_data = request.get_data(as_text=True)
    if not raw_data:
        return jsonify({"error": "Request body is empty. Raw HTML content is expected."}), 400

    # Handles both raw HTML and the nested JSON structure { "html": "..." }
    html_input = raw_data
    try:
        data_json = json.loads(raw_data)
        if 'html' in data_json and isinstance(data_json['html'], str):
            html_input = data_json['html']
    except json.JSONDecodeError:
        pass # It's not JSON, so we assume it's raw HTML

    soup = BeautifulSoup(html_input, 'html.parser')
    sections = []

    all_h2s = soup.find_all('h2')

    for h2 in all_h2s:
        title_text = h2.get_text(strip=True)
        if not title_text:
            continue

        title_html = str(h2)
        
        content_parts = []
        for sibling in h2.find_next_siblings():
            if sibling.name == 'h2':
                break
            content_parts.append(str(sibling))
        
        content_html = "".join(content_parts).strip()

        if content_html:
            sections.append({
                "title_html": title_html,
                "content_html": content_html
            })
            
    return jsonify(sections)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
