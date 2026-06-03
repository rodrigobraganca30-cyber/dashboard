filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Adicionar debug com alert na funcao showMappingModal
old = """function showMappingModal(csvText) {
  const lines = csvText.split(/\r?\n/).filter(l => l.trim());"""

new = """function showMappingModal(csvText) {
  try {
  console.log('[DEBUG] showMappingModal chamado, csvText length:', csvText.length);
  const lines = csvText.split(/\\r?\\n/).filter(l => l.trim());"""

if old in content:
    content = content.replace(old, new)
    print("Debug 1 OK - adicionado console.log no showMappingModal")
else:
    print("Debug 1 SKIP")
    # Tentar ver o que tem
    idx = content.find("function showMappingModal")
    if idx >= 0:
        print(f"  Funcao encontrada na posicao {idx}")
        print(f"  Trecho: {repr(content[idx:idx+120])}")

# Fechar o try/catch antes do fim da funcao
old_end = """  window._updatePreview = previewHTML;
  // Trigger initial preview
  setTimeout(() => { document.getElementById('map-preview').innerHTML = previewHTML(); }, 50);
}"""

new_end = """  window._updatePreview = previewHTML;
  // Trigger initial preview
  setTimeout(() => { document.getElementById('map-preview').innerHTML = previewHTML(); }, 50);
  } catch(err) { alert('Erro no mapeamento: ' + err.message); console.error(err); }
}"""

if old_end in content:
    content = content.replace(old_end, new_end)
    print("Debug 2 OK - adicionado try/catch com alert")
else:
    print("Debug 2 SKIP")

# Tambem adicionar debug no processCSV
old_process = """  const processCSV = (csvText) => {
    window._pendingCSV = csvText;
    showMappingModal(csvText);
  };"""

new_process = """  const processCSV = (csvText) => {
    console.log('[DEBUG] processCSV chamado, tamanho:', csvText.length);
    window._pendingCSV = csvText;
    try { showMappingModal(csvText); } catch(err) { alert('Erro: ' + err.message); console.error(err); }
  };"""

if old_process in content:
    content = content.replace(old_process, new_process)
    print("Debug 3 OK - adicionado debug no processCSV")
else:
    print("Debug 3 SKIP")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
