#!/usr/bin/env python3
ARQUIVO = '/docker/whatsapp-agenda/frontend/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """    loadXLSX(() => {
      const r = new FileReader();
      r.onload = ev => {
        const wb = XLSX.read(new Uint8Array(ev.target.result), { type:'array' });
        const csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
        processCSV(csv);
      };
      r.readAsArrayBuffer(file);
    });"""

NEW = """    loadXLSX(() => {
      if (!window.XLSX) {
        alert('Erro: biblioteca Excel não carregou. Verifique sua conexão e tente novamente.');
        return;
      }
      const r = new FileReader();
      r.onload = ev => {
        try {
          const wb = XLSX.read(new Uint8Array(ev.target.result), { type:'array' });
          const csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
          processCSV(csv);
        } catch(err) {
          alert('Erro ao ler o Excel: ' + err.message);
        }
      };
      r.onerror = () => alert('Erro ao ler o arquivo.');
      r.readAsArrayBuffer(file);
    });"""

OLD2 = """      if (window.XLSX) return cb();
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      script.onload = cb;
      document.head.appendChild(script);"""

NEW2 = """      if (window.XLSX) return cb();
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      script.onload = cb;
      script.onerror = () => {
        // fallback para segundo CDN
        const s2 = document.createElement('script');
        s2.src = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
        s2.onload = cb;
        s2.onerror = () => { alert('Erro ao carregar biblioteca Excel. Verifique sua conexão.'); };
        document.head.appendChild(s2);
      };
      document.head.appendChild(script);"""

changes = 0
if OLD in content:
    content = content.replace(OLD, NEW, 1)
    changes += 1
    print('[OK] Handler de erro Excel corrigido')
else:
    print('[AVISO] Ancora 1 nao encontrada')

if OLD2 in content:
    content = content.replace(OLD2, NEW2, 1)
    changes += 1
    print('[OK] Fallback CDN adicionado')
else:
    print('[AVISO] Ancora 2 nao encontrada')

if changes > 0:
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[OK] {changes} correcoes salvas em {ARQUIVO}')
else:
    print('[ERRO] Nenhuma correcao aplicada')
