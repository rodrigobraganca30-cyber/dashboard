#!/usr/bin/env python3
"""Fix Excel handler no whatsapp_agenda_gen.py - adiciona onerror e fallback CDN"""
ARQUIVO = '/docker/dashboard/whatsapp_agenda_gen.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = r"""            var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
            sc.onload=function(){var r=new FileReader();r.onload=function(ev){var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))};r.readAsArrayBuffer(file)};
            document.head.appendChild(sc);"""

NEW = r"""            var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
            sc.onload=function(){var r=new FileReader();r.onload=function(ev){try{var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))}catch(e2){alert('Erro ao ler Excel: '+e2.message)}};r.onerror=function(){alert('Erro ao ler o arquivo.')};r.readAsArrayBuffer(file)};
            sc.onerror=function(){var s2=document.createElement('script');s2.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';s2.onload=sc.onload;s2.onerror=function(){alert('Erro ao carregar biblioteca Excel. Verifique sua conexão e recarregue a página.')};document.head.appendChild(s2)};
            document.head.appendChild(sc);"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] Fix aplicado no whatsapp_agenda_gen.py')
else:
    print('[ERRO] Ancora nao encontrada')
    # mostra o que tem no arquivo para debug
    import re
    m = re.search(r'sc\.src=.{0,100}xlsx', content)
    if m:
        print('[DIAG]', content[m.start()-50:m.start()+200])
