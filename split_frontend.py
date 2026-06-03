import os

file_path = 'frontend/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract CSS
style_start = content.find('<style>')
style_end = content.find('</style>')
if style_start != -1 and style_end != -1:
    css_content = content[style_start+7:style_end].strip()
    with open('frontend/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    content = content[:style_start] + '<link rel="stylesheet" href="style.css">\n' + content[style_end+8:]

# Extract JS
script_start = content.rfind('<script>')
script_end = content.rfind('</script>')
if script_start != -1 and script_end != -1:
    js_content = content[script_start+8:script_end].strip()
    with open('frontend/script.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    content = content[:script_start] + '<script src="script.js"></script>\n' + content[script_end+9:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Split completed successfully!")
