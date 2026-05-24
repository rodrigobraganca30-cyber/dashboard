filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old = """window._updatePreview?.()??''"""
new = """(window._updatePreview?window._updatePreview():'')"""

if old in content:
    content = content.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK - optional chaining removido")
else:
    print("SKIP - nao encontrado")
