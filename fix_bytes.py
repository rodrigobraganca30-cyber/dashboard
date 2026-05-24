filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "rb") as f:
    raw = f.read()

# Contar ocorrencias de \\\\ (double backslash real)
count_before = raw.count(b'\\\\')
print(f"Double backslashes antes: {count_before}")

# Substituir \\\\ por \\ em todo o arquivo
raw = raw.replace(b'\\\\r', b'\\r')
raw = raw.replace(b'\\\\n', b'\\n')
raw = raw.replace(b'\\\\t', b'\\t')
raw = raw.replace(b'\\\\s', b'\\s')

count_after = raw.count(b'\\\\')
print(f"Double backslashes depois: {count_after}")
print(f"Corrigidos: {count_before - count_after}")

with open(filepath, "wb") as f:
    f.write(raw)

print("DONE")
