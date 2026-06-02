import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar o que o dashboard-nginx serve
print('[1] Mount do dashboard-nginx:')
i, o, e = c.exec_command("docker inspect dashboard-nginx --format='{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}'")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

# 2. Verificar se a aba WhatsApp carrega corretamente - buscar a linha do onclick
print('\n[2] onclick showWaSub no HTML publicado:')
i, o, e = c.exec_command("curl -s https://svoboda.rtflowapp.com/ 2>/dev/null | grep -o \"onclick=\\\"showWaSub[^\\\"]*\\\"\" | head -5")
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Verificar se há erro na seção CSS/JS que pode impedir a renderização
print('\n[3] Verificando erros de sintaxe com Node.js:')
i, o, e = c.exec_command("""docker exec backend-agenda node -e "
const fs = require('fs');
try {
  // Extrair apenas a parte do WhatsApp Agenda JS do HTML
  const html = fs.readFileSync('/frontend/index.html', 'utf8');
  // Verificar se tem página whatsapp-agenda
  const hasWA = html.includes('whatsapp-agenda');
  console.log('whatsapp-agenda encontrado:', hasWA);
  // Procurar erros de template literal ou chaves
  const scripts = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
  console.log('Blocos script:', scripts.length);
  for (let i = 0; i < scripts.length; i++) {
    const s = scripts[i].replace(/<\/?script>/g, '');
    try { new Function(s); console.log('Script', i, ': OK'); }
    catch(e) { console.log('Script', i, ': ERRO -', e.message.substring(0, 150)); }
  }
} catch(e) { console.log('Erro:', e.message); }
" 2>&1""")
time.sleep(8)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
