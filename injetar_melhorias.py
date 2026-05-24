#!/usr/bin/env python3
"""
injetar_melhorias.py - Preserva todas as melhorias aplicadas em 15/05/2026.
Executar APOS gerar_dashboard_v2.py e demais injetores.
"""
import sys, os, shutil, datetime, re

DASH = "/docker/dashboard/html/index.html"

def log(msg): print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

if not os.path.exists(DASH):
    log(f"ERRO: {DASH} nao encontrado"); sys.exit(1)

with open(DASH, "r", encoding="utf-8") as f:
    html = f.read()

bak = DASH + ".bak.melhorias_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(DASH, bak)
log(f"Backup: {bak}")
changes = 0

# 1. TITULO DO CHAT = TELEFONE
OLD1 = "document.getElementById('wa-chat-title').textContent=nome;"
NEW1 = "document.getElementById('wa-chat-title').textContent=phone;"
if OLD1 in html:
    html = html.replace(OLD1, NEW1, 1)
    log("OK [1] Chat title: nome -> telefone")
    changes += 1
elif NEW1 in html:
    log("OK [1] Chat title ja usa telefone")
else:
    log("AVISO [1] Linha do chat title nao encontrada")

# 2. SEPARADORES DE DATA NO CHAT
OLD2 = "document.getElementById('wa-chat-msgs').innerHTML=msgs.map(function(m){"
NEW2_MARKER = "var html='',lastDay='';"
if OLD2 in html:
    start = html.find(OLD2)
    end_marker = "box.scrollTop=box.scrollHeight;"
    end = html.find(end_marker, start)
    if end != -1:
        end = html.find("\n", end) + 1
        html = html[:start] + (
            "var html='',lastDay='';\n"
            "      msgs.forEach(function(m){\n"
            "        var d=new Date(m.ts);\n"
            "        var today=new Date();today.setHours(0,0,0,0);\n"
            "        var yesterday=new Date(today);yesterday.setDate(yesterday.getDate()-1);\n"
            "        var msgDay=new Date(d);msgDay.setHours(0,0,0,0);\n"
            "        var dayKey=msgDay.toDateString();\n"
            "        if(dayKey!==lastDay){\n"
            "          var lbl;\n"
            "          if(msgDay.getTime()===today.getTime())lbl='Hoje';\n"
            "          else if(msgDay.getTime()===yesterday.getTime())lbl='Ontem';\n"
            "          else lbl=d.toLocaleDateString('pt-BR',{day:'2-digit',month:'long',year:'numeric'});\n"
            "          html+='<div style=\"text-align:center;margin:12px 0 8px\"><span style=\"background:#1c2237;color:#64748b;font-size:11px;padding:3px 12px;border-radius:12px;border:1px solid #2d3748\">'+lbl+'</span></div>';\n"
            "          lastDay=dayKey;\n"
            "        }\n"
            "        var cls=m.from==='me'?'me':'client';\n"
            "        var t=d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});\n"
            "        html+='<div class=\"wa-msg '+cls+'\">'+m.text+'<div style=\"font-size:9px;opacity:0.7;margin-top:2px;text-align:right\">'+t+'</div></div>';\n"
            "      });\n"
            "      document.getElementById('wa-chat-msgs').innerHTML=html;\n"
            "      var box=document.getElementById('wa-chat-msgs');\n"
            "      box.scrollTop=box.scrollHeight;\n"
        ) + html[end:]
        log("OK [2] Separadores de data no chat aplicados")
        changes += 1
elif NEW2_MARKER in html:
    log("OK [2] Separadores de data ja existem")
else:
    log("AVISO [2] Bloco msgs.map nao encontrado")

# 3. EXPORT CSV COMPLETO (11 colunas)
OLD3 = "  function waExportCSV(){"
NEW3 = """  function waExportCSV(){
    function esc(v){ return (v||'').toString().replace(/"/g,'""'); }
    var fase_labels={d1:'D-1 (Amanha)',d0:'D-0 (Hoje)',pos:'Pos-servico'};
    var rows=[['Nome','Telefone','Data','Intervalo','Endereco','Cidade','Tipo de Atividade','Fase','Status OFS','Status Atual','Observacoes']];
    waClients.forEach(function(c){
      var obs=(waTratativas[c.id]&&waTratativas[c.id].obs)||'';
      var fase=fase_labels[waGetFase(c)]||waGetFase(c);
      rows.push([esc(c.nome),esc(c.phone),esc(c.data),esc(c.intervalo),esc(c.endereco),esc(c.cidade),esc(c.tipo),fase,esc(c.statusOfs),waGetStatus(c).replace(/[^\\w\\s\\-]/g,''),esc(obs)]);
    });
    var csv='\\ufeff'+rows.map(function(r){return r.map(function(v){return '\\"'+v+'\\"';}).join(',');}).join('\\n');
    var blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});
    if(navigator.msSaveBlob){navigator.msSaveBlob(blob,'agenda.csv');return;}
    var link=document.createElement('a');link.href=URL.createObjectURL(blob);
    link.setAttribute('download','agenda.csv');link.style.visibility='hidden';
    document.body.appendChild(link);link.click();document.body.removeChild(link);
  }"""

if OLD3 in html:
    start = html.find(OLD3)
    end = html.find("\n  }\n", start)
    if end == -1: end = html.find("\n  }\r\n", start)
    end += 5
    if "fase_labels" not in html[start:end]:
        html = html[:start] + NEW3 + html[end:]
        log("OK [3] Export CSV completo aplicado")
        changes += 1
    else:
        log("OK [3] Export CSV completo ja existe")
else:
    log("AVISO [3] waExportCSV nao encontrada")

# 4. CORRECAO REGEX QUEBRADA
lines = html.split('\n')
new_lines = []
regex_fixed = 0
i = 0
while i < len(lines):
    line = lines[i]
    if line.rstrip('\r').endswith("replace(/") and i+1 < len(lines):
        nxt = lines[i+1].lstrip()
        if nxt.startswith("/g,") or nxt.startswith("/gi,"):
            new_lines.append(line.rstrip('\r') + r"\n" + lines[i+1])
            i += 2; regex_fixed += 1; continue
    new_lines.append(line); i += 1
if regex_fixed:
    html = '\n'.join(new_lines)
    log(f"OK [4] {regex_fixed} regex(es) quebrada(s) corrigida(s)")
    changes += 1
else:
    log("OK [4] Sem regex quebrada")

# 5. REMOVER JS DUPLICADO
count_func = html.count("function waLoadMetaTemplates")
if count_func >= 2:
    lines2 = html.split('\n')
    func_lines = [i for i, l in enumerate(lines2) if "function waLoadMetaTemplates" in l]
    second = func_lines[1]
    block_start = max(0, second - 3)
    block_end = None
    for i in range(second, min(second+120, len(lines2))):
        if "FIM META TEMPLATE SELECTOR" in lines2[i]:
            block_end = i + 1; break
    if block_end:
        lines2 = lines2[:block_start] + lines2[block_end:]
        html = '\n'.join(lines2)
        log(f"OK [5] JS duplicado removido")
        changes += 1
else:
    log("OK [5] Sem JS duplicado")

# SALVAR
if changes > 0:
    with open(DASH, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"PRONTO: {changes} melhoria(s) | {os.path.getsize(DASH):,} bytes")
else:
    log("Dashboard ja atualizado - nenhuma alteracao necessaria")
