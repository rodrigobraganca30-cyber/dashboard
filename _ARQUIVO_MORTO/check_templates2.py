import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Ver a seção de templates no backup recente que NÃO está no atual
print('[1] Diferença entre os dois HTMLs (seção templates):')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const atual = fs.readFileSync('/data/index.html', 'utf8');
const bak = fs.readFileSync('/data/index.html.bak.20260526_220224', 'utf8');

// Extrair bloco de templates do backup
const templateStart = bak.indexOf('Usar Template Meta Aprovado');
const templateEnd = bak.indexOf('HISTÓRICO DE CAMPANHAS');

const templateStartAtual = atual.indexOf('Usar Template Meta Aprovado');
const templateEndAtual = atual.indexOf('HISTÓRICO DE CAMPANHAS');

console.log('Backup - Template section:', templateStart > 0 ? 'EXISTE' : 'NAO');
console.log('Atual  - Template section:', templateStartAtual > 0 ? 'EXISTE' : 'NAO');

if (templateStart > 0 && templateStartAtual > 0) {
  const bakSection = bak.substring(templateStart, templateEnd > 0 ? templateEnd : templateStart + 2000);
  const atualSection = atual.substring(templateStartAtual, templateEndAtual > 0 ? templateEndAtual : templateStartAtual + 2000);
  console.log('Backup template section length:', bakSection.length);
  console.log('Atual template section length:', atualSection.length);
  if (bakSection.length !== atualSection.length) {
    console.log('DIFEREM em tamanho!');
  }
}

// Check if meta template select/dropdown exists
console.log('');
console.log('Backup - template select:', bak.includes('wa-tpl-select') ? 'SIM' : 'NAO');
console.log('Atual  - template select:', atual.includes('wa-tpl-select') ? 'SIM' : 'NAO');

console.log('Backup - Usar Template:', bak.includes('Usar Template Meta') ? 'SIM' : 'NAO');
console.log('Atual  - Usar Template:', atual.includes('Usar Template Meta') ? 'SIM' : 'NAO');

// Check waLoadMetaTemplates function
const bakFn = bak.indexOf('function waLoadMetaTemplates');
const atualFn = atual.indexOf('function waLoadMetaTemplates');
console.log('');
console.log('Backup - waLoadMetaTemplates fn pos:', bakFn);
console.log('Atual  - waLoadMetaTemplates fn pos:', atualFn);

// Compare the function
if (bakFn > 0 && atualFn > 0) {
  const bakFnEnd = bak.indexOf('}', bakFn + 500);
  const atualFnEnd = atual.indexOf('}', atualFn + 500);
  const bakFnCode = bak.substring(bakFn, bakFnEnd + 1);
  const atualFnCode = atual.substring(atualFn, atualFnEnd + 1);
  console.log('Backup fn length:', bakFnCode.length);
  console.log('Atual fn length:', atualFnCode.length);
  if (bakFnCode === atualFnCode) console.log('Funções IGUAIS');
  else console.log('Funções DIFERENTES!');
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Verificar se o endpoint /meta/templates existe no backend
print('\n[2] Backend - rota /meta/templates:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/meta/templates').then(r=>{console.log('Status:',r.status);return r.text()}).then(t=>console.log(t.substring(0,200))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
