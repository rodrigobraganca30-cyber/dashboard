#!/usr/bin/env python3
import os, shutil, datetime, sys, re

DASH = "/docker/dashboard/html/index.html"

def log(m): print(m)

def backup(p):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(p, p + ".bak." + ts)
    log("[BAK] " + p + ".bak." + ts)

def load(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def save(p, html):
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)

# 1. LOGIN GUARD
def inject_login_guard(html):
    if "tf_auth" in html:
        log("[1] Login guard OK"); return html
    guard = '<script>if(sessionStorage.getItem("tf_auth")!=="ok"){window.location.replace("login.html");}</script>'
    if "<head>" in html:
        html = html.replace("<head>", "<head>\n" + guard, 1)
        log("[1] Login guard INJETADO")
    return html

# 2. BOTOES ADMIN
def inject_admin_buttons(html):
    # Cleanup: remover bloco TF_ADMIN_BTNS do injetar_admin_btn.py (previne duplicacao)
    if '<!-- TF_ADMIN_BTNS -->' in html:
        tf_start = html.find('<!-- TF_ADMIN_BTNS -->')
        # O bloco TF_ADMIN_BTNS termina no </script> logo apos (script do tf-user-label)
        tf_script_end = html.find('</script>', tf_start)
        if tf_script_end != -1:
            tf_end = tf_script_end + len('</script>')
            # Pula newlines apos </script>
            while tf_end < len(html) and html[tf_end] in '\r\n':
                tf_end += 1
            html = html[:tf_start] + html[tf_end:]
            log("[2] Cleanup: bloco TF_ADMIN_BTNS removido (duplicacao do injetar_admin_btn.py)")

    if "btn-logout-dash" in html:
        log("[2] Botoes admin OK"); return html
    
    # Match header-date div with or without style="display:none;"
    pattern = r'(  <div class="header-date"(?:\s+style="[^"]*")?>\s*\n    <span class="live-dot"></span>\s*\n    <span id="current-date">CARREGANDO\.\.\.</span>\s*\n  </div>\s*\n</div>)'
    
    btns = (
        '  <div class="header-date" style="display:none;">\n'
        '    <span class="live-dot"></span>\n'
        '    <span id="current-date">CARREGANDO...</span>\n'
        '  </div>\n'
        '  <div class="header-right" style="margin-left:auto;display:flex;align-items:center;gap:16px;">\n'
        '    <span id="header-user-name" style="font-size:12px;color:#94a3b8;font-family:var(--font-mono);font-weight:600;display:flex;align-items:center;gap:6px;"></span>\n'
        '    <a href="admin_usuarios.html" \n'
        '       style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a5b4fc;font-size:12px;font-weight:600;text-decoration:none;cursor:pointer;transition:all 0.2s ease;" \n'
        '       onmouseover="this.style.background=\'#7c3aed\';this.style.color=\'#ffffff\';" \n'
        '       onmouseout="this.style.background=\'rgba(124,58,237,0.15)\';this.style.color=\'#a5b4fc\';" \n'
        '       title="Gerenciar Usuários">\n'
        '       👥 Usuários\n'
        '    </a>\n'
        '    <button id="btn-logout-dash" \n'
        '            onclick="sessionStorage.clear();window.location.replace(\'login.html\');" \n'
        '            style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.2s ease;"\n'
        '            onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#ffffff\';" \n'
        '            onmouseout="this.style.background=\'rgba(239,68,68,0.15)\';this.style.color=\'#fca5a5\';">\n'
        '            🚪 Sair\n'
        '    </button>\n'
        '  </div>\n'
        '</div>\n'
        '<script>\n'
        '(function(){\n'
        '  try {\n'
        '    var u = "";\n'
        '    var auth = JSON.parse(sessionStorage.getItem("dash_auth") || "{}");\n'
        '    u = auth.nome || auth.user || "";\n'
        '    if(!u) u = sessionStorage.getItem("tf_user") || "";\n'
        '    var el = document.getElementById("header-user-name");\n'
        '    if(el && u) el.innerHTML = "👤 " + u;\n'
        '  } catch(e) {}\n'
        '})();\n'
        '</script>'
    )
    
    m = re.search(pattern, html)
    if m:
        html = html[:m.start()] + btns + html[m.end():]
        log("[2] Botoes admin INJETADOS no Header")
    else:
        log("[2] AVISO: nao encontrou ancora do header-date para injecao no Header")
    return html

# 3. CAMPO INTERVALO
def inject_intervalo_field(html):
    if "wa-intervalo-input" in html:
        log("[3] Campo intervalo OK"); return html
    old = '<div id="wa-tpl-boxes">'
    new = (
        '<div style="margin-bottom:10px;display:flex;align-items:center;gap:8px">'
        '<label style="font-size:11px;color:#f59e0b;font-weight:600;white-space:nowrap">Intervalo:</label>'
        '<input id="wa-intervalo-input" class="wa-cfg-input" placeholder="Ex: Manha / Tarde / Noite" '
        'oninput="waUpdatePreview()" style="font-size:12px;padding:6px 10px;flex:1">'
        '</div>'
        '<div id="wa-tpl-boxes">'
    )
    if old in html:
        html = html.replace(old, new, 1); log("[3] Campo intervalo INJETADO")
    else:
        log("[3] AVISO wa-tpl-boxes nao encontrado")
    return html

# 4. LABEL {intervalo}
def inject_intervalo_label(html):
    if "{intervalo}" in html and "f59e0b" in html:
        log("[4] Label OK"); return html
    old = '<span style="color:#60a5fa">{remetente}</span>\n          </div>'
    new = '<span style="color:#60a5fa">{remetente}</span> <span style="color:#f59e0b">{intervalo}</span>\n          </div>'
    if old in html:
        html = html.replace(old, new, 1); log("[4] Label intervalo INJETADO")
    return html

# 5. PREVIEW intervalo
def inject_intervalo_preview(html):
    if "c.intervalo" in html:
        log("[5] Preview OK"); return html
    old = ".split('{{remetente}}').join(document.getElementById('wa-sender-name').value||'Remetente');"
    new = (
        ".split('{{remetente}}').join(document.getElementById('wa-sender-name').value||'Remetente')"
        ".split('{{intervalo}}').join(c.intervalo"
        "||(document.getElementById('wa-intervalo-input')"
        "&&document.getElementById('wa-intervalo-input').value)||'--');"
    )
    if old in html:
        html = html.replace(old, new, 1); log("[5] Preview intervalo INJETADO")
    else:
        log("[5] AVISO chain nao encontrada")
    return html

# 6. FILTRO CANCELADO
def inject_cancelado_filter(html):
    if "cancelamento-do-contrato" in html:
        log("[6] Filtro Cancelado OK"); return html
    old = '<option value="nao-atendido">Nao Atendeu</option>'
    new = '<option value="cancelamento-do-contrato">Cancelado</option>' + old
    if old in html:
        html = html.replace(old, new, 1); log("[6] Filtro Cancelado INJETADO")
    return html

# 6B. SHOWPAGE FUNCTION (garante que sempre existe e é robusta)
def inject_showpage(html):
    # Achar a função showPage original e substituí-la por nossa versão blindada com !important
    new_sp_js = (
        "function showPage(id, btn) {\n"
        "  console.log('Navegando para a aba:', id);\n"
        "  document.querySelectorAll('.page').forEach(function(p){\n"
        "    p.classList.remove('active');\n"
        "    p.style.setProperty('display', 'none', 'important');\n"
        "  });\n"
        "  document.querySelectorAll('.nav-btn').forEach(function(b){\n"
        "    b.classList.remove('active');\n"
        "  });\n"
        "  var el = document.getElementById(id);\n"
        "  if(el){\n"
        "    el.classList.add('active');\n"
        "    el.style.setProperty('display', 'block', 'important');\n"
        "  }\n"
        "  if(btn) btn.classList.add('active');\n"
        "  var evoW = document.getElementById('evo-chart-wrapper');\n"
        "  if(evoW) evoW.style.setProperty('display', (id==='visao-geral') ? 'block' : 'none', 'important');\n"
        "}"
    )

    # Regex para capturar a função showPage original (com arrow functions ou function expressions)
    pattern = r'function showPage\s*\(id,\s*btn\)\s*\{(?:[^{}]*(?:\{[^{}]*\})*[^{}]*)*\}'
    if re.search(pattern, html):
        html = re.sub(pattern, new_sp_js, html, count=1)
        log("[6B] showPage original substituída por versão blindada")
    else:
        # Se não achar a original, injetamos como script antes do body
        log("[6B] AVISO: showPage original não encontrada para substituição, injetando no fim")
        showpage_js = '<script>\n' + new_sp_js + '\n</script>'
        if '</body>' in html:
            html = html.replace('</body>', showpage_js + '\n</body>', 1)

    # Injetar script de inicialização APENAS se ainda não existe (previne duplicação)
    if 'Inicializando exibicao de abas' not in html:
        init_js = (
            "<script>\n"
            "document.addEventListener('DOMContentLoaded', function(){\n"
            "  console.log('Inicializando exibicao de abas...');\n"
            "  document.querySelectorAll('.page').forEach(function(p){\n"
            "    p.style.setProperty('display', 'none', 'important');\n"
            "  });\n"
            "  var vg = document.getElementById('visao-geral');\n"
            "  if(vg){ \n"
            "    vg.style.setProperty('display', 'block', 'important'); \n"
            "    vg.classList.add('active'); \n"
            "  }\n"
            "});\n"
            "</script>"
        )
        if '</body>' in html:
            html = html.replace('</body>', init_js + '\n</body>', 1)
            log("[6B] Script de inicialização de abas injetado")
    else:
        log("[6B] Script de inicialização já existe, pulando duplicação")

    return html




# 7. DROPDOWN MANUAL COMPLETO
def inject_full_dropdown(html):
    if "sem-retorno-supervisao" in html:
        log("[7] Dropdown completo OK"); return html
    vals = [
        ("","-- Alterar Status --"),("pendente","Pendente"),("confirmado","Confirmado"),
        ("nao-atendido","Nao Atendeu"),("reagendado","Reagendado"),("conveniente","Conveniente"),
        ("cancelamento-do-contrato","Cancelado"),("entregue-pos-servico","Entregue Pos"),
        ("entregue-d1","Entregue D-1"),("entregue-d0","Entregue D-0"),
        ("normalizado","Normalizado"),("resolvido","Resolvido"),("aberto-reparo","Aberto Reparo"),
        ("problema-na-rede","Problema na Rede"),("central","Central"),("agendado","Agendado"),
        ("suspenso-por-debito","Suspenso por Debito"),("numero-nao-pertence","Numero Nao Pertence"),
        ("area-de-risco","Area de Risco"),("nao-se-encontra","Nao se Encontra"),
        ("solicitou-upgrade","Solicitou Upgrade"),("sem-contato","Sem Contato"),
        ("sem-retorno-supervisao","Sem Retorno Supervisao"),
    ]
    opts = "".join('<option value="{}">{}</option>'.format(v,l) for v,l in vals)
    anchor = 'sel.innerHTML=\'<option value="">-- Alterar Status --</option><option value="pendente">Pendente</option>'
    if anchor in html:
        idx = html.find(anchor)
        end = html.find("';", idx)
        if end != -1:
            html = html[:idx] + "sel.innerHTML='" + opts + "'" + html[end+2:]
            log("[7] Dropdown SUBSTITUIDO")
        else:
            log("[7] AVISO fim innerHTML nao encontrado")
    else:
        log("[7] AVISO ancora nao encontrada")
    return html

# 8. ABA ESTOQUE
def inject_estoque(html):
    if "kpi-estoque-cards" in html:
        log("[8] Aba Estoque OK"); return html

    anchor = '<div class="page" id="estoque">'
    if anchor not in html:
        log("[8] AVISO div estoque nao encontrado"); return html

    css = (
        "<style>"
        ".estoque-tabs{display:flex;gap:8px;margin-bottom:24px}"
        ".estoque-tab{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-weight:600;transition:all .2s}"
        ".estoque-tab:hover{border-color:#7c3aed;color:#e8eaf6}"
        ".estoque-tab.active{background:#7c3aed;border-color:#7c3aed;color:#fff}"
        ".estoque-sub{display:none}.estoque-sub.active{display:block}"
        "#kpi-estoque-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-bottom:18px}"
        ".kpi-ec{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;font-size:11px;color:var(--muted)}"
        ".kpi-ec .num{font-size:22px;font-weight:700;color:#fff;display:block;margin-bottom:2px}"
        ".kpi-ec .mi{width:60px;text-align:center;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:4px;color:#fff;padding:3px 5px;font-size:11px;margin-top:6px;display:none}"
        ".kpi-ec .pb{height:6px;background:rgba(255,255,255,.05);border-radius:3px;margin-top:6px;overflow:hidden}"
        ".kpi-ec .pf{height:100%;background:linear-gradient(90deg,#22d3a0,#00e5ff);border-radius:3px;transition:width .8s}"
        "#tbl-tec{width:100%;border-collapse:collapse;font-size:12px}"
        "#tbl-tec th{background:#111520;color:#94a3b8;padding:8px 10px;text-align:center;border:1px solid #1c2237;position:sticky;top:0;z-index:2;white-space:nowrap}"
        "#tbl-tec th:first-child{text-align:left;position:sticky;left:0;z-index:3;background:#111520}"
        "#tbl-tec td{padding:7px 10px;border:1px solid #1a2035;text-align:center;color:#94a3b8}"
        "#tbl-tec td:first-child{text-align:left;font-weight:600;color:#e8eaf6;position:sticky;left:0;background:#0b0f1e;z-index:1}"
        "#tbl-tec td.val{color:#22d3a0;font-weight:700}"
        ".tw{overflow:auto;max-height:500px}"
        "</style>"
    )
    header_html = (
        "<div class='estoque-tabs'>"
        "<div class='estoque-tab active' onclick=\"showEstoqueSub('estoque-metas',this)\">Consumo e Metas</div>"
        "<div class='estoque-tab' onclick=\"showEstoqueSub('estoque-arquivos',this)\">Relatorios</div>"
        "</div>"
        "<div class='estoque-sub active' id='estoque-metas'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:16px'>"
        "<div class='section-title' style='margin:0'>Consumo Semanal</div>"
        "<div style='display:flex;gap:8px'>"
        "<button onclick='toggleEditMetas()' style='background:transparent;border:1px solid #7c3aed;color:#a78bfa;padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer'>Editar Metas</button>"
        "<button onclick='calcEstoque()' id='btn-est' style='background:transparent;border:1px solid #1c2237;color:#94a3b8;padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer'>Atualizar</button>"
        "<button onclick='exportEst()' style='background:transparent;border:1px solid #22d3a0;color:#22d3a0;padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer'>Exportar Excel</button>"
        "</div></div>"
        "<div id='kpi-estoque-cards'><div style='color:#64748b;font-size:13px;padding:20px'>Clique em Atualizar...</div></div>"
        "<div class='section-title' style='margin:16px 0 10px'>Consumo por Tecnico</div>"
        "<div class='tw'><table id='tbl-tec'><thead><tr><th>Tecnico</th></tr></thead><tbody></tbody></table></div>"
        "</div>"
        "<div class='estoque-sub' id='estoque-arquivos'>"
    )

    # JS sem aspas simples conflitantes — usa aspas duplas em todo lugar
    js = """<script>
var _ed={},_em=false;
function showEstoqueSub(id,btn){
  document.querySelectorAll(".estoque-tab").forEach(e=>e.classList.remove("active"));
  document.querySelectorAll(".estoque-sub").forEach(e=>e.classList.remove("active"));
  btn.classList.add("active");document.getElementById(id).classList.add("active");
  if(id==="estoque-metas"&&!Object.keys(_ed).length)calcEstoque();
}
function toggleEditMetas(){
  _em=!_em;
  document.querySelectorAll(".mi").forEach(e=>e.style.display=_em?"inline-block":"none");
}
async function calcEstoque(){
  var btn=document.getElementById("btn-est");if(btn)btn.innerHTML="...";
  if(!window.XLSX){await new Promise(r=>{var s=document.createElement("script");s.src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";s.onload=r;document.head.appendChild(s);});}
  _ed={};var td={},pA=[];
  for(var i=0;i<7;i++){
    var d=new Date();d.setDate(d.getDate()-i);
    var ds=("0"+d.getDate()).slice(-2)+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+d.getFullYear();
    pA.push(fetch("inventarios/inventario_"+ds+".xlsx").then(r=>r.ok?r.arrayBuffer():null).then(ab=>{
      if(!ab)return;
      var wb=XLSX.read(new Uint8Array(ab),{type:"array"});
      XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]).forEach(r=>{
        var sec=r["Secao"]||r["secao"]||"";
        if(sec==="Instalado"){
          var de=(r["Descricao"]||r["descricao"]||r["Tipo"]||"Outros").trim();
          var te=(r["Tecnico"]||r["tecnico"]||r["TECNICO"]||"?").trim();
          var q=parseFloat(r["Quantidade"]||r["quantidade"]||1)||1;
          _ed[de]=(_ed[de]||0)+q;if(!td[te])td[te]={};td[te][de]=(td[te][de]||0)+q;
        }
      });
    }).catch(e=>{}));
  }
  await Promise.all(pA);renderKpi();renderTec(td);if(btn)btn.innerHTML="Atualizar";
}
function renderKpi(){
  var m=JSON.parse(localStorage.getItem("dash_metas_v2")||"{}"),its=Object.keys(_ed).sort(),h="";
  if(!its.length){document.getElementById("kpi-estoque-cards").innerHTML="<div style=\\"color:#64748b;padding:20px\\">Sem dados.</div>";return;}
  its.forEach(it=>{
    var v=_ed[it]||0,mv=parseFloat(m[it])||0,p=mv?Math.min(100,v/mv*100):0,id="mi_"+it.replace(/[^a-z0-9]/gi,"_");
    h+="<div class=\\"kpi-ec\\"><span class=\\"num\\">"+v+"</span><div style=\\"font-size:11px;color:#94a3b8;margin-bottom:4px\\">"+it+"</div>"+(mv?"<div style=\\"font-size:10px;color:#64748b\\">Meta:"+mv+" ("+p.toFixed(0)+"%)</div>":"")+"<div class=\\"pb\\"><div class=\\"pf\\" style=\\"width:"+p+"%\\"></div></div><input type=\\"number\\" id=\\""+id+"\\" class=\\"mi\\" value=\\""+(m[it]||"")+"\\" placeholder=\\"Meta\\" onchange=\\"sm2('"+it+"','"+id+"')\\"></div>";
  });
  document.getElementById("kpi-estoque-cards").innerHTML=h;
  if(_em)document.querySelectorAll(".mi").forEach(e=>e.style.display="inline-block");
}
function sm2(it,id){var m=JSON.parse(localStorage.getItem("dash_metas_v2")||"{}");m[it]=document.getElementById(id).value;localStorage.setItem("dash_metas_v2",JSON.stringify(m));renderKpi();}
function renderTec(td){
  var ts=Object.keys(td).sort(),its=Object.keys(_ed).sort();
  document.querySelector("#tbl-tec thead tr").innerHTML="<th>Tecnico</th>"+its.map(i=>"<th>"+i+"</th>").join("");
  document.querySelector("#tbl-tec tbody").innerHTML=ts.map(t=>"<tr><td>"+t+"</td>"+its.map(i=>td[t][i]?"<td class=\\"val\\">"+td[t][i]+"</td>":"<td style=\\"color:#374151\\">-</td>").join("")+"</tr>").join("");
}
function exportEst(){window.location.href="inventarios/consolidado_inventarios.xlsx";}
var _osp=window.showPage;
window.showPage=function(p,b){if(_osp)_osp(p,b);if(p==="estoque"&&!Object.keys(_ed).length)calcEstoque();};
</script>"""

    parts = html.split(anchor)
    pre, rest = parts[0], parts[1]
    count, idx = 1, 0
    while count > 0 and idx < len(rest):
        t = rest.find("<", idx)
        if t == -1: break
        if rest.startswith("<div", t): count += 1
        elif rest.startswith("</div", t): count -= 1
        idx = t + 1
    idx -= 1

    new_html = pre + anchor + css + header_html + rest[:idx] + "  </div>\n" + rest[idx:]
    new_html = new_html.replace("</body>", js + "\n</body>", 1)
    log("[8] Aba Estoque INJETADA")
    return new_html

# 9. FIX JS QUOTES (garante que aspas em onclick inline não quebrem o JS)
def fix_js_quotes(html):
    # waFluxoCancelar('' + fl.id + '') → waFluxoCancelar(\x27' + fl.id + '\x27)
    bad = "waFluxoCancelar('' + fl.id + '')"
    good = "waFluxoCancelar(\\x27' + fl.id + '\\x27)"
    if bad in html:
        html = html.replace(bad, good)
        log("[9] Fix JS quotes: waFluxoCancelar CORRIGIDO")
    else:
        log("[9] Fix JS quotes OK (sem problemas detectados)")
    return html


# MAIN
if __name__ == "__main__":
    print("=" * 50)
    print("post_inject.py", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    if not os.path.exists(DASH):
        print("[ERRO] index.html nao encontrado"); sys.exit(1)
    backup(DASH)
    html = load(DASH)
    html = inject_login_guard(html)
    html = inject_admin_buttons(html)
    html = inject_intervalo_field(html)
    html = inject_intervalo_label(html)
    html = inject_intervalo_preview(html)
    html = inject_cancelado_filter(html)
    html = inject_showpage(html)
    html = inject_full_dropdown(html)
    html = inject_estoque(html)
    html = fix_js_quotes(html)
    save(DASH, html)
    print("")
    print("[DONE] Concluido! Tamanho:", os.path.getsize(DASH), "bytes")

