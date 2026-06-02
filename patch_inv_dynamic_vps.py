# -*- coding: utf-8 -*-
"""Patch VPS: substitui tabela estatica de inventario por JS dinamico"""
import re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

inv_rows = re.findall(r'<tr><td style="font-weight:700;color:white;font-size:14px;">.*?inventario_\d{2}-\d{2}-\d{4}\.xlsx.*?</tr>\n?', html)

if not inv_rows:
    print('[!] Nenhuma linha estatica encontrada')
    exit(0)

print('Encontradas %d linhas estaticas' % len(inv_rows))

for row in inv_rows:
    html = html.replace(row, '')

# Encontrar a tabela e inserir tbody dinamico
header_idx = html.find('DATA DO RELAT')
if header_idx < 0:
    header_idx = html.find('TAMANHO ESTIMADO')

if header_idx > 0:
    table_end = html.find('</table>', header_idx)
    if table_end > 0:
        tbody_start = html.rfind('<tbody', header_idx, table_end)
        if tbody_start > 0:
            tbody_end = html.find('</tbody>', tbody_start)
            if tbody_end > 0:
                old_tbody = html[tbody_start:tbody_end+8]
                html = html.replace(old_tbody, '<tbody id="inv-tbody-dynamic"></tbody>')
                print('[+] tbody substituido')
        else:
            html = html[:table_end] + '<tbody id="inv-tbody-dynamic"></tbody>\n' + html[table_end:]
            print('[+] tbody inserido')

# JS dinamico
inv_js = ('<' + 'script>\n'
    '(function(){\n'
    '  fetch("inventarios/list.json?t="+Date.now())\n'
    '    .then(function(r){return r.json()})\n'
    '    .then(function(items){\n'
    '      var tbody=document.getElementById("inv-tbody-dynamic");\n'
    '      if(!tbody)return;\n'
    '      var countEls=document.querySelectorAll("div");\n'
    '      for(var i=0;i<countEls.length;i++){\n'
    '        if(countEls[i].textContent.trim().match(/^\\d+$/) && countEls[i].nextElementSibling && countEls[i].nextElementSibling.textContent.indexOf("relat")>=0){\n'
    '          countEls[i].textContent=items.length;\n'
    '          break;\n'
    '        }\n'
    '      }\n'
    '      var h="";\n'
    '      items.forEach(function(inv){\n'
    '        h+="<tr><td style=\\"font-weight:700;color:white;font-size:14px;\\"><i class=\\"far fa-calendar-alt\\" style=\\"color:var(--muted);margin-right:8px;\\"></i>"+inv.date+"</td>";\n'
    '        h+="<td><span class=\\"badge\\" style=\\"background:rgba(255,255,255,0.05)\\">"+inv.size_kb+" KB</span></td>";\n'
    '        h+="<td><a href=\\"inventarios/"+inv.file+"\\" download=\\""+inv.file+"\\" class=\\"estoque-btn\\"><i class=\\"fas fa-file-excel\\"></i> Baixar Planilha</a></td></tr>";\n'
    '      });\n'
    '      tbody.innerHTML=h;\n'
    '    })\n'
    '    .catch(function(e){console.log("Inv list error:",e)});\n'
    '})();\n'
    '</' + 'script>\n')

body_end = html.rfind('</body>')
if body_end > 0:
    html = html[:body_end] + inv_js + html[body_end:]
    print('[+] Script dinamico inserido')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo (%d bytes)' % len(html))
