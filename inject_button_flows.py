"""
inject_button_flows.py — Injeta lógica de resposta automática por botão Meta
no webhook do backend-agenda.

Fluxo A: Confirmação de Visita (SIM confirmo / Preciso reagendar / Cancelar)
Fluxo B: Recolhimento de Equipamento (Agendar / Já devolvi)
Fluxo C: Pesquisa de Qualidade (SIM tudo certo / NÃO tenho problema / Quero falar com alguém)
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# ══════════════════════════════════════════════════
# FASE 2: BACKUP
# ══════════════════════════════════════════════════
print(f'[1/6] Backup do index.js atual...')
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js /docker/backup_index_{ts}_pre_buttons.js')
time.sleep(2)
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'    ERRO backup: {err}')
    c.close()
    sys.exit(1)
print('    OK')

print(f'\n[2/6] Backup Redis BGSAVE...')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli BGSAVE')
time.sleep(2)
print(f'    {o.read().decode().strip()}')

# ══════════════════════════════════════════════════
# FASE 4: PATCH — Injetar BUTTON_FLOWS no webhook
# ══════════════════════════════════════════════════
patch_js = r'''
const fs = require('fs');
let code = fs.readFileSync('/app/index.js', 'utf8');

// ── Verificar se já foi injetado ──
if (code.includes('BUTTON_FLOWS')) {
  console.log('[=] BUTTON_FLOWS já existe no código. Nada a fazer.');
  process.exit(0);
}

// ── Encontrar ponto de inserção ──
// Âncora: logo após "await redis.incr(KEY_UNREAD(phone));"
// e antes de "// ── JARVIS IA"
const anchorIncr = 'await redis.incr(KEY_UNREAD(phone));';
const anchorJarvis = '// ── JARVIS IA';

const idxIncr = code.indexOf(anchorIncr);
const idxJarvis = code.indexOf(anchorJarvis);

if (idxIncr === -1) {
  console.log('[!] Âncora "redis.incr(KEY_UNREAD)" não encontrada!');
  process.exit(1);
}
if (idxJarvis === -1) {
  console.log('[!] Âncora "JARVIS IA" não encontrada!');
  process.exit(1);
}

console.log('[+] Âncoras encontradas:');
console.log('    incr(KEY_UNREAD) na posição:', idxIncr);
console.log('    JARVIS IA na posição:', idxJarvis);

// ── Mover clientId para antes do bloco de botões ──
// Remover "const clientId = ..." da seção Jarvis e colocar antes
const clientIdLine = "const clientId = await redis.get(KEY_PHONE_ID(phone));";
const jarvisUrlLine = "const jarvisUrl = process.env.JARVIS_URL";
const jarvisHandledLine = "let jarvisHandled = false;";

// Ponto de inserção: logo após o \n do anchorIncr
const insertPos = code.indexOf('\n', idxIncr) + 1;

// O bloco a inserir
const buttonBlock = `
            // ── FLUXO AUTOMÁTICO POR BOTÃO META ──────────────
            const clientId = await redis.get(KEY_PHONE_ID(phone));
            let jarvisHandled = false;

            const BUTTON_FLOWS = {
              // Fluxo A: Confirmação de visita
              'sim, confirmo':          { status: 'confirmado',      msg: 'Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!' },
              'preciso reagendar':      { status: 'reagendado',      msg: 'Sem problemas, NOME! Por favor, nos informe uma nova data e horário de sua preferência.' },
              'cancelar':               { status: 'nao-atendido',    msg: 'Entendido, NOME. Seu atendimento foi cancelado. Caso precise, entre em contato conosco.' },
              // Fluxo B: Recolhimento de equipamento
              'agendar':                { status: 'agendado',        msg: 'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.' },
              'já devolvi':             { status: 'resolvido',       msg: 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.' },
              'ja devolvi':             { status: 'resolvido',       msg: 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.' },
              // Fluxo C: Pesquisa de qualidade
              'sim, tudo certo':        { status: 'satisfeito',      msg: 'Que bom saber, NOME! Ficamos felizes que está tudo funcionando. Qualquer dúvida, estamos à disposição!' },
              'não, tenho problema':    { status: 'problema-aberto', msg: 'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.' },
              'nao, tenho problema':    { status: 'problema-aberto', msg: 'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.' },
              'quero falar com alguém': { status: 'problema-aberto', msg: 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.' },
              'quero falar com alguem': { status: 'problema-aberto', msg: 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.' },
            };

            const btnKey = text.toLowerCase().trim();
            const btnFlow = BUTTON_FLOWS[btnKey];
            if (btnFlow && clientId) {
              try {
                const cRaw = await redis.get(KEY_CLIENTS);
                const cList = cRaw ? JSON.parse(cRaw) : [];
                const cData = cList.find(c => c.id === clientId) || {};
                const firstName = (cData.nome || 'Cliente').split(' ')[0];
                const firstName2 = firstName.charAt(0).toUpperCase() + firstName.slice(1).toLowerCase();
                const replyMsg = btnFlow.msg.replace(/NOME/g, firstName2);

                await setStatus(clientId, btnFlow.status, 'Botão: "' + text + '"');
                await sendText(phone, replyMsg);
                await appendMsg(phone, { from: 'me', text: replyMsg, ts: Date.now(), instance: 'Meta API Oficial' });
                jarvisHandled = true;
                log('info', 'Fluxo botão processado', { phone, button: text, status: btnFlow.status, clientId });
              } catch (btnErr) {
                log('error', 'Erro no fluxo botão', { phone, button: text, error: btnErr.message });
              }
            }
            // ── FIM FLUXO BOTÃO ──────────────────────────────

`;

// Inserir bloco
code = code.substring(0, insertPos) + buttonBlock + code.substring(insertPos);

// Remover duplicatas: "const clientId" e "let jarvisHandled" que ficaram na seção Jarvis
// Agora elas estão DEPOIS do bloco inserido, precisamos removê-las
const afterBlock = code.indexOf('// ── FIM FLUXO BOTÃO');
const jarvisSection = code.indexOf(anchorJarvis, afterBlock);

if (jarvisSection !== -1) {
  // Encontrar e remover "const clientId = ..." na seção Jarvis (agora é duplicata)
  const searchArea = code.substring(jarvisSection, jarvisSection + 500);
  
  // Substituir "const clientId" por comentário (já declarado acima)
  if (searchArea.includes(clientIdLine)) {
    code = code.substring(0, jarvisSection) + 
           code.substring(jarvisSection).replace(
             clientIdLine, 
             '// clientId já declarado acima (BUTTON_FLOWS)'
           );
    console.log('[+] Removida duplicata de clientId na seção Jarvis');
  }
  
  // Substituir "let jarvisHandled = false;" (já declarado acima)
  const jarvisSectionNew = code.indexOf(anchorJarvis, afterBlock);
  const searchArea2 = code.substring(jarvisSectionNew, jarvisSectionNew + 500);
  if (searchArea2.includes(jarvisHandledLine)) {
    code = code.substring(0, jarvisSectionNew) + 
           code.substring(jarvisSectionNew).replace(
             jarvisHandledLine,
             '// jarvisHandled já declarado acima (BUTTON_FLOWS)'
           );
    console.log('[+] Removida duplicata de jarvisHandled na seção Jarvis');
  }
}

// ── Salvar ──
fs.writeFileSync('/app/index.js', code);
console.log('[+] index.js salvo com BUTTON_FLOWS (' + code.split('\n').length + ' linhas)');

// ── Verificação rápida ──
const verify = fs.readFileSync('/app/index.js', 'utf8');
const hasButtons = verify.includes('BUTTON_FLOWS');
const hasSimConfirmo = verify.includes("'sim, confirmo'");
const hasPesquisa = verify.includes("'sim, tudo certo'");
const hasRecolhimento = verify.includes("'agendar'");
console.log('[✓] BUTTON_FLOWS presente:', hasButtons);
console.log('[✓] Fluxo A (confirmo):', hasSimConfirmo);
console.log('[✓] Fluxo B (recolhimento):', hasRecolhimento);
console.log('[✓] Fluxo C (qualidade):', hasPesquisa);
'''

# Enviar patch para VPS
print(f'\n[3/6] Enviando patch para VPS...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_buttons.js', 'w') as f:
    f.write(patch_js)
sftp.close()
print('    OK')

# Executar patch dentro do container
print(f'\n[4/6] Aplicando patch no container...')
i, o, e = c.exec_command('docker cp /tmp/patch_buttons.js backend-agenda:/tmp/patch_buttons.js')
time.sleep(1)
i, o, e = c.exec_command('docker exec backend-agenda node /tmp/patch_buttons.js')
time.sleep(5)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'    STDERR: {err[:300]}')
if '[!]' in out or 'Error' in err:
    print('\n❌ PATCH FALHOU — container NÃO foi modificado. Backup intacto.')
    c.close()
    sys.exit(1)

# Reiniciar container
print(f'\n[5/6] Reiniciando backend-agenda...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(10)
print(f'    {o.read().decode().strip()}')

# Verificar
print(f'\n[6/6] Verificação final...')
time.sleep(3)

# Container rodando?
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
status = o.read().decode().strip()
print(f'    Container: {status}')

# BUTTON_FLOWS existe?
i, o, e = c.exec_command('docker exec backend-agenda grep -c "BUTTON_FLOWS" /app/index.js')
time.sleep(1)
count = o.read().decode().strip()
print(f'    BUTTON_FLOWS encontrado: {count} ocorrências')

# Testar health
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/health').then(r=>r.json()).then(j=>console.log('Health:', JSON.stringify(j))).catch(e=>console.log('ERR:', e.message))"''')
time.sleep(3)
print(f'    {o.read().decode().strip()}')

# Últimos logs (botões sendo processados?)
print(f'\n    Últimos logs:')
i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
print(f'\n{"="*50}')
print(f'✅ BUTTON_FLOWS INJETADO COM SUCESSO')
print(f'   Backup: /docker/backup_index_{ts}_pre_buttons.js')
print(f'{"="*50}')
