filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# Fix 1: Optional chaining pode nao funcionar em alguns browsers
old_onchange = """onchange="document.getElementById('map-preview').innerHTML=window._updatePreview?.()??''" """
new_onchange = """onchange="if(window._updatePreview)document.getElementById('map-preview').innerHTML=window._updatePreview()" """
if old_onchange in content:
    content = content.replace(old_onchange, new_onchange)
    changes += 1
    print("Fix 1 OK - removido optional chaining")

# Fix 2: Garantir que o modal nao esteja escondido no CSS inicial
# Adicionar z-index maior ao mapping-modal
old_modal_create = """  modal.className = 'modal-overlay';"""
new_modal_create = """  modal.className = 'modal-overlay';
  modal.style.zIndex = '999';"""
if old_modal_create in content:
    content = content.replace(old_modal_create, new_modal_create)
    changes += 1
    print("Fix 2 OK - z-index 999 adicionado")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print(f"\nTotal: {changes} fixes")
