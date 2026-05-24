#!/usr/bin/env python3
"""
patch_meta_templates.py
Insere a secao de Gerenciador de Templates Meta na aba Configuracao
do whatsapp_agenda_gen.py do servidor.
Ponto de insercao: logo antes de <!-- SUB: Chat -->
"""
import sys

ARQUIVO = '/docker/dashboard/whatsapp_agenda_gen.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Ponto de insercao: logo antes da linha <!-- SUB: Chat -->
ANCHOR = '  <!-- SUB: Chat -->'

if ANCHOR not in content:
    print('[ERRO] Ancora nao encontrada. Verifique o arquivo.')
    sys.exit(1)

# Bloco HTML a inserir (entre wa-config e o Chat)
HTML_BLOCK = '''  <!-- GERENCIADOR DE TEMPLATES META -->
  <div class="chart-card" style="margin-top:20px;grid-column:1/-1">
    <div class="chart-title">📋 Templates de Mensagens (Meta)</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:12px">
      <!-- FORM CRIAR -->
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
      <!-- TABELA TEMPLATES -->
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
  <!-- FIM GERENCIADOR DE TEMPLATES META -->

'''

# Bloco JS a inserir — logo antes do fechamento </script>
JS_BLOCK = '''
  // ── Gerenciador de Templates Meta ──
  async function tplLoad() {{
    if(!WA_BACKEND) {{ alert('Configure o backend primeiro'); return; }}
    document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;padding:16px">Carregando...</td></tr>';
    try {{
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY);
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      var tpls = d.templates || [];
      if (!tpls.length) {{
        document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#64748b;padding:20px">Nenhum template encontrado.<br>Crie o primeiro!</td></tr>';
        document.getElementById('tpl-msg').textContent = 'Total: 0 templates';
        return;
      }}
      var statusMap = {{APPROVED:'🟢 Aprovado', PENDING:'🟡 Pendente', REJECTED:'🔴 Rejeitado', PAUSED:'⏸️ Pausado', DISABLED:'⛔ Desativado'}};
      var html = '';
      tpls.forEach(function(t) {{
        var st = statusMap[t.status] || t.status;
        var cat = {{UTILITY:'📦 Utility', MARKETING:'📢 Marketing', AUTHENTICATION:'🔐 Auth'}}[t.category] || t.category;
        html += '<tr>';
        html += '<td style="padding:8px 10px;font-family:monospace;font-size:11px">' + t.name + '</td>';
        html += '<td style="padding:8px 10px">' + cat + '</td>';
        html += '<td style="padding:8px 10px">' + st + '</td>';
        html += '<td style="padding:8px 10px;text-align:right">';
        html += '<button class="wa-cfg-btn" style="padding:4px 8px;font-size:10px;background:#1e293b" onclick="tplDelete(\\'' + t.name + '\\')">' + '🗑️' + '</button>';
        html += '</td></tr>';
      }});
      document.getElementById('tpl-tbody').innerHTML = html;
      document.getElementById('tpl-msg').textContent = 'Total: ' + tpls.length + ' template(s)';
    }} catch(e) {{
      document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ff6b81;padding:16px">' + e.message + '</td></tr>';
    }}
  }}

  async function tplCreate() {{
    if(!WA_BACKEND) {{ alert('Configure o backend primeiro'); return; }}
    var name = document.getElementById('tpl-name').value.trim();
    var cat = document.getElementById('tpl-category').value;
    var body = document.getElementById('tpl-body').value.trim();
    if (!name || !body) {{ alert('Preencha o nome e o corpo da mensagem'); return; }}
    var btn = document.getElementById('tpl-create-btn');
    btn.disabled = true; btn.textContent = '⏳ Enviando...';
    try {{
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY, {{
        method: 'POST',
        headers: {{'Content-Type':'application/json'}},
        body: JSON.stringify({{ name: name, category: cat, body_text: body, language: 'pt_BR' }})
      }});
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      btn.textContent = '✅ Enviado!'; btn.style.background = '#065f46';
      document.getElementById('tpl-name').value = '';
      document.getElementById('tpl-body').value = '';
      document.getElementById('tpl-preview').innerHTML = '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
      setTimeout(function() {{
        btn.textContent = '🚀 Enviar para Aprovação da Meta';
        btn.style.background = '';
        btn.disabled = false;
      }}, 2000);
      tplLoad();
    }} catch(e) {{
      alert('Erro: ' + e.message);
      btn.textContent = '🚀 Enviar para Aprovação da Meta';
      btn.style.background = '';
      btn.disabled = false;
    }}
  }}

  async function tplDelete(name) {{
    if (!confirm('Excluir o template "' + name + '"?')) return;
    try {{
      var r = await fetch(WA_BACKEND + '/meta/templates/' + name + '?apikey=' + WA_KEY, {{ method: 'DELETE' }});
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      tplLoad();
    }} catch(e) {{
      alert('Erro: ' + e.message);
    }}
  }}

  // Preview em tempo real do template
  document.addEventListener('input', function(e) {{
    if (e.target.id === 'tpl-body') {{
      var txt = e.target.value || '';
      var preview = document.getElementById('tpl-preview');
      if (preview) {{
        if (txt) {{
          preview.innerHTML = txt.replace(/\\n/g, '<br>').replace(/\\{{1\\}}/g, '<b style="color:#a7f3d0">Nome</b>').replace(/\\{{2\\}}/g, '<b style="color:#a7f3d0">Data</b>').replace(/\\{{3\\}}/g, '<b style="color:#a7f3d0">Cidade</b>').replace(/\\{{(\\d+)\\}}/g, '<b style="color:#a7f3d0">Var$1</b>');
        }} else {{
          preview.innerHTML = '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
        }}
      }}
    }}
  }});
'''

# Patch 1: inserir bloco HTML antes do <!-- SUB: Chat -->
if '<!-- GERENCIADOR DE TEMPLATES META -->' in content:
    print('[INFO] Bloco HTML ja existe no arquivo. Pulando insercao HTML.')
else:
    content = content.replace(ANCHOR, HTML_BLOCK + ANCHOR, 1)
    print('[OK] Bloco HTML inserido.')

# Patch 2: inserir JS antes do fechamento </script>
JS_ANCHOR = '  </script>\n</div>'
if 'async function tplLoad()' in content:
    print('[INFO] Funcoes JS ja existem. Pulando insercao JS.')
else:
    if JS_ANCHOR in content:
        content = content.replace(JS_ANCHOR, JS_BLOCK + '\n  </script>\n</div>', 1)
        print('[OK] Funcoes JS inseridas.')
    else:
        # tenta alternativa
        JS_ANCHOR2 = '  </script>\r\n</div>'
        if JS_ANCHOR2 in content:
            content = content.replace(JS_ANCHOR2, JS_BLOCK + '\n  </script>\n</div>', 1)
            print('[OK] Funcoes JS inseridas (alt).')
        else:
            print('[AVISO] Ancora JS nao encontrada. Verifique manualmente.')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Arquivo salvo:', ARQUIVO)
