import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Script para reescrever a linha WA_STATUS_LABELS com emojis seguros
fix_script = r'''
const fs = require('fs');
let html = fs.readFileSync('/data/index.html', 'utf8');

// Definir a versão correta do WA_STATUS_LABELS sem problemas de surrogate
const correctLabels = "var WA_STATUS_LABELS={" +
  "pendente:'\u23F3 Pendente'," +
  "confirmado:'\u2705 Confirmado'," +
  "'nao-atendido':'\uD83D\uDCF5 N\u00E3o Atendeu'," +
  "reagendado:'\uD83D\uDD01 Reagendado'," +
  "entregue:'\uD83D\uDCE4 Entregue'," +
  "conveniente:'\uD83D\uDFE1 Conveniente'," +
  "'entregue-d1':'\uD83D\uDCE5 Entregue D-1'," +
  "'entregue-d0':'\uD83D\uDCE8 Entregue D-0'," +
  "'entregue-pos':'\uD83D\uDCE4 Entregue P\u00F3s'," +
  "satisfeito:'\uD83D\uDE0A Satisfeito'," +
  "insatisfeito:'\uD83D\uDE24 Insatisfeito'," +
  "'problema-aberto':'\uD83D\uDD27 Problema Aberto'," +
  "elogio:'\u2B50 Elogio'," +
  "normalizado:'NORMALIZADO'," +
  "'sem-contato':'SEM CONTATO'," +
  "resolvido:'RESOLVIDO'," +
  "'aberto-reparo':'ABERTO REPARO'," +
  "'problema-na-rede':'PROBLEMA NA REDE'," +
  "central:'CENTRAL'," +
  "'cancelamento-do-contrato':'CANCELAMENTO DO CONTRATO'," +
  "agendado:'AGENDADO'," +
  "'suspenso-por-debito':'SUSPENSO POR D\u00C9BITO'," +
  "'sem-retorno-supervisao':'SEM RETORNO SUPERVIS\u00C3O'," +
  "'numero-nao-pertence':'N\u00DAMERO N\u00C3O PERTENCE'," +
  "'area-de-risco':'\u00C1REA DE RISCO'," +
  "'nao-se-encontra':'N\u00C3O SE ENCONTRA'," +
  "'solicitou-upgrade':'SOLICITOU UPGRADE'," +
  "bloqueado:'\uD83D\uDEAB Bloqueado'" +
  "};";

// Encontrar e substituir
const start = html.indexOf('var WA_STATUS_LABELS={');
if (start < 0) { console.log('NOT FOUND!'); process.exit(1); }

const end = html.indexOf('};', start) + 2;
const oldBlock = html.substring(start, end);
console.log('Old block length:', oldBlock.length);
console.log('New block length:', correctLabels.length);

html = html.substring(0, start) + correctLabels + html.substring(end);

fs.writeFileSync('/data/index.html', html, 'utf8');
console.log('HTML saved, size:', html.length);

// Verify
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); }
  catch(e) { errors++; console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 80)); }
  idx++;
}
console.log(errors === 0 ? 'TODOS OK (' + idx + ' scripts)' : errors + ' ERROS');
console.log('showWaSub:', html.includes('function showWaSub'));
console.log('fluxo:', html.includes('waFluxoLoadConfig'));
console.log('bloqueado:', html.includes('bloqueado'));
'''

print('[1] Enviando fix final...')
sftp = c.open_sftp()
with sftp.open('/tmp/fix_emojis.js', 'w') as f:
    f.write(fix_script)
sftp.close()

print('[2] Executando...')
cmd = 'docker run --rm -v /docker/dashboard/html:/data -v /tmp:/scripts node:20-alpine node /scripts/fix_emojis.js'
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:200]}')

c.close()
