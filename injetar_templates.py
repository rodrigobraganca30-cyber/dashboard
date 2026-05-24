"""
injetar_templates.py — Injeta a seção de Templates Meta na aba Configuração do dashboard.
Roda no servidor: python3 /docker/dashboard/injetar_templates.py
"""
import os

INDEX_HTML = '/docker/dashboard/html/index.html'
MARKER = '<!-- TF_META_TEMPLATES -->'

TEMPLATE_HTML = '''<!-- TF_META_TEMPLATES -->
    <div class="chart-card" style="margin-top:20px;grid-column:1/-1">
      <div class="chart-title">📋 Templates de Mensagens (Meta)</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:12px">
        <!-- FORM -->
        <div>
          <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px">Criar Novo Template</div>
          <div style="display:flex;flex-direction:column;gap:10px">
            <input class="wa-cfg-input" id="tpl-name" placeholder="Nome (ex: confirmacao_visita)" style="font-family:monospace">
            <select class="wa-cfg-input" id="tpl-category" style="cursor:pointer">
              <option value="UTILITY">📦 Utility (Notificação/Aviso)</option>
              <option value="MARKETING">📢 Marketing (Promoção)</option>
              <option value="AUTHENTICATION">🔐 Authentication (Código)</option>
            </select>
            <textarea class="wa-cfg-input" id="tpl-body" rows="4" placeholder="Corpo da mensagem. Use {{1}}, {{2}} para variáveis.&#10;Ex: Olá {{1}}, sua visita está agendada para {{2}}." style="resize:vertical;font-size:13px;line-height:1.5"></textarea>
            <div style="font-size:11px;color:#475569">
              <b>Variáveis:</b> Use <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{{1}}</code>, <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{{2}}</code>, etc. para dados dinâmicos (nome, data, endereço).
            </div>
            <button class="wa-cfg-btn" onclick="tplCreate()" id="tpl-create-btn" style="padding:12px;font-size:14px">
              🚀 Enviar para Aprovação da Meta
            </button>
          </div>
          <!-- Preview -->
          <div style="margin-top:16px">
            <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Preview</div>
            <div style="background:#0b141a;border-radius:12px;padding:16px;position:relative">
              <div style="background:#005c4b;color:white;padding:10px 14px;border-radius:10px 10px 2px 10px;font-size:13px;line-height:1.6;max-width:280px;word-wrap:break-word" id="tpl-preview">
                <span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>
              </div>
              <div style="text-align:right;font-size:10px;color:#667781;margin-top:4px">12:00 ✓✓</div>
            </div>
          </div>
        </div>
        <!-- TABLE -->
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="font-size:12px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Templates Cadastrados</div>
            <button class="wa-cfg-btn" onclick="tplLoad()" style="padding:5px 12px;font-size:11px">🔄 Atualizar</button>
          </div>
          <div id="tpl-table-wrap" style="max-height:420px;overflow-y:auto">
            <table class="data-table" style="font-size:12px">
              <thead>
                <tr>
                  <th style="padding:8px 10px">Nome</th>
                  <th style="padding:8px 10px">Categoria</th>
                  <th style="padding:8px 10px">Status</th>
                  <th style="padding:8px 10px;text-align:right">Ação</th>
                </tr>
              </thead>
              <tbody id="tpl-tbody">
                <tr><td colspan="4" style="text-align:center;color:#64748b;padding:24px">Clique em "Atualizar" para carregar os templates</td></tr>
              </tbody>
            </table>
          </div>
          <div id="tpl-msg" style="font-size:12px;margin-top:8px;color:#64748b"></div>
        </div>
      </div>
    </div>
'''

TEMPLATE_JS = '''
// ── META TEMPLATES ──
var _tplBodyEl = document.getElementById('tpl-body');
if (_tplBodyEl) {
  _tplBodyEl.addEventListener('input', function() {
    var txt = this.value || '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
    // Highlight variables
    txt = txt.replace(/\\{\\{(\\d+)\\}\\}/g, '<b style="color:#25D366">[$1]</b>');
    txt = txt.replace(/\\n/g, '<br>');
    document.getElementById('tpl-preview').innerHTML = txt;
  });
}

async function tplLoad() {
  if(!WA_BACKEND) { alert('Configure o backend primeiro'); return; }
  document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;padding:16px"><i class="fas fa-spinner fa-spin"></i> Carregando...</td></tr>';
  try {
    var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY);
    var d = await r.json();
    if (d.error) throw new Error(d.error);
    var tpls = d.templates || [];
    if (!tpls.length) {
      document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#64748b;padding:20px">Nenhum template encontrado.<br>Crie o primeiro!</td></tr>';
      document.getElementById('tpl-msg').textContent = 'Total: 0 templates';
      return;
    }
    var statusMap = {APPROVED:'🟢 Aprovado', PENDING:'🟡 Pendente', REJECTED:'🔴 Rejeitado', PAUSED:'⏸️ Pausado', DISABLED:'⛔ Desativado'};
    var html = '';
    tpls.forEach(function(t) {
      var st = statusMap[t.status] || t.status;
      var cat = {UTILITY:'📦 Utility', MARKETING:'📢 Marketing', AUTHENTICATION:'🔐 Auth'}[t.category] || t.category;
      html += '<tr>';
      html += '<td style="padding:8px 10px;font-family:monospace;font-size:11px">' + t.name + '</td>';
      html += '<td style="padding:8px 10px">' + cat + '</td>';
      html += '<td style="padding:8px 10px">' + st + '</td>';
      html += '<td style="padding:8px 10px;text-align:right">';
      html += '<button class="wa-cfg-btn" style="padding:4px 8px;font-size:10px;background:#1e293b" onclick="tplDelete(\\'' + t.name + '\\')">🗑️</button>';
      html += '</td></tr>';
    });
    document.getElementById('tpl-tbody').innerHTML = html;
    document.getElementById('tpl-msg').textContent = 'Total: ' + tpls.length + ' template(s)';
  } catch(e) {
    document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ff6b81;padding:16px">' + e.message + '</td></tr>';
  }
}

async function tplCreate() {
  if(!WA_BACKEND) { alert('Configure o backend primeiro'); return; }
  var name = document.getElementById('tpl-name').value.trim();
  var cat = document.getElementById('tpl-category').value;
  var body = document.getElementById('tpl-body').value.trim();
  if (!name || !body) { alert('Preencha o nome e o corpo da mensagem'); return; }
  var btn = document.getElementById('tpl-create-btn');
  btn.disabled = true; btn.textContent = '⏳ Enviando...';
  try {
    var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: name, category: cat, body_text: body, language: 'pt_BR' })
    });
    var d = await r.json();
    if (d.error) throw new Error(d.error);
    btn.textContent = '✅ Enviado!'; btn.style.background = '#065f46';
    document.getElementById('tpl-name').value = '';
    document.getElementById('tpl-body').value = '';
    document.getElementById('tpl-preview').innerHTML = '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
    setTimeout(function() {
      btn.textContent = '🚀 Enviar para Aprovação da Meta';
      btn.style.background = '';
      btn.disabled = false;
    }, 2000);
    tplLoad();
  } catch(e) {
    alert('Erro: ' + e.message);
    btn.textContent = '🚀 Enviar para Aprovação da Meta';
    btn.style.background = '';
    btn.disabled = false;
  }
}

async function tplDelete(name) {
  if (!confirm('Excluir o template "' + name + '"?')) return;
  try {
    var r = await fetch(WA_BACKEND + '/meta/templates/' + name + '?apikey=' + WA_KEY, { method: 'DELETE' });
    var d = await r.json();
    if (d.error) throw new Error(d.error);
    tplLoad();
  } catch(e) {
    alert('Erro: ' + e.message);
  }
}
'''

def main():
    if not os.path.exists(INDEX_HTML):
        print(f"[ERRO] {INDEX_HTML} não encontrado!")
        return

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print("[OK] Seção de Templates já está no index.html")
        return

    # 1. Inject HTML - inside the wa-config div (before its closing </div>)
    wa_config_start = html.find('id="wa-config"')
    if wa_config_start == -1:
        print("[ERRO] Não encontrou div wa-config")
        return
    # Find the start of the wa-config div
    wa_config_div = html.rfind('<div', 0, wa_config_start)
    # Count divs to find the matching closing </div>
    count = 1
    idx = wa_config_start + 14  # skip past id="wa-config"
    while count > 0 and idx < len(html):
        nxt_o = html.find('<div', idx)
        nxt_c = html.find('</div', idx)
        if nxt_o != -1 and (nxt_c == -1 or nxt_o < nxt_c):
            count += 1; idx = nxt_o + 4
        elif nxt_c != -1:
            count -= 1
            if count == 0:
                # Insert TEMPLATE_HTML just before this closing </div>
                html = html[:nxt_c] + '\n' + TEMPLATE_HTML + '\n  ' + html[nxt_c:]
                break
            idx = nxt_c + 6
        else:
            break
    else:
        print("[ERRO] Não encontrou fechamento do wa-config")
        return

    # 2. Also need to add WABA ID input to the existing config form
    # Add WABA ID field after Phone Number ID
    phone_field = '<input class="wa-cfg-input" id="wa-meta-phone" placeholder="Phone Number ID (Meta)">'
    if phone_field in html:
        waba_field = phone_field + '\n          <input class="wa-cfg-input" id="wa-meta-waba" placeholder="WABA ID (WhatsApp Business Account ID)">'
        html = html.replace(phone_field, waba_field)
        print("  [+] Campo WABA ID adicionado")

    # 3. Update waSaveMetaConfig to also send wabaId
    old_save = "async function waSaveMetaConfig()"
    if old_save not in html:
        # The function may be named differently, let's search for it
        pass

    # 4. Inject JS before closing </script>
    # Find the last </script> tag
    last_script = html.rfind('</script>')
    if last_script != -1:
        html = html[:last_script] + TEMPLATE_JS + '\n' + html[last_script:]
        print("  [+] JavaScript de Templates injetado")

    # 5. Update the waSaveMetaConfig function to include wabaId
    old_meta_fn = "var t = document.getElementById('wa-meta-token').value.trim();\n    var p = document.getElementById('wa-meta-phone').value.trim();"
    new_meta_fn = "var t = document.getElementById('wa-meta-token').value.trim();\n    var p = document.getElementById('wa-meta-phone').value.trim();\n    var wb = document.getElementById('wa-meta-waba') ? document.getElementById('wa-meta-waba').value.trim() : '';"
    # Try with \r\n
    old_meta_fn_rn = old_meta_fn.replace('\n', '\r\n')
    new_meta_fn_rn = new_meta_fn.replace('\n', '\r\n')
    
    if old_meta_fn_rn in html:
        html = html.replace(old_meta_fn_rn, new_meta_fn_rn)
        print("  [+] Variável wabaId adicionada na função (\\r\\n)")
    elif old_meta_fn in html:
        html = html.replace(old_meta_fn, new_meta_fn)
        print("  [+] Variável wabaId adicionada na função (\\n)")

    old_body = "body: JSON.stringify({ token: t, phoneId: p })"
    new_body = "body: JSON.stringify({ token: t, phoneId: p, wabaId: wb })"
    if old_body in html:
        html = html.replace(old_body, new_body)
        print("  [+] wabaId incluído no payload de save")

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print("[OK] Seção de Templates Meta injetada no index.html!")

if __name__ == '__main__':
    main()
