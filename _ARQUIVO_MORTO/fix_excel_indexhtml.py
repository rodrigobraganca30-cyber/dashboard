#!/usr/bin/env python3
"""Fix Excel handler diretamente no index.html gerado"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = "var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';\n            sc.onload=function(){var r=new FileReader();r.onload=function(ev){var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))};r.readAsArrayBuffer(file)};\n            document.head.appendChild(sc);"

NEW = "var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';\n            sc.onload=function(){var r=new FileReader();r.onload=function(ev){try{var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))}catch(e2){alert('Erro ao ler Excel: '+e2.message)}};r.onerror=function(){alert('Erro ao ler o arquivo.')};r.readAsArrayBuffer(file)};\n            sc.onerror=function(){var s2=document.createElement('script');s2.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';s2.onload=sc.onload;s2.onerror=function(){alert('Erro ao carregar biblioteca Excel. Recarregue a pagina.')};document.head.appendChild(s2)};\n            document.head.appendChild(sc);"

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] Fix aplicado no index.html')
else:
    import re
    m = re.search(r"sc\.src='https://cdnjs.*xlsx", content)
    if m:
        print('[DIAG encontrado]:', repr(content[m.start():m.start()+300]))
    else:
        print('[ERRO] Bloco nao encontrado no index.html')
