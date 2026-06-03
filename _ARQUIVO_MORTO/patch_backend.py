"""
patch_backend.py
Baixa index.js do VPS, aplica cirurgicamente o validador de telefones, a checagem
de Blacklist e o salvamento dinâmico de falhas. Em seguida, envia de volta e reinicia o backend.
"""
import paramiko, os, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# 1. Baixa o arquivo index.js atual do VPS
sftp = client.open_sftp()
remote_path = '/docker/whatsapp-agenda/backend/index.js'
local_path = r'C:\Users\SVOBODA\Desktop\DASHBOARD\index_vps.js'
sftp.get(remote_path, local_path)
sftp.close()
print(f'[OK] Arquivo index.js baixado para: {local_path}')

with open(local_path, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 2. Insere a função de validação validateAndCleanPhone
if 'function validateAndCleanPhone' not in conteudo:
    validador_code = """
// ──────────────────────────────────────────────
// TELEPHONE VALIDATOR & NORMALIZER (PREVENTS ERRO 131026)
// ──────────────────────────────────────────────
function validateAndCleanPhone(phone) {
  if (!phone) return { valid: false, error: 'Telefone ausente', num: '' };
  let cleaned = String(phone).replace(/\\D/g, '');
  if (cleaned.startsWith('550')) {
    cleaned = '55' + cleaned.substring(3);
  }
  if (cleaned.length === 10 || cleaned.length === 11) {
    cleaned = '55' + cleaned;
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['9', '8', '7'].includes(firstDig)) {
      cleaned = cleaned.substring(0, 4) + '9' + cleaned.substring(4);
    }
  }
  if (cleaned.length !== 12 && cleaned.length !== 13) {
    return { valid: false, error: 'Tamanho invalido (' + cleaned.length + ' digitos)', num: cleaned };
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['2', '3', '4', '5'].includes(firstDig)) {
      return { valid: false, error: 'Telefone Fixo (Sem WhatsApp ativo)', num: cleaned };
    }
  }
  return { valid: true, num: cleaned };
}
"""
    conteudo = conteudo.replace(
        "function log(level, msg, data = {}) {",
        validador_code.strip() + "\n\nfunction log(level, msg, data = {}) {"
    )
    print('[+] Função validateAndCleanPhone injetada.')
else:
    print('[ ] Função validateAndCleanPhone já está no código.')

# 3. Insere as novas rotas de Blacklist no index.js
if 'app.get(\'/agenda/blacklist\'' not in conteudo:
    blacklist_routes = """
// ──────────────────────────────────────────────
// BLACKLIST ENDPOINTS
// ──────────────────────────────────────────────
app.get('/agenda/blacklist', async (req, res) => {
  try {
    const list = await redis.sMembers('agenda:blacklist');
    res.json(list || []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/agenda/blacklist', async (req, res) => {
  try {
    const { phone, action } = req.body;
    if (!phone) return res.status(400).json({ error: 'phone obrigatorio' });
    let number = String(phone).replace(/\\D/g, '');
    if (!number.startsWith('55') && number.length >= 10) number = '55' + number;
    
    if (action === 'add') {
      await redis.sAdd('agenda:blacklist', number);
      log('info', 'Numero adicionado a Blacklist via API', { number });
      res.json({ ok: true, msg: 'Numero adicionado' });
    } else if (action === 'remove') {
      await redis.sRem('agenda:blacklist', number);
      log('info', 'Numero removido da Blacklist via API', { number });
      res.json({ ok: true, msg: 'Numero removido' });
    } else {
      res.status(400).json({ error: 'action deve ser add ou remove' });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
"""
    # Insere antes da rota app.get('/agenda/clients'
    conteudo = conteudo.replace(
        "app.get('/agenda/clients'",
        blacklist_routes + "\napp.get('/agenda/clients'"
    )
    print('[+] Rotas de Blacklist (/agenda/blacklist) injetadas.')
else:
    print('[ ] Rotas de Blacklist já estão no código.')

# 4. Atualiza POST /status/:clientId para gerenciar a Blacklist
original_status_post = """app.post('/status/:clientId', async (req, res) => {
  try {
    const { status, obs } = req.body;
    await setStatus(req.params.clientId, status, obs);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});"""

patched_status_post = """app.post('/status/:clientId', async (req, res) => {
  try {
    const { status, obs } = req.body;
    await setStatus(req.params.clientId, status, obs);
    
    // Sincronizacao automatica com a Blacklist baseada estritamente no Numero
    let phone = '';
    const match = req.params.clientId.match(/^wa_(\\d+)_/);
    if (match) {
      phone = match[1];
    } else {
      phone = req.params.clientId.replace(/\\D/g, '');
    }
    
    if (phone) {
      if (!phone.startsWith('55') && phone.length >= 10) {
        phone = '55' + phone;
      }
      if (status === 'numero-nao-pertence') {
        await redis.sAdd('agenda:blacklist', phone);
        log('info', 'Numero adicionado a Blacklist manualmente pelo Painel', { phone, status });
      } else {
        await redis.sRem('agenda:blacklist', phone);
        log('info', 'Numero removido da Blacklist manualmente pelo Painel', { phone, status });
      }
    }
    
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});"""

if 'Sincronizacao automatica com a Blacklist' not in conteudo:
    # Garante normalização de quebras de linha
    c_norm = conteudo.replace('\r\n', '\n')
    osp_norm = original_status_post.replace('\r\n', '\n')
    psp_norm = patched_status_post.replace('\r\n', '\n')
    
    if osp_norm in c_norm:
        conteudo = c_norm.replace(osp_norm, psp_norm)
        print('[+] Rota POST /status/:clientId patcheada com sucesso.')
    else:
        # Tenta substituir via regex caso haja pequenas variações de espaços
        patt = r"app\.post\('/status/:clientId'.*?\}\s*\}\);\s*\}"
        # Se não achou exato, deixa um aviso
        print('[ALERTA] Rota POST /status/:clientId exata nao encontrada. Tentando patch aproximado...')
        conteudo = re.sub(
            r"app\.post\('/status/:clientId',\s*async\s*\(req,\s*res\)\s*=>\s*\{.*?\}\s*\}\);\s*\}",
            patched_status_post.replace('\\', '\\\\'),
            c_norm,
            flags=re.DOTALL
        )
else:
    print('[ ] Rota POST /status/:clientId já está patcheada.')

# 5. Adiciona validação pré-envio no POST /send
original_send_top = """app.post('/send', async (req, res) => {
  try {
    if (!checkRateLimit('send')) {
      return res.status(429).json({ error: 'Rate limit: máx 20 envios/min' });
    }

    const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    const instance = 'Meta_API_Oficial';"""

patched_send_top = """app.post('/send', async (req, res) => {
  try {
    if (!checkRateLimit('send')) {
      return res.status(429).json({ error: 'Rate limit: máx 20 envios/min' });
    }

    const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    // 1. Limpeza e Validacao de Formato
    const val = validateAndCleanPhone(phone);
    if (!val.valid) {
      return res.status(400).json({ error: `Numero Invalido: ${val.error}` });
    }
    const number = val.num;

    // 2. Checagem de Blacklist
    const isBlacklisted = await redis.sIsMember('agenda:blacklist', number);
    if (isBlacklisted) {
      return res.status(400).json({ error: 'Este numero esta bloqueado na Blacklist devido a falhas anteriores.' });
    }

    const instance = 'Meta_API_Oficial';"""

if 'Validacao de Formato' not in conteudo:
    c_norm = conteudo.replace('\r\n', '\n')
    ost_norm = original_send_top.replace('\r\n', '\n')
    pst_norm = patched_send_top.replace('\r\n', '\n')
    if ost_norm in c_norm:
        conteudo = c_norm.replace(ost_norm, pst_norm)
        # Substitui também a referência de 'phone' por 'number' no envio logo abaixo
        conteudo = conteudo.replace("sendText(phone, text)", "sendText(number, text)")
        conteudo = conteudo.replace("appendMsg(phone.replace(/\\D/g, '')", "appendMsg(number")
        print('[+] Rota POST /send patcheada com sucesso.')
    else:
        print('[ALERTA] Rota POST /send original não encontrada para patch.')
else:
    print('[ ] Rota POST /send já está patcheada.')

# 6. Atualiza a checagem no POST /send-bulk
# Localiza a função autônoma de disparo no send-bulk
if 'validateAndCleanPhone(rawPhone)' not in conteudo:
    print('[+] Injetando validador no loop do POST /send-bulk...')
    
    # Vamos patchear o loop do send-bulk cirurgicamente
    old_loop_start = """      for (let idx = 0; idx < clients.length; idx++) {
        const c = clients[idx];
        // Rodízio de templates
        const chosenTpl = tpls[idx % tpls.length];
        try {"""
        
    new_loop_start = """      for (let idx = 0; idx < clients.length; idx++) {
        const c = clients[idx];
        const rawPhone = c.phone || c.tel1 || c.tel2 || '';
        let number = rawPhone.replace(/\\D/g, '');
        if (!number.startsWith('55') && number.length >= 10) number = '55' + number;
        
        // Rodízio de templates
        const chosenTpl = tpls[idx % tpls.length];
        try {
          // 1. Validacao de formato
          const val = validateAndCleanPhone(rawPhone);
          if (!val.valid) {
            throw new Error(`Validacao de formato: ${val.error}`);
          }
          number = val.num;

          // 2. Checagem de Blacklist
          const isBlacklisted = await redis.sIsMember('agenda:blacklist', number);
          if (isBlacklisted) {
            throw new Error('Bloqueado pela Blacklist (Falhas anteriores)');
          }"""

    c_norm = conteudo.replace('\r\n', '\n')
    ols_norm = old_loop_start.replace('\r\n', '\n')
    nls_norm = new_loop_start.replace('\r\n', '\n')
    
    if ols_norm in c_norm:
        conteudo = c_norm.replace(ols_norm, nls_norm)
        # Substitui referências de telefone no loop
        conteudo = conteudo.replace("c.phone || c.tel1 || c.tel2", "number")
        conteudo = conteudo.replace("number = (c.phone || c.tel1 || c.tel2 || '').replace(/\\D/g, '')", "// number ja normalizado")
        
        # Patchear o bloco catch de erro do loop para adicionar a Blacklist Dinamica
        old_catch = """        } catch (e) {
          failed++;
          log('error', 'Falha envio', { nome: c.nome, error: e.response?.data || e.message });
        }"""
        
        new_catch = """        } catch (e) {
          failed++;
          log('error', 'Falha envio', { nome: c.nome, phone: number, error: e.response?.data || e.message });
          
          const isBlacklistError = e.message.includes('Blacklist');
          const isValidationError = e.message.includes('Validacao');
          const statusText = 'numero-nao-pertence';
          
          let obsText = 'Falha envio: ' + (e.response?.data?.error?.message || e.message);
          if (isBlacklistError) obsText = 'Bloqueado: Lista Negra (Falhas anteriores)';
          if (isValidationError) obsText = 'Bloqueado pelo sistema: ' + e.message;
          
          await setStatus(c.id, statusText, obsText);
          
          // DYNAMIC BLACKLIST: Adiciona automaticamente a blacklist se for erro real
          const isMetaInvalidUser = e.response?.data?.error?.code === 131026 || 
                                    (e.response?.data?.error?.message && e.response.data.error.message.includes('valid'));
          
          if (isValidationError || isMetaInvalidUser) {
            if (number && number.length >= 10) {
              await redis.sAdd('agenda:blacklist', number);
              log('info', 'Numero adicionado a Blacklist automaticamente devido a falha real', { number, error: e.message });
            }
          }
        }"""
        
        oc_norm = old_catch.replace('\r\n', '\n')
        nc_norm = new_catch.replace('\r\n', '\n')
        
        if oc_norm in conteudo:
            conteudo = conteudo.replace(oc_norm, nc_norm)
            print('[+] Blacklist Dinâmica e tratamento de erros do loop injetados no catch.')
        else:
            print('[ALERTA] Bloco catch original do send-bulk não encontrado.')
            
        print('[+] Loop do POST /send-bulk patcheado.')
    else:
        print('[ALERTA] Loop do POST /send-bulk original não encontrado para patch.')
else:
    print('[ ] Loop do POST /send-bulk já está patcheada.')


# 7. Salva o arquivo modificado e envia de volta ao VPS
with open(local_path, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('[...] Enviando index.js modificado de volta ao VPS...')
sftp = client.open_sftp()
sftp.put(local_path, remote_path)
sftp.close()
print('[OK] index.js enviado com sucesso.')

# 8. Reinicia o container backend-agenda para aplicar
print('[...] Reiniciando container backend-agenda...')
stdin, stdout, stderr = client.exec_command('docker restart backend-agenda')
print(f'[DOCKER] {stdout.read().decode("utf-8").strip()}')

client.close()
print('=== PROCESSO DE PATCH DO BACKEND CONCLUÍDO COM SUCESSO ===')
