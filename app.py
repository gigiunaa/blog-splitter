from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_html():
    # ----- Change starts here -----
    # Get the request body directly as text.
    # request.get_data(as_text=True) reads the raw data and converts it into a string.
    html_input = request.get_data(as_text=True)

    # Check if the request body is empty.
    if not html_input:
        return jsonify({"error": "Request body is empty. Raw HTML content is expected."}), 400
    # ----- Change ends here -----

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

# This section for Gunicorn and local testing remains unchanged.
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
