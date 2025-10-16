from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from collections import Counter

app = Flask(__name__)

def analyze_global_styles(soup):
    """
    Analyzes the entire document and creates a "style dictionary"
    for the most frequently used classes.
    """
    styles = {}
    
    # List of tags to analyze for styling
    tags_to_analyze = ['p', 'h3', 'li']
    
    for tag_name in tags_to_analyze:
        class_counter = Counter()
        span_class_counter = Counter()
        
        for tag in soup.find_all(tag_name):
            # Store the classes of the main tag
            if tag.has_attr('class'):
                class_counter[" ".join(tag['class'])] += 1
            
            # Store the classes of the inner <span> tag
            span = tag.find('span')
            if span and span.has_attr('class'):
                span_class_counter[" ".join(span['class'])] += 1
                
        # Select the most frequently used classes
        if class_counter:
            styles[tag_name] = {
                "tag_class": class_counter.most_common(1)[0][0],
                "span_class": span_class_counter.most_common(1)[0][0] if span_class_counter else ""
            }
            
    return styles

@app.route('/prepare', methods=['POST'])
def prepare_for_ai():
    html_input = request.get_data(as_text=True)
    if not html_input:
        return jsonify({"error": "Request body is empty."}), 400

    soup = BeautifulSoup(html_input, 'html.parser')
    head_content = str(soup.find('head')) if soup.find('head') else ""
    
    # 1. Create the global style dictionary once
    style_dictionary = analyze_global_styles(soup)
    
    processed_sections = []
    all_h2s = soup.find_all('h2')

    for h2 in all_h2s:
        title_text = h2.get_text(strip=True)
        if not title_text:
            continue

        content_tags = [sibling for sibling in h2.find_next_siblings() if sibling.name != 'h2']
        if not content_tags:
            continue
        
        temp_div = soup.new_tag("div")
        for tag in content_tags:
            temp_div.append(tag.clone())
        
        clean_text_for_ai = temp_div.get_text(separator='\n\n', strip=True)
        
        processed_sections.append({
            "head_content": head_content,
            "title_html": str(h2),
            "clean_text_for_ai": clean_text_for_ai,
            "style_dictionary": style_dictionary # Pass the same dictionary to every section
        })
            
    return jsonify(processed_sections)

@app.route('/reconstruct', methods=['POST'])
def reconstruct_html():
    data = request.get_json()
    if not data or 'ai_html' not in data or 'style_dictionary' not in data:
        return jsonify({"error": "Missing required data."}), 400

    ai_html = data['ai_html']
    style_dictionary = data['style_dictionary']
    
    soup = BeautifulSoup(ai_html, 'html.parser')
    
    # 2. Process all tags for which we have saved styles
    for tag in soup.find_all(True): # True gets all tags
        tag_name = tag.name
        if tag_name in style_dictionary:
            style_info = style_dictionary[tag_name]
            original_text = tag.get_text(strip=True)
            
            # 3. Create the new, full structure
            tag.clear() # Clear old content to insert the new structure

            # Apply the class to the main tag
            if style_info.get("tag_class"):
                tag['class'] = style_info["tag_class"].split()

            # Create and insert the inner <span>
            if style_info.get("span_class"):
                new_span = soup.new_tag('span')
                new_span['class'] = style_info["span_class"].split()
                new_span.string = original_text
                tag.append(new_span)
            else:
                tag.string = original_text

    return str(soup)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
