filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix double-escaped regex: \\r -> \r, \\n -> \n, \\t -> \t, \\s -> \s
# Mas APENAS dentro das funcoes que adicionamos (showMappingModal, parseCSVWithMapping, applyMapping)
# Na verdade, o problema e que o Python escreveu \\r como dois chars (backslash + r)
# quando deveria ser um char (backslash real)

# Vou buscar e corrigir os padoes especificos
fixes = [
    # Regex splits
    ("/\\\\r?\\\\n/", "/\\r?\\n/"),
    ("'\\\\t'", "'\\t'"),
    # String escapes no parseCSVWithMapping
    ("/\\\\s+/g", "/\\s+/g"),
]

changes = 0
for old, new in fixes:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        changes += count
        print(f"  Fixed: {repr(old)} -> {repr(new)} ({count}x)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal: {changes} regex fixes")
