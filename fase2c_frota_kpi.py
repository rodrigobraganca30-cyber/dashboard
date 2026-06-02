"""
Adiciona atualização dos KPI cards da Frota ao dynamic loader.
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

if 'dynamicFrotaKPI' in html:
    print('[!] Frota KPI loader ja existe')
    exit(0)

kpi_js = '<' + 'script id="dynamicFrotaKPI">\n'
kpi_js += r"""
(function(){
  fetch('data/frota.json?t='+Date.now())
    .then(function(r){if(!r.ok) throw r.status; return r.json();})
    .then(function(f){
      var k = f.kpis || {};
      var comb = f.combustivel || [];
      var nTec = comb.length;

      // Combustivel KPIs - encontrar cards dentro de frota-comb
      var combDiv = document.getElementById('frota-comb');
      if(!combDiv) return;
      var cards = combDiv.querySelectorAll('.kpi-card, [style*="border-radius"]');

      // Abordagem: encontrar os valores grandes (kpi-value ou font-size grande)
      var bigNums = combDiv.querySelectorAll('[style*="font-size"]');
      var kpiVals = [];
      bigNums.forEach(function(el){
        var fs = el.style.fontSize || window.getComputedStyle(el).fontSize;
        if(fs && (parseInt(fs) >= 28 || fs.indexOf('48') >= 0 || fs.indexOf('36') >= 0 || fs.indexOf('32') >= 0)) {
          kpiVals.push(el);
        }
      });

      // Se nao encontrou por style, tenta por class
      if(kpiVals.length === 0) {
        kpiVals = Array.from(combDiv.querySelectorAll('.kpi-value, .stat-value'));
      }

      // Atualizar: Total Gasto, Projecao, Litros, KM
      var totalGasto = k.combustivel_total || 0;
      var litros = k.litros_total || 0;
      var km = k.km_total || 0;
      var diaAtual = new Date().getDate();
      var projecao = diaAtual > 0 ? (totalGasto / diaAtual) * 30 : 0;
      var mediaLitros = nTec > 0 ? Math.round(litros / nTec) : 0;
      var mediaKm = nTec > 0 ? Math.round(km / nTec) : 0;

      // Tentar atualizar por texto - procurar nos containers
      var allText = combDiv.querySelectorAll('div, span');
      allText.forEach(function(el){
        var t = el.textContent.trim();
        // Total Gasto valor
        if(t.match(/^R\$\s*[\d,.]+$/) && el.style.fontSize && parseInt(el.style.fontSize) >= 28) {
          // Verificar se e o total gasto ou projecao
          var parent = el.parentElement;
          var label = parent ? parent.textContent : '';
          if(label.indexOf('TOTAL GASTO') >= 0 || label.indexOf('total gasto') >= 0) {
            el.textContent = 'R$\n' + totalGasto.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
          } else if(label.indexOf('PROJE') >= 0 || label.indexOf('proje') >= 0) {
            el.textContent = 'R$\n' + projecao.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
          }
        }
      });

      // Abordagem mais simples: encontrar por conteudo nos cards
      var cardDivs = combDiv.querySelectorAll('div');
      for(var i=0; i<cardDivs.length; i++){
        var txt = cardDivs[i].textContent;
        var children = cardDivs[i].children;
        
        // Card TOTAL GASTO
        if(txt.indexOf('TOTAL GASTO') >= 0 && children.length > 0) {
          for(var j=0; j<children.length; j++){
            if(children[j].textContent.indexOf('R$') >= 0 && children[j].textContent.match(/[\d,.]/) && children[j].style.fontSize) {
              children[j].innerHTML = 'R$<br>' + totalGasto.toLocaleString('pt-BR', {minimumFractionDigits:2});
            }
            if(children[j].textContent.match(/\d+\s*t[eé]cnicos/i)) {
              children[j].textContent = nTec + ' t\u00e9cnicos';
            }
          }
        }
        // Card PROJEÇÃO
        if(txt.indexOf('PROJE') >= 0 && txt.indexOf('30') >= 0 && children.length > 0) {
          for(var j=0; j<children.length; j++){
            if(children[j].textContent.indexOf('R$') >= 0 && children[j].textContent.match(/[\d,.]/) && children[j].style.fontSize) {
              children[j].innerHTML = 'R$<br>' + projecao.toLocaleString('pt-BR', {minimumFractionDigits:2});
            }
            if(children[j].textContent.match(/dia\s*\d+/i)) {
              children[j].textContent = 'proje\u00e7\u00e3o mensal (dia ' + diaAtual + '/30)';
            }
          }
        }
        // Card LITROS
        if(txt.indexOf('LITROS') >= 0 && txt.indexOf('ABASTECIDOS') >= 0 && children.length > 0) {
          for(var j=0; j<children.length; j++){
            if(children[j].textContent.match(/^[\d,.]+\s*L$/)) {
              children[j].textContent = litros.toLocaleString('pt-BR', {maximumFractionDigits:0}) + 'L';
            }
            if(children[j].textContent.match(/m[eé]dia\s*\d+/i)) {
              children[j].textContent = 'm\u00e9dia ' + mediaLitros + 'L/t\u00e9cnico';
            }
          }
        }
        // Card KM
        if(txt.indexOf('KM ESTIMADO') >= 0 && children.length > 0) {
          for(var j=0; j<children.length; j++){
            if(children[j].textContent.match(/^[\d,.]+$/) && children[j].style.fontSize) {
              children[j].textContent = km.toLocaleString('pt-BR', {maximumFractionDigits:0});
            }
            if(children[j].textContent.match(/m[eé]dia\s*\d+/i)) {
              children[j].textContent = 'm\u00e9dia ' + mediaKm + ' km/t\u00e9cnico';
            }
          }
        }
      }
      console.log('[DynFrotaKPI] Cards atualizados: R$'+totalGasto.toFixed(2)+', '+nTec+' tecs');
    })
    .catch(function(e){ console.log('[DynFrotaKPI] Falhou:', e); });
})();
"""
kpi_js += '</' + 'script>\n'

body_end = html.rfind('</body>')
html = html[:body_end] + kpi_js + '\n' + html[body_end:]
print('[+] Frota KPI loader inserido')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo')
'''

print('Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_frota_kpi.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_frota_kpi.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

c.close()
print('\nCtrl+Shift+R para testar.')
