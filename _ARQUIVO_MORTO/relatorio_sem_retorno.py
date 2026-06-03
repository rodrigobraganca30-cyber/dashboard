"""
relatorio_sem_retorno.py
Envia o script de análise para o VPS, executa lá e baixa o resultado.
"""
import paramiko, os, sys, json, csv, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Script que vai rodar NO VPS
SCRIPT_CONTEUDO = r'''#!/usr/bin/env python3
import subprocess, json, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def redis(cmd):
    r = subprocess.run(["docker","exec","redis-agenda","redis-cli"] + cmd, capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

def redis_list(cmd):
    r = subprocess.run(["docker","exec","redis-agenda","redis-cli"] + cmd, capture_output=True)
    return [l for l in r.stdout.decode("utf-8", errors="replace").strip().split("\n") if l]

print("Coletando msgs keys...", file=sys.stderr)
msgs_keys = redis_list(["KEYS", "agenda:msgs:*"])
print(f"Total msgs keys: {len(msgs_keys)}", file=sys.stderr)

print("Coletando status keys...", file=sys.stderr)
status_keys = redis_list(["KEYS", "agenda:status:*"])

phone2nome = {}
for sk in status_keys:
    m = re.match(r"agenda:status:wa_(\d+)_(.*)", sk)
    if m:
        phone_short = m.group(1)
        nome = m.group(2).replace("_", " ").title()
        phone2nome[phone_short] = nome

resultado = []
for i, mk in enumerate(msgs_keys):
    if i % 200 == 0:
        print(f"Processando {i}/{len(msgs_keys)}...", file=sys.stderr)
    raw = redis(["GET", mk])
    if not raw or raw == "(nil)":
        continue
    try:
        msgs = json.loads(raw)
    except:
        continue
    if not isinstance(msgs, list):
        continue

    enviadas  = sum(1 for m in msgs if m.get("from") == "me")
    recebidas = sum(1 for m in msgs if m.get("from") == "client")
    phone_full = mk.replace("agenda:msgs:", "")
    phone_short = phone_full[2:] if phone_full.startswith("55") else phone_full
    nome = phone2nome.get(phone_short, phone2nome.get(phone_full, ""))
    minhas = [m for m in msgs if m.get("from") == "me"]
    ultima_ts = max((m.get("ts", 0) for m in minhas), default=0)

    resultado.append({
        "nome": nome,
        "telefone": phone_full,
        "enviadas": enviadas,
        "recebidas": recebidas,
        "ultima_ts": ultima_ts,
    })

with open("/tmp/relatorio_wpp.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False)
print(f"Salvo: {len(resultado)} registros", file=sys.stderr)
print("OK")
'''

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# Envia o script para o VPS
sftp = client.open_sftp()
with sftp.open('/tmp/analise_wpp.py', 'w') as f:
    f.write(SCRIPT_CONTEUDO.encode('utf-8'))
sftp.close()
print('[OK] Script enviado para /tmp/analise_wpp.py')

# Executa no VPS
print('[...] Executando análise (2-3 min)...')
stdin, stdout, stderr = client.exec_command(
    'python3 /tmp/analise_wpp.py 2>/tmp/analise_wpp_err.txt',
    timeout=360
)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f'[VPS] {out}')

# Lê stderr para progress
stdin2, stdout2, _ = client.exec_command('tail -5 /tmp/analise_wpp_err.txt')
print('[PROGRESS]', stdout2.read().decode('utf-8', errors='replace').strip())

if 'OK' not in out:
    print('[ERRO] Script não terminou com OK')
    sys.exit(1)

# Baixa o resultado JSON
print('[...] Baixando resultado...')
sftp2 = client.open_sftp()
with sftp2.open('/tmp/relatorio_wpp.json', 'r') as f:
    dados = json.loads(f.read().decode('utf-8'))
sftp2.close()
client.close()

print(f'[OK] Total clientes com histórico: {len(dados)}')

# Filtra 3+ enviadas e ZERO recebidas
sem_retorno = [d for d in dados if d['enviadas'] >= 3 and d['recebidas'] == 0]
sem_retorno.sort(key=lambda x: x['enviadas'], reverse=True)

com_retorno = [d for d in dados if d['recebidas'] > 0]
um_envio    = [d for d in dados if d['enviadas'] == 1 and d['recebidas'] == 0]
dois_envios = [d for d in dados if d['enviadas'] == 2 and d['recebidas'] == 0]

print(f'\n========== RESUMO ==========')
print(f'  Total c/ histórico:          {len(dados)}')
print(f'  Responderam (alguma vez):    {len(com_retorno)}')
print(f'  1 msg enviada, sem retorno:  {len(um_envio)}')
print(f'  2 msgs enviadas, sem retorno:{len(dois_envios)}')
print(f'  3+ msgs, SEM RETORNO:        {len(sem_retorno)}  ← RELATÓRIO')

# CSV
ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
csv_path = rf'C:\Users\SVOBODA\Desktop\DASHBOARD\sem_retorno_{ts}.csv'
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Nome', 'Telefone', 'Msgs Enviadas', 'Msgs Recebidas', 'Ultima Msg Enviada'])
    for d in sem_retorno:
        ultima = ''
        if d['ultima_ts']:
            try:
                ultima = dt.datetime.fromtimestamp(d['ultima_ts']/1000).strftime('%d/%m/%Y %H:%M')
            except: pass
        w.writerow([d['nome'], d['telefone'], d['enviadas'], d['recebidas'], ultima])

print(f'\n[OK] Relatório CSV: {csv_path}')

# Preview
print('\n' + '='*72)
print(f'{"NOME":<30} {"TELEFONE":<16} {"ENV":>5}  ULTIMA MSG')
print('='*72)
for d in sem_retorno[:50]:
    nome = (d['nome'] or 'Sem nome')[:29]
    tel  = d['telefone'][:15]
    ultima = ''
    if d['ultima_ts']:
        try: ultima = dt.datetime.fromtimestamp(d['ultima_ts']/1000).strftime('%d/%m %H:%M')
        except: pass
    print(f'{nome:<30} {tel:<16} {d["enviadas"]:>5}  {ultima}')
if len(sem_retorno) > 50:
    print(f'\n... +{len(sem_retorno)-50} no CSV')
print(f'\nTOTAL: {len(sem_retorno)} clientes — 3+ disparos sem nenhum retorno.')
