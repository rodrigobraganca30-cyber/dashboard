import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

if 'dynamicDonutFix' in html:
    print('[!] Donut fix ja existe')
    exit(0)

fix_js = """<script id="dynamicDonutFix">
// Fix: limpar donut-wrap inline antes do runFilter para evitar legenda duplicada
(function(){
  // Limpar o conteudo inline do donut-wrap para que o runFilter crie do zero
  var dw = document.querySelector('.donut-wrap');
  if(dw) {
    // Salvar apenas a estrutura, runFilter vai recriar
    dw.innerHTML = '';
  }

  // Apos dados carregarem, forcar re-render
  var checkReady = setInterval(function(){
    if(window._jsonDataLoaded && typeof runFilter === 'function') {
      clearInterval(checkReady);
      runFilter();
      console.log('[DonutFix] Donut re-renderizado limpo');
    }
  }, 200);

  // Timeout de seguranca
  setTimeout(function(){ clearInterval(checkReady); }, 5000);
})();
</""" + """script>
"""

body_end = html.rfind('</body>')
html = html[:body_end] + fix_js + '\n' + html[body_end:]

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] Donut fix aplicado')
'''

print('Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_donut.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_donut.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar.')
