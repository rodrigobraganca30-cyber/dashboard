#!/usr/bin/env python3
"""
patch_meta_templates_v2.py
Insere a secao de Gerenciador de Templates Meta DENTRO da aba wa-config,
logo antes do </div></div> que fecha o grid-2 e o wa-sub.
"""
import sys

ARQUIVO = '/docker/dashboard/whatsapp_agenda_gen.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Ancora correta: o fechamento do grid-2 e wa-sub id="wa-config"
# Essa sequencia e unica no arquivo
ANCHOR = (
    '      </div>\n'
    '    </div>\n'
    '  </div>\n'
    '\n'
    '  <!-- SUB: Chat -->'
)

if ANCHOR not in content:
    print('[ERRO] Ancora nao encontrada.')
    sys.exit(1)

# O bloco e inserido DENTRO do wa-config, antes do fechamento dos divs
HTML_BLOCK = (
    '    </div>\n'                                   # fecha grid-2
    '\n'
    '    <!-- GERENCIADOR DE TEMPLATES META -->\n'
    '    <div class="chart-card" style="margin-top:20px">\n'
    '      <div class="chart-title">📋 Templates de Mensagens (Meta)</div>\n'
    '      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:12px">\n'
    '        <!-- FORM CRIAR -->\n'
    '        <div>\n'
    '          <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px">Criar Novo Template</div>\n'
    '          <div style="display:flex;flex-direction:column;gap:10px">\n'
    '            <input class="wa-cfg-input" id="tpl-name" placeholder="Nome (ex: confirmacao_visita)" style="font-family:monospace">\n'
    '            <select class="wa-cfg-input" id="tpl-category" style="cursor:pointer">\n'
    '              <option value="UTILITY">📦 Utility (Notificação/Aviso)</option>\n'
    '              <option value="MARKETING">📢 Marketing (Promoção)</option>\n'
    '              <option value="AUTHENTICATION">🔐 Authentication (Código)</option>\n'
    '            </select>\n'
    '            <textarea class="wa-cfg-input" id="tpl-body" rows="4" placeholder="Corpo da mensagem. Use {1}, {2} para variáveis." style="resize:vertical;font-size:13px;line-height:1.5"></textarea>\n'
    '            <div style="font-size:11px;color:#475569">\n'
    '              <b>Variáveis:</b> Use <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{1}</code>, <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{2}</code>, etc.\n'
    '            </div>\n'
    '            <button class="wa-cfg-btn" onclick="tplCreate()" id="tpl-create-btn" style="padding:12px;font-size:14px">\n'
    '              🚀 Enviar para Aprovação da Meta\n'
    '            </button>\n'
    '          </div>\n'
    '          <div style="margin-top:16px">\n'
    '            <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Preview</div>\n'
    '            <div style="background:#0b141a;border-radius:12px;padding:16px">\n'
    '              <div style="background:#005c4b;color:white;padding:10px 14px;border-radius:10px 10px 2px 10px;font-size:13px;line-height:1.6;max-width:280px;word-wrap:break-word" id="tpl-preview">\n'
    '                <span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>\n'
    '              </div>\n'
    '              <div style="text-align:right;font-size:10px;color:#667781;margin-top:4px">12:00 ✓✓</div>\n'
    '            </div>\n'
    '          </div>\n'
    '        </div>\n'
    '        <!-- TABELA -->\n'
    '        <div>\n'
    '          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">\n'
    '            <div style="font-size:12px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Templates Cadastrados</div>\n'
    '            <button class="wa-cfg-btn" onclick="tplLoad()" style="padding:5px 12px;font-size:11px">🔄 Atualizar</button>\n'
    '          </div>\n'
    '          <div id="tpl-table-wrap" style="max-height:420px;overflow-y:auto">\n'
    '            <table class="data-table" style="font-size:12px">\n'
    '              <thead><tr>\n'
    '                <th style="padding:8px 10px">Nome</th>\n'
    '                <th style="padding:8px 10px">Categoria</th>\n'
    '                <th style="padding:8px 10px">Status</th>\n'
    '                <th style="padding:8px 10px;text-align:right">Ação</th>\n'
    '              </tr></thead>\n'
    '              <tbody id="tpl-tbody">\n'
    '                <tr><td colspan="4" style="text-align:center;color:#64748b;padding:24px">Clique em "Atualizar" para carregar os templates</td></tr>\n'
    '              </tbody>\n'
    '            </table>\n'
    '          </div>\n'
    '          <div id="tpl-msg" style="font-size:12px;margin-top:8px;color:#64748b"></div>\n'
    '        </div>\n'
    '      </div>\n'
    '    </div>\n'
    '    <!-- FIM GERENCIADOR DE TEMPLATES META -->\n'
    '\n'
    '  </div>\n'                                     # fecha wa-sub wa-config
    '\n'
    '  <!-- SUB: Chat -->'
)

# A ancora original tem o grid-2 + wa-config fechando juntos,
# o novo bloco substitui esse trecho adicionando o gerenciador antes do fechamento
ANCHOR_ORIGINAL = (
    '      </div>\n'
    '    </div>\n'
    '  </div>\n'
    '\n'
    '  <!-- SUB: Chat -->'
)

NEW_ANCHOR = HTML_BLOCK

content = content.replace(ANCHOR_ORIGINAL, NEW_ANCHOR, 1)

# JS: inserir funcoes antes do fechamento </script>
JS_BLOCK = '''
  // -- Gerenciador de Templates Meta --
  async function tplLoad() {
    if(!WA_BACKEND) { alert('Configure o backend primeiro'); return; }
    document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;padding:16px">Carregando...</td></tr>';
    try {
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY);
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      var tpls = d.templates || [];
      if (!tpls.length) {
        document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#64748b;padding:20px">Nenhum template ainda.<br>Crie o primeiro!</td></tr>';
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
        html += '<button class="wa-cfg-btn" style="padding:4px 8px;font-size:10px;background:#1e293b" onclick="tplDelete(' + "'" + t.name + "'" + ')">🗑️</button>';
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
    btn.disabled = true; btn.textContent = 'Enviando...';
    try {
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: name, category: cat, body_text: body, language: 'pt_BR' })
      });
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      btn.textContent = 'Enviado!'; btn.style.background = '#065f46';
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

  document.addEventListener('input', function(e) {
    if (e.target && e.target.id === 'tpl-body') {
      var txt = e.target.value || '';
      var preview = document.getElementById('tpl-preview');
      if (preview) {
        if (txt) {
          preview.innerHTML = txt.replace(/\\n/g, '<br>');
        } else {
          preview.innerHTML = '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
        }
      }
    }
  });
'''

JS_ANCHOR = '  </script>\n</div>'
JS_ANCHOR2 = '  </script>\r\n</div>'

if 'async function tplLoad' not in content:
    if JS_ANCHOR in content:
        content = content.replace(JS_ANCHOR, JS_BLOCK + '\n  </script>\n</div>', 1)
        print('[OK] JS inserido.')
    elif JS_ANCHOR2 in content:
        content = content.replace(JS_ANCHOR2, JS_BLOCK + '\n  </script>\n</div>', 1)
        print('[OK] JS inserido (alt).')
    else:
        print('[AVISO] Ancora JS nao encontrada.')
else:
    print('[INFO] JS ja existe, pulando.')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Arquivo salvo:', ARQUIVO)
