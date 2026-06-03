import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

if 'dynamicKPISubs' in html:
    print('[!] KPI subs patch ja existe')
    exit(0)

# Patch que atualiza os subtitulos de porcentagem apos o runFilter rodar
fix_js = """<script id="dynamicKPISubs">
// Corrige subtitulos % do total nos KPI cards da Visao Geral
(function(){
  var _origRunFilter = window.runFilter;
  if(!_origRunFilter) return;

  window.runFilter = function() {
    _origRunFilter.apply(this, arguments);

    // Pegar os valores atualizados
    var vBlue = document.querySelector('.kpi-value.blue');
    var vRed = document.querySelector('.kpi-value.red');
    var vYellow = document.querySelector('.kpi-value.yellow');
    var vWhites = document.querySelectorAll('.kpi-value.white');

    var total = vBlue ? parseInt(vBlue.textContent) || 0 : 0;
    if(total === 0) return;

    // Canceladas - sub
    if(vRed) {
      var val = parseInt(vRed.textContent) || 0;
      var pct = (val / total * 100).toFixed(1);
      var sub = vRed.parentElement.querySelector('.kpi-sub');
      if(sub) sub.textContent = pct + '% do total';
    }
    // Nao Concluidas - sub
    if(vYellow) {
      var val = parseInt(vYellow.textContent) || 0;
      var pct = (val / total * 100).toFixed(1);
      var sub = vYellow.parentElement.querySelector('.kpi-sub');
      if(sub) sub.textContent = pct + '% do total';
    }
    // Suspensas - sub
    if(vWhites.length >= 1) {
      var val = parseInt(vWhites[0].textContent) || 0;
      var pct = (val / total * 100).toFixed(1);
      var sub = vWhites[0].parentElement.querySelector('.kpi-sub');
      if(sub) sub.textContent = pct + '% do total';
    }
    // Pendentes - sub
    if(vWhites.length >= 2) {
      var val = parseInt(vWhites[1].textContent) || 0;
      var pct = (val / total * 100).toFixed(1);
      var sub = vWhites[1].parentElement.querySelector('.kpi-sub');
      if(sub) sub.textContent = pct + '% do total';
    }
    // Total - sub (periodo)
    if(vBlue) {
      var sub = vBlue.parentElement.querySelector('.kpi-sub');
      if(sub) {
        // Pegar range de datas do rawOSData
        var dates = rawOSData.map(function(d){return d.date;}).filter(function(d){return d!=='--';});
        if(dates.length > 0) {
          sub.textContent = dates[0] + ' a ' + dates[dates.length-1];
        }
      }
    }
  };

  // Executar agora para corrigir valores ja exibidos
  setTimeout(function(){ if(typeof runFilter === 'function') runFilter(); }, 500);
  console.log('[DynKPISubs] Subtitulos de % serao atualizados');
})();
</""" + """script>
"""

body_end = html.rfind('</body>')
html = html[:body_end] + fix_js + '\n' + html[body_end:]

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] KPI subs patch aplicado')
'''

print('Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_kpi_subs.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_kpi_subs.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar.')
