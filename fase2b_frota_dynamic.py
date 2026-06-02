"""
Fase 2b: Dinamizar aba Frota.
Injeta JS que carrega frota.json e re-renderiza as tabelas.
Fallback: se fetch falhar, dados inline ficam.
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')
print('[1/3] Backup...')
c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_frota.html')
time.sleep(1)

patch_code = r'''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

if 'dynamicFrotaLoader' in html:
    print('[!] Frota loader ja existe')
    exit(0)

# JS que carrega frota.json e re-renderiza
frota_js = '<' + 'script id="dynamicFrotaLoader">\n'
frota_js += r"""
(function(){
  fetch('data/frota.json?t='+Date.now())
    .then(function(r){if(!r.ok) throw 'HTTP '+r.status; return r.json();})
    .then(function(f){
      console.log('[DynFrota] frota.json: '+f.veiculos.length+' veiculos');

      // === KPIs Frota (cards no topo) ===
      var kpiEls = document.querySelectorAll('#frota-veiculos .kpi-value, #frota .kpi-value');
      // Nao temos IDs especificos nos KPIs de frota, vamos atualizar pelo contexto

      // === VEICULOS ===
      var vDiv = document.getElementById('frota-veiculos');
      if(vDiv && f.veiculos.length) {
        var tbl = vDiv.querySelector('table');
        if(tbl) {
          var tbody = tbl.tBodies[0] || tbl;
          var rows = '';
          f.veiculos.forEach(function(v){
            var st = (v.status||'').toUpperCase();
            var badge;
            if(st.indexOf('ATIVIDADE')>=0) badge='<span class="badge green">Em Atividade</span>';
            else if(st.indexOf('OFICINA')>=0) badge='<span class="badge red">Oficina</span>';
            else if(st==='PARADO'||st==='DESMOBILIZADO') badge='<span class="badge yellow">Parado</span>';
            else if(st.indexOf('DEVOLVIDO')>=0) badge='<span class="badge yellow">Devolvido</span>';
            else if(st.indexOf('ATESTADO')>=0) badge='<span class="badge yellow">Atestado</span>';
            else badge='<span class="badge">'+v.status+'</span>';
            rows+='<tr><td style="font-weight:600;color:#e8eaf6">'+v.placa+'</td><td>'+v.tecnico+'</td><td>'+v.locadora+'</td><td>'+badge+'</td></tr>';
          });
          tbody.innerHTML = rows;
        }
      }

      // === OFICINA ===
      var mDiv = document.getElementById('frota-manut');
      if(mDiv && f.oficina) {
        var tables = mDiv.querySelectorAll('table');
        // Primeira tabela = oficina
        if(tables[0] && f.oficina.length) {
          var tbody = tables[0].tBodies[0] || tables[0];
          var rows = '';
          f.oficina.sort(function(a,b){return (b.dias||0)-(a.dias||0);});
          f.oficina.forEach(function(o){
            var st=o.status.toUpperCase();
            var badge=st.indexOf('OFICINA')>=0?'<span class="badge red">Na Oficina</span>':st.indexOf('AGEND')>=0?'<span class="badge yellow">Agendado</span>':'<span class="badge">'+o.status+'</span>';
            var d=o.dias||0;
            var db=d>30?'<span class="badge red">'+d+'d</span>':d>14?'<span class="badge yellow">'+d+'d</span>':'<span class="badge green">'+d+'d</span>';
            rows+='<tr><td style="font-weight:600;color:#e8eaf6">'+o.placa+'</td><td>'+o.motorista+'</td><td>'+o.entrada+'</td><td>'+o.previsao+'</td><td>'+o.cidade+'</td><td>'+badge+'</td><td>'+db+'</td></tr>';
          });
          tbody.innerHTML = rows;
        }
        // Segunda tabela = revisao
        if(tables[1] && f.revisao && f.revisao.length) {
          var tbody2 = tables[1].tBodies[0] || tables[1];
          var rows2 = '';
          f.revisao.forEach(function(r){
            var st=r.status.toUpperCase();
            var badge=st.indexOf('AGENDAR')>=0?'<span class="badge yellow">Agendar</span>':'<span class="badge red">Revis\u00e3o</span>';
            rows2+='<tr><td style="font-weight:600;color:#e8eaf6">'+r.placa+'</td><td>'+r.tecnico+'</td><td>'+r.locadora+'</td><td>'+r.km+' km</td><td>'+r.data+'</td><td>'+badge+'</td></tr>';
          });
          tbody2.innerHTML = rows2;
        }
      }

      // === COMBUSTIVEL ===
      var cDiv = document.getElementById('frota-comb');
      if(cDiv && f.combustivel && f.combustivel.length) {
        var tbl = cDiv.querySelector('table');
        if(tbl) {
          var tbody = tbl.tBodies[0] || tbl;
          var rows = '';
          f.combustivel.forEach(function(c,i){
            var kmR = c.km_rodado||0;
            var kmE = c.km||0;
            var pct = kmE>0 ? Math.min(Math.round(kmR/kmE*100),100) : 0;
            var color = pct>=80?'#22d3a0':pct>=50?'#fbbf24':'#ff4d6d';
            var bar = '<div style="display:flex;align-items:center;gap:10px;"><div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:10px;min-width:120px;"><div style="width:'+pct+'%;height:100%;background:'+color+';border-radius:4px;transition:width 0.3s;"></div></div><span style="font-size:12px;color:'+color+';font-weight:700;min-width:40px;text-align:right;">'+pct+'%</span></div>';
            rows+='<tr><td style="padding:10px 8px;text-align:center;">'+(i+1)+'</td><td style="padding:10px 12px;">'+c.tecnico+'</td><td style="padding:10px 12px;color:#f472b6;font-weight:600;text-align:right;">R$ '+c.gasto.toLocaleString('pt-BR',{minimumFractionDigits:2})+'</td><td style="padding:10px 12px;text-align:right;">'+c.litros+'</td><td style="padding:10px 12px;text-align:right;color:#60a5fa;font-weight:600;">'+kmR.toLocaleString('pt-BR',{maximumFractionDigits:0})+'</td><td style="padding:10px 12px;text-align:right;color:#94a3b8;">'+kmE.toLocaleString('pt-BR',{maximumFractionDigits:0})+'</td><td style="padding:10px 12px;min-width:180px;">'+bar+'</td></tr>';
          });
          tbody.innerHTML = rows;
        }
      }

      // === DESLOCAMENTO ===
      var dDiv = document.getElementById('frota-desl');
      if(dDiv) {
        var tables = dDiv.querySelectorAll('table');
        // Primeira tabela = por tecnico
        if(tables[0] && f.deslocamento_tec && f.deslocamento_tec.length) {
          var tbody = tables[0].tBodies[0] || tables[0];
          var rows = '';
          f.deslocamento_tec.forEach(function(t,i){
            rows+='<tr><td>'+(i+1)+'</td><td>'+t.tecnico+'</td><td>'+t.viagens+'</td><td>'+t.km.toLocaleString('pt-BR',{maximumFractionDigits:0})+'</td><td>R$ '+t.valor.toLocaleString('pt-BR',{minimumFractionDigits:2})+'</td></tr>';
          });
          tbody.innerHTML = rows;
        }
        // Segunda tabela = por destino
        if(tables[1] && f.deslocamento_dest && f.deslocamento_dest.length) {
          var tbody2 = tables[1].tBodies[0] || tables[1];
          var rows2 = '';
          f.deslocamento_dest.forEach(function(d,i){
            rows2+='<tr><td>'+(i+1)+'</td><td style="font-weight:600;color:#e8eaf6">'+d.destino+'</td><td>'+d.viagens+'</td><td>'+d.km.toLocaleString('pt-BR',{maximumFractionDigits:0})+'</td></tr>';
          });
          tbody2.innerHTML = rows2;
        }
      }

      console.log('[DynFrota] Todas as tabelas atualizadas');
    })
    .catch(function(e){ console.log('[DynFrota] Falhou (usando inline):', e); });
})();
"""
frota_js += '</' + 'script>\n'

# Inserir antes de </body>
body_end = html.rfind('</body>')
if body_end > 0:
    html = html[:body_end] + frota_js + '\n' + html[body_end:]
    print('[+] Dynamic Frota Loader inserido')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo (%d bytes)' % len(html))
'''

print('\n[2/3] Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_frota.py', 'w') as f:
    f.write(patch_code)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_frota.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

print('\n[3/3] Verificacao...')
i, o, e = c.exec_command("grep -c 'dynamicFrotaLoader' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'  dynamicFrotaLoader: {o.read().decode().strip()} refs')

c.close()
print('\nFrota dinamica! Ctrl+Shift+R para testar.')
