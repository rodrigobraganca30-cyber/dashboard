import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Remover script antigo que nao funciona
html = html.replace(html[html.find('<script id="dynamicFrotaKPI">'):html.find('</script>', html.find('<script id="dynamicFrotaKPI">')) + len('</script>')], '') if 'dynamicFrotaKPI' in html else html

kpi_js = """<script id="dynamicFrotaKPI2">
(function(){
  fetch('data/frota.json?t='+Date.now())
    .then(function(r){return r.json();})
    .then(function(f){
      var k=f.kpis||{};
      var nTec=(f.combustivel||[]).length;
      var totalGasto=k.combustivel_total||0;
      var litros=k.litros_total||0;
      var km=k.km_total||0;
      var dia=new Date().getDate();
      var proj=dia>0?(totalGasto/dia)*30:0;
      var mLit=nTec>0?Math.round(litros/nTec):0;
      var mKm=nTec>0?Math.round(km/nTec):0;

      var box=document.getElementById('frota-comb');
      if(!box) return;
      var cards=box.querySelectorAll('.kpi-card');

      // Card 0: Total Gasto (red)
      if(cards[0]){
        var v=cards[0].querySelector('.kpi-value');
        if(v) v.textContent='R$ '+totalGasto.toLocaleString('pt-BR',{minimumFractionDigits:2});
        var s=cards[0].querySelector('.kpi-sub');
        if(s) s.textContent=nTec+' t\\u00e9cnicos';
      }
      // Card 1: Projecao
      if(cards[1]){
        var v=cards[1].querySelector('.kpi-value');
        if(v) v.textContent='R$ '+proj.toLocaleString('pt-BR',{minimumFractionDigits:2});
        var s=cards[1].querySelector('.kpi-sub');
        if(s) s.textContent='proje\\u00e7\\u00e3o mensal (dia '+dia+'/30)';
      }
      // Card 2: Litros (blue)
      if(cards[2]){
        var v=cards[2].querySelector('.kpi-value');
        if(v) v.textContent=litros.toLocaleString('pt-BR',{maximumFractionDigits:0})+'L';
        var s=cards[2].querySelector('.kpi-sub');
        if(s) s.textContent='m\\u00e9dia '+mLit+'L/t\\u00e9cnico';
      }
      // Card 3: KM (green)
      if(cards[3]){
        var v=cards[3].querySelector('.kpi-value');
        if(v) v.textContent=km.toLocaleString('pt-BR',{maximumFractionDigits:0});
        var s=cards[3].querySelector('.kpi-sub');
        if(s) s.textContent='m\\u00e9dia '+mKm+' km/t\\u00e9cnico';
      }
      console.log('[DynFrotaKPI] R$'+totalGasto.toFixed(2)+' | '+litros+'L | '+km+'km');
    })
    .catch(function(e){console.log('[DynFrotaKPI] err:',e);});
})();
</""" + """script>
"""

body_end = html.rfind('</body>')
html = html[:body_end] + kpi_js + '\n' + html[body_end:]

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] KPI cards patch aplicado')
'''

print('Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_kpi2.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_kpi2.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar.')
