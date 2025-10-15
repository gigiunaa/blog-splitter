from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_html():
    # ვიღებთ JSON მონაცემებს მოთხოვნიდან
    data = request.get_json()
    if not data or 'html_content' not in data:
        return jsonify({"error": "Missing 'html_content' in request body"}), 400

    html_input = data['html_content']
    
    soup = BeautifulSoup(html_input, 'html.parser')
    sections = []

    # ვპოულობთ ყველა h2 თეგს
    all_h2s = soup.find_all('h2')

    for h2 in all_h2s:
        # ვამოწმებთ, შეიცავს თუ არა h2 რეალურ ტექსტს
        title_text = h2.get_text(strip=True)
        if not title_text:
            continue

        title_html = str(h2)
        
        content_parts = []
        # ვიღებთ ყველა ელემენტს ამ h2-ის შემდეგ, მომდევნო h2-მდე
        for sibling in h2.find_next_siblings():
            if sibling.name == 'h2':
                break
            content_parts.append(str(sibling))
        
        content_html = "".join(content_parts).strip()

        # ვამატებთ მხოლოდ იმ შემთხვევაში, თუ კონტენტიც არსებობს
        if content_html:
            sections.append({
                "title_html": title_html,
                "content_html": content_html
            })
            
    return jsonify(sections)

if __name__ == "__main__":
    # Render.com იყენებს Gunicorn-ს და ეს ნაწილი ლოკალური ტესტირებისთვისაა
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
