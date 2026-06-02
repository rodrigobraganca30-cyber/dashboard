"""
Fase 2: Injeta script dinamico no HTML que carrega dados de JSON.
Se o fetch funcionar -> dados frescos. Se falhar -> dados inline (fallback).
ZERO risco de quebra.
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# 1. Backup
print('[1/3] Backup...')
c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_fase2.html')
time.sleep(1)

# 2. Criar o script do patch no servidor
patch_code = r'''
import re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Verificar se o dynamic loader ja esta injetado
if 'dynamicDataLoader' in html:
    print('[!] Dynamic loader ja existe, pulando')
    exit(0)

# O script que carrega dados de JSON com fallback seguro
loader_js = """
<""" + """script id="dynamicDataLoader">
// === FASE 2: Dynamic Data Loader ===
// Carrega dados de JSONs. Se falhar, usa dados inline (fallback).
(function(){
  var _t = Date.now();
  var loaded = 0;
  var total = 2; // os.json + filtros.json

  function _done() {
    loaded++;
    if(loaded >= total) {
      // Status mapping: processar_dados.py usa sem acento, inline usa com acento
      var statusMap = {
        'Concluida': 'Conclu\\u00edda',
        'Nao Concluida': 'N\\u00e3o Conclu\\u00edda',
        'Cancelada': 'Cancelada',
        'Suspensa': 'Suspensa',
        'Pendente': 'Pendente'
      };
      // Remapear status dos dados do JSON para formato esperado pelo runFilter
      if(window._jsonDataLoaded) {
        rawOSData = rawOSData.map(function(d) {
          if(statusMap[d.status]) d.status = statusMap[d.status];
          return d;
        });
      }
      // Re-renderizar com dados frescos
      if(typeof runFilter === 'function') {
        try { runFilter(); } catch(e) { console.log('[DynLoader] runFilter error:', e); }
      }
      console.log('[DynLoader] Dados carregados de JSON em ' + (Date.now()-_t) + 'ms');
    }
  }

  // Carregar os.json
  fetch('data/os.json?t='+_t)
    .then(function(r) { if(!r.ok) throw 'HTTP '+r.status; return r.json(); })
    .then(function(data) {
      rawOSData = data;
      window._jsonDataLoaded = true;
      console.log('[DynLoader] os.json: ' + data.length + ' registros');
      _done();
    })
    .catch(function(e) {
      console.log('[DynLoader] os.json falhou (usando inline):', e);
      _done();
    });

  // Carregar filtros.json
  fetch('data/filtros.json?t='+_t)
    .then(function(r) { if(!r.ok) throw 'HTTP '+r.status; return r.json(); })
    .then(function(data) {
      filterLists = data;
      // Limpar dropdowns cacheados para recriar com novos dados
      document.querySelectorAll('.filter-dropdown').forEach(function(d) { d.innerHTML = ''; });
      console.log('[DynLoader] filtros.json: OK');
      _done();
    })
    .catch(function(e) {
      console.log('[DynLoader] filtros.json falhou (usando inline):', e);
      _done();
    });

  // Carregar kpis.json para atualizar recordes
  fetch('data/kpis.json?t='+_t)
    .then(function(r) { if(!r.ok) throw 'HTTP '+r.status; return r.json(); })
    .then(function(kpis) {
      if(kpis.recordes) {
        var r = kpis.recordes;
        var updates = {
          'top-tec-taxa': r.tec_melhor_taxa ? r.tec_melhor_taxa.taxa+'%' : null,
          'top-tec-nome': r.tec_melhor_taxa ? r.tec_melhor_taxa.nome : null,
          'top-tec-prod': r.tec_mais_prod ? r.tec_mais_prod.total : null,
          'top-tec-prod-nome': r.tec_mais_prod ? r.tec_mais_prod.nome : null,
          'bad-tec-taxa': r.tec_pior_taxa ? r.tec_pior_taxa.taxa+'%' : null,
          'bad-tec-nome': r.tec_pior_taxa ? r.tec_pior_taxa.nome : null,
          'top-cit-taxa': r.cit_melhor_taxa ? r.cit_melhor_taxa.taxa+'%' : null,
          'top-cit-nome': r.cit_melhor_taxa ? r.cit_melhor_taxa.nome : null,
          'top-cit-vol': r.cit_mais_vol ? r.cit_mais_vol.total : null,
          'top-cit-vol-nome': r.cit_mais_vol ? r.cit_mais_vol.nome : null,
          'bad-cit-taxa': r.cit_pior_taxa ? r.cit_pior_taxa.taxa+'%' : null,
          'bad-cit-nome': r.cit_pior_taxa ? r.cit_pior_taxa.nome : null,
          'evo-pico-vol': r.pico_dia ? r.pico_dia.total : null,
          'evo-pico-data': r.pico_dia ? r.pico_dia.data : null,
          'evo-top-taxa': r.melhor_dia ? r.melhor_dia.taxa+'%' : null,
          'evo-top-data': r.melhor_dia ? r.melhor_dia.data : null,
          'evo-bad-taxa': r.pior_dia ? r.pior_dia.taxa+'%' : null,
          'evo-bad-data': r.pior_dia ? r.pior_dia.data : null,
          'evo-avg-vol': r.media_diaria ? r.media_diaria.toFixed(1) : null
        };
        for(var id in updates) {
          if(updates[id] !== null) {
            var el = document.getElementById(id);
            if(el) el.textContent = updates[id];
          }
        }
      }
      console.log('[DynLoader] kpis.json: OK');
    })
    .catch(function(e) { console.log('[DynLoader] kpis.json falhou:', e); });

})();
</scr""" + """ipt>
"""

# Inserir antes de </body>
body_end = html.rfind('</body>')
if body_end > 0:
    html = html[:body_end] + loader_js + '\n' + html[body_end:]
    print('[+] Dynamic Data Loader inserido')
else:
    print('[!] </body> nao encontrado')
    exit(1)

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo (%d bytes)' % len(html))
'''

print('[2/3] Aplicando Fase 2...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_fase2.py', 'w') as f:
    f.write(patch_code)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_fase2.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

# 3. Verificacao
print('\n[3/3] Verificacao...')
i, o, e = c.exec_command("grep -c 'dynamicDataLoader' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'  dynamicDataLoader: {o.read().decode().strip()} refs')

i, o, e = c.exec_command("ls -la /docker/dashboard/html/data/")
time.sleep(1)
print(f'  data/:\n{o.read().decode().strip()}')

c.close()
print('\nFase 2 aplicada! Ctrl+Shift+R para testar.')
print('Abra o console do navegador (F12) e veja as mensagens [DynLoader]')
