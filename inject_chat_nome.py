#!/usr/bin/env python3
"""
inject_chat_nome.py
Adiciona nome do cliente no header do chat e permite busca por nome.

MudanÃ§as:
  1. CSS: .chat-main-client (nome em verde no header)
  2. CSS: .chat-contact-phone (telefone abaixo do nome no sidebar)
  3. HTML: <div id="chat-main-client"> entre nome e telefone raw
  4. Placeholder da busca: "Buscar nÃºmero ou nome..."
  5. Filtro: busca por nome OU nÃºmero em chatRenderContacts
  6. Card sidebar: mostra nome do cliente + telefone formatado
  7. chatOpenConversation: preenche o nome no header
"""

import re, shutil, os
from datetime import datetime

if os.path.exists("/docker/dashboard/html/index.html"):
    HTML = "/docker/dashboard/html/index.html"
else:
    HTML = os.path.join(os.path.dirname(__file__), "public_html", "index.html")
BAK  = HTML + ".bak.pre_chat_nome_" + datetime.now().strftime("%Y%m%d_%H%M%S")

print(f"[1/8] Lendo {HTML} ...")
with open(HTML, "r", encoding="utf-8", errors="replace") as f:
    src = f.read()

print(f"[2/8] Criando backup -> {os.path.basename(BAK)}")
shutil.copy2(HTML, BAK)

original_len = len(src)
changes = 0

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. CSS â€” adicionar .chat-main-client e .chat-contact-phone
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_CSS = ".chat-main-phone{font-size:11px;color:#94a3b8;font-family:'DM Mono',monospace}"
NEW_CSS = (
    OLD_CSS +
    "\n  .chat-main-client{font-size:12px;color:#25d366;font-weight:600;margin-top:1px}" +
    "\n  .chat-contact-phone{font-size:10px;color:#475569;font-family:'DM Mono',monospace;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
)
if OLD_CSS in src:
    src = src.replace(OLD_CSS, NEW_CSS, 1)
    changes += 1
    print("[3/8] âœ… CSS adicionado (.chat-main-client + .chat-contact-phone)")
else:
    print("[3/8] âš ï¸  CSS alvo nÃ£o encontrado â€” verifique manualmente")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. HTML â€” inserir div#chat-main-client entre name e phone
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_HTML = '<div class="chat-main-name" id="chat-main-name">-</div>\n              <div class="chat-main-phone" id="chat-main-phone">-</div>'
NEW_HTML = (
    '<div class="chat-main-name" id="chat-main-name">-</div>\n'
    '              <div class="chat-main-client" id="chat-main-client"></div>\n'
    '              <div class="chat-main-phone" id="chat-main-phone">-</div>'
)
if OLD_HTML in src:
    src = src.replace(OLD_HTML, NEW_HTML, 1)
    changes += 1
    print("[4/8] âœ… HTML div#chat-main-client inserido")
else:
    # Tenta variaÃ§Ã£o com â€”
    OLD_HTML2 = '<div class="chat-main-name" id="chat-main-name">\u2014</div>'
    if OLD_HTML2 in src:
        src = src.replace(
            OLD_HTML2,
            '<div class="chat-main-name" id="chat-main-name">\u2014</div>\n              <div class="chat-main-client" id="chat-main-client"></div>',
            1
        )
        changes += 1
        print("[4/8] âœ… HTML div#chat-main-client inserido (variaÃ§Ã£o â€”)")
    else:
        print("[4/8] âš ï¸  HTML alvo nÃ£o encontrado â€” verifique manualmente")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. Placeholder da busca
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_PH = 'placeholder="ðŸ” Buscar nÃºmero..."'
NEW_PH = 'placeholder="ðŸ” Buscar nÃºmero ou nome..."'
# Tenta tambÃ©m versÃ£o sem emoji (encoding pode variar)
if OLD_PH in src:
    src = src.replace(OLD_PH, NEW_PH, 1)
    changes += 1
    print("[5/8] âœ… Placeholder atualizado")
else:
    # Tenta padrÃ£o alternativo com ?? (encoding quebrado)
    alt = re.sub(r'placeholder="[^"]*Buscar n[^"]*\.\.\."', NEW_PH, src, count=1)
    if alt != src:
        src = alt
        changes += 1
        print("[5/8] âœ… Placeholder atualizado (regex fallback)")
    else:
        print("[5/8] âš ï¸  Placeholder nÃ£o encontrado")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. Filtro em chatRenderContacts â€” busca por nome OU nÃºmero
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_FILTER = "if (q) filtered = list.filter(function(c) { return c.phone.includes(q); });"
NEW_FILTER = (
    "if (q) filtered = list.filter(function(c) {\n"
    "      var nome = _chatGetNomeByPhone(c.phone).toLowerCase();\n"
    "      return c.phone.includes(q) || nome.includes(q);\n"
    "    });"
)
if OLD_FILTER in src:
    src = src.replace(OLD_FILTER, NEW_FILTER, 1)
    changes += 1
    print("[6/8] âœ… Filtro de busca expandido (nome + nÃºmero)")
else:
    print("[6/8] âš ï¸  Filtro alvo nÃ£o encontrado")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. Card sidebar â€” mostra nome + telefone formatado
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_CARD = "html += '<div class=\"chat-contact-name\">' + _chatFormatPhone(c.phone) + '</div>';"
NEW_CARD = (
    "var _cn = _chatGetNomeByPhone(c.phone);\n"
    "      html += '<div class=\"chat-contact-name\">' + (_cn || _chatFormatPhone(c.phone)) + '</div>';\n"
    "      if (_cn) html += '<div class=\"chat-contact-phone\">' + _chatFormatPhone(c.phone) + '</div>';"
)
if OLD_CARD in src:
    src = src.replace(OLD_CARD, NEW_CARD, 1)
    changes += 1
    print("[7/8] âœ… Card sidebar atualizado (nome + telefone)")
else:
    print("[7/8] âš ï¸  Card sidebar alvo nÃ£o encontrado")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 6. chatOpenConversation â€” preenche nome no header + funÃ§Ã£o lookup
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OLD_OPEN = (
    "document.getElementById('chat-main-name').textContent = _chatFormatPhone(phone);\n"
    "    document.getElementById('chat-main-phone').textContent = phone;"
)
NEW_OPEN = (
    "document.getElementById('chat-main-name').textContent = _chatFormatPhone(phone);\n"
    "    document.getElementById('chat-main-client').textContent = _chatGetNomeByPhone(phone);\n"
    "    document.getElementById('chat-main-phone').textContent = phone;"
)

# FunÃ§Ã£o helper a ser injetada antes de chatRenderContacts
HELPER_FN = """
  // â”€â”€ Helper: busca nome do cliente pelo telefone (waClients) â”€â”€
  function _chatGetNomeByPhone(phone) {
    if (!phone || typeof waClients === 'undefined') return '';
    var clean = phone.replace(/\\D/g, '');
    for (var i = 0; i < waClients.length; i++) {
      var cp = (waClients[i].phone || '').replace(/\\D/g, '');
      if (cp && (cp === clean || cp.slice(-8) === clean.slice(-8))) {
        return waClients[i].nome || '';
      }
    }
    return '';
  }
"""

if OLD_OPEN in src:
    src = src.replace(OLD_OPEN, NEW_OPEN, 1)
    changes += 1
    print("[8/8] âœ… chatOpenConversation atualizado (nome no header)")
else:
    print("[8/8] âš ï¸  chatOpenConversation alvo nÃ£o encontrado")

# Injeta a funÃ§Ã£o helper antes de chatRenderContacts
ANCHOR_FN = "function chatRenderContacts(list) {"
if HELPER_FN.strip() not in src and ANCHOR_FN in src:
    src = src.replace(ANCHOR_FN, HELPER_FN + "  " + ANCHOR_FN, 1)
    changes += 1
    print("[+]   âœ… FunÃ§Ã£o _chatGetNomeByPhone injetada")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Salva
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if changes == 0:
    print("\nâŒ Nenhuma alteraÃ§Ã£o aplicada. Verifique o HTML manualmente.")
else:
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(src)
    new_len = len(src)
    print(f"\nâœ… {changes} alteraÃ§Ãµes aplicadas. Arquivo: {original_len} â†’ {new_len} bytes")
    print(f"   Backup: {os.path.basename(BAK)}")

