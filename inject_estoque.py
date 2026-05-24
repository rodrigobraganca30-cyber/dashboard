#!/usr/bin/env python3
"""Injeta a aba de Estoque enhanced com download table dinâmica.
Reconstroi a tabela de inventarios a partir dos arquivos reais no servidor.
"""
import os, shutil, datetime, glob

INDEX = '/docker/dashboard/html/index.html'
INV_DIR = '/docker/dashboard/html/inventarios'

with open(INDEX, 'r', encoding='utf-8') as f:
    html = f.read()

print('[*] Injetando/atualizando Estoque enhanced...')

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(INDEX, INDEX + '.bak.pre_inject.' + ts)

# --- Gerar tabela de downloads dinamicamente ---
inv_files = sorted(glob.glob(os.path.join(INV_DIR, 'inventario_*.xlsx')), reverse=True)
download_rows = ""
for inv in inv_files:
    nome = os.path.basename(inv)
    # Extract date from filename: inventario_DD-MM-YYYY.xlsx
    date_part = nome.replace('inventario_', '').replace('.xlsx', '')
    size_kb = os.path.getsize(inv) // 1024
    download_rows += f'''<tr><td style="font-weight:700;color:white;font-size:14px;"><i class="far fa-calendar-alt" style="color:var(--muted);margin-right:8px;"></i>{date_part}</td><td><span class="badge" style="background:rgba(255,255,255,0.05)">{size_kb} KB</span></td><td><a href="inventarios/{nome}" download="{nome}" class="estoque-btn"><i class="fas fa-file-excel"></i> Baixar Planilha</a></td></tr>\n'''

# --- HTML do estoque enhanced ---
ESTOQUE_HTML = f'''<div class="page" id="estoque"><style>.estoque-tabs{{display:flex;gap:8px;margin-bottom:24px}}.estoque-tab{{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-weight:600;transition:all .2s}}.estoque-tab:hover{{border-color:#7c3aed;color:#e8eaf6}}.estoque-tab.active{{background:#7c3aed;border-color:#7c3aed;color:#fff}}.estoque-sub{{display:none}}.estoque-sub.active{{display:block}}#kpi-estoque-cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:6px;margin-bottom:18px}}.kpi-ec{{background:#0b0f1a;border:1px solid #1a2035;border-radius:6px;padding:10px 12px 0 12px;display:flex;flex-direction:column;min-height:82px;overflow:hidden;position:relative}}.kpi-ec .num{{font-size:28px;font-weight:800;color:#00e5ff;font-family:monospace;line-height:1;display:block;margin-bottom:4px;order:2}}.kpi-ec .mi{{width:55px;text-align:center;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:4px;color:#fff;padding:2px 4px;font-size:11px;display:none;order:5}}.kpi-ec .pb{{height:3px;background:rgba(255,255,255,.04);margin:auto -12px 0 -12px;flex-shrink:0;order:4}}.kpi-ec .pf{{height:100%;background:linear-gradient(90deg,#22d3a0,#00e5ff);transition:width .8s}}.kpi-ec>div[style*="94a3b8"]{{font-size:10px!important;color:#94a3b8!important;font-weight:600;letter-spacing:.4px;text-transform:uppercase;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;order:1;margin-bottom:3px}}.kpi-ec>div[style*="64748b"]{{font-size:11px!important;color:#475569!important;order:3;margin-bottom:4px}}#tbl-tec{{width:100%;border-collapse:collapse;font-size:12px}}#tbl-tec th{{background:#111520;color:#94a3b8;padding:8px 10px;text-align:center;border:1px solid #1c2237;position:sticky;top:0;z-index:2;white-space:nowrap}}#tbl-tec th:first-child{{text-align:left;position:sticky;left:0;z-index:3;background:#111520}}#tbl-tec td{{padding:7px 10px;border:1px solid #1a2035;text-align:center;color:#94a3b8}}#tbl-tec td:first-child{{text-align:left;font-weight:600;color:#e8eaf6;position:sticky;left:0;background:#0a0d14;z-index:1;white-space:nowrap}}#tbl-tec td.val{{color:#00e5ff;font-weight:700}}</style>
  <div class="estoque-tabs">
    <div class="estoque-tab active" onclick="showEstoqueSub('estoque-metas',this)">Consumo e Metas</div>
    <div class="estoque-tab" onclick="showEstoqueSub('estoque-relatorios',this)">Relat&oacute;rios</div>
  </div>
  <div class="estoque-sub active" id="estoque-metas">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
      <button id="btn-est" onclick="calcEstoque()" style="background:#7c3aed;color:#fff;border:none;border-radius:6px;padding:8px 18px;font-weight:700;cursor:pointer">Atualizar</button>
      <button onclick="toggleEditMetas()" style="background:rgba(255,255,255,.06);color:#94a3b8;border:1px solid #1c2237;border-radius:6px;padding:8px 14px;font-size:12px;cursor:pointer">&#9998; Editar Metas</button>
      <button onclick="exportEst()" style="background:rgba(255,255,255,.06);color:#94a3b8;border:1px solid #1c2237;border-radius:6px;padding:8px 14px;font-size:12px;cursor:pointer">&#128229; Exportar</button>
    </div>
    <div id="kpi-estoque-cards"><div style="color:#64748b;padding:20px">Clique em "Atualizar" para carregar os dados de consumo semanal...</div></div>
    <div class="section-title" style="margin-top:24px">Consumo por T&eacute;cnico</div>
    <div style="overflow:auto;max-height:500px;border:1px solid #1a2035;border-radius:8px;">
      <table id="tbl-tec"><thead><tr><th>Tecnico</th></tr></thead><tbody></tbody></table>
    </div>
  </div>
  <div class="estoque-sub" id="estoque-relatorios">
    <div class="kpi-card blue" style="margin-bottom:24px;padding:20px;">
      <div class="kpi-label">BASE DE INVENT&Aacute;RIO</div>
      <div class="kpi-value blue">{len(inv_files)}</div>
      <div class="kpi-sub">relat&oacute;rios di&aacute;rios salvos no servidor</div>
    </div>
    <div class="section-title">DOWNLOAD DE INVENT&Aacute;RIOS</div>
    <fieldset style="border:1px solid var(--border);border-radius:12px;padding:16px 24px;">
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr><th style="text-align:left;padding:10px;color:var(--muted);font-size:11px;">DATA DO RELAT&Oacute;RIO</th><th style="text-align:left;padding:10px;color:var(--muted);font-size:11px;">TAMANHO ESTIMADO</th><th style="text-align:left;padding:10px;color:var(--muted);font-size:11px;">A&Ccedil;&Atilde;O</th></tr></thead>
      <tbody>
{download_rows}
      </tbody>
    </table>
    </fieldset>
  </div>
</div>
'''

# --- JS do estoque enhanced ---
ESTOQUE_JS = '''<script>
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
  if(!its.length){document.getElementById("kpi-estoque-cards").innerHTML="<div style=\\"color:#64748b;padding:20px\\">Sem dados de inventario nos ultimos 7 dias.</div>";return;}
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
function exportEst(){
  if(!window.XLSX)return;
  var rs=[...[...document.querySelectorAll("#tbl-tec tbody tr")].map(r=>[...r.querySelectorAll("td")].map(c=>c.textContent))];
  var hs=[...[...document.querySelectorAll("#tbl-tec thead th")].map(c=>c.textContent)];
  var wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet([hs,...rs]),"Consumo");
  XLSX.writeFile(wb,"consumo_semanal.xlsx");
}
var _ed={},_em=false;
var _osp=window.showPage;
window.showPage=function(p,b){if(_osp)_osp(p,b);if(p==="estoque"&&!Object.keys(_ed).length)calcEstoque();};
</script>
'''

# --- Substituir o bloco id="estoque" ---
START = '<div class="page" id="estoque">'
idx_s = html.find(START)
if idx_s == -1:
    print('[ERRO] div estoque nao encontrado')
    exit(1)

count = 1
idx = idx_s + len(START)
while count > 0 and idx < len(html):
    nxt_o = html.find('<div', idx)
    nxt_c = html.find('</div', idx)
    if nxt_o != -1 and (nxt_c == -1 or nxt_o < nxt_c):
        count += 1; idx = nxt_o + 4
    elif nxt_c != -1:
        count -= 1; idx = nxt_c + 6
    else: break

html = html[:idx_s] + ESTOQUE_HTML + html[idx:]

# --- Remover JS antigo se existir ---
for marker in ['async function calcEstoque', 'function calcEstoque']:
    pos = html.find(marker)
    if pos != -1:
        script_open = html.rfind('<script>', 0, pos)
        script_close = html.find('</script>', pos)
        if script_open != -1 and script_close != -1:
            html = html[:script_open] + html[script_close + len('</script>'):]
            print('  Removido bloco JS antigo')
            break

# Inserir JS antes de </body>
html = html.replace('</body>', ESTOQUE_JS + '\n</body>', 1)

with open(INDEX, 'w', encoding='utf-8') as f:
    f.write(html)

print('[OK] Estoque enhanced injetado!')
print(f'  Inventarios: {len(inv_files)} arquivos')
print(f'  Tamanho: {os.path.getsize(INDEX):,} bytes')
with open(INDEX, 'r', encoding='utf-8') as f: chk = f.read()
print(f'  calcEstoque: {"OK" if "async function calcEstoque(" in chk else "ERRO"}')
print(f'  kpi-cards: {"OK" if "kpi-estoque-cards" in chk else "ERRO"}')
print(f'  download table: {"OK" if "Baixar Planilha" in chk else "ERRO"}')
