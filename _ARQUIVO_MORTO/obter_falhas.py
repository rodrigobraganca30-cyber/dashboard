"""
obter_falhas.py
Conecta no Redis do VPS, busca todos os clientes e seus status, e gera um relatório
apenas dos clientes onde as mensagens NÃO CHEGARAM (numero-nao-pertence ou falhas).
Usando MGET otimizado em chunks de 500 chaves para ser ultra rápido.
"""
import paramiko, os, sys, json, csv, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Script que vai rodar NO VPS para coletar status em chunks de 500 (super rápido)
SCRIPT_CONTEUDO = r'''#!/usr/bin/env python3
import subprocess, json, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def redis_list(cmd):
    r = subprocess.run(["docker","exec","redis-agenda","redis-cli"] + cmd, capture_output=True)
    return [l for l in r.stdout.decode("utf-8", errors="replace").strip().split("\n") if l]

print("Coletando status keys...", file=sys.stderr)
status_keys = redis_list(["KEYS", "agenda:status:*"])
print(f"Total status keys: {len(status_keys)}", file=sys.stderr)

dados_brutos = []
chunk_size = 500
for i in range(0, len(status_keys), chunk_size):
    chunk = status_keys[i:i+chunk_size]
    print(f"Processando chunk {i//chunk_size + 1}...", file=sys.stderr)
    r = subprocess.run(["docker","exec","redis-agenda","redis-cli", "MGET"] + chunk, capture_output=True)
    linhas = r.stdout.decode("utf-8", errors="replace").strip().split("\n")
    # Limpa linhas vazias ou nulas
    dados_brutos.extend(linhas)

resultado = []
for sk, raw in zip(status_keys, dados_brutos):
    if not raw or raw == "(nil)" or not raw.startswith("{"):
        continue
        
    m = re.match(r"agenda:status:wa_(\d+)_(.*)", sk)
    if not m:
        continue
    
    phone = m.group(1)
    nome = m.group(2).replace("_", " ").title()
    
    try:
        data = json.loads(raw)
    except:
        continue
        
    status = data.get("status", "")
    obs = data.get("obs", "")
    ts = data.get("ts", 0)
    
    resultado.append({
        "nome": nome,
        "telefone": phone,
        "status": status,
        "obs": obs,
        "ts": ts
    })

with open("/tmp/status_wpp.json", "w", encoding="utf-8") as f:
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
with sftp.open('/tmp/analise_status.py', 'w') as f:
    f.write(SCRIPT_CONTEUDO.encode('utf-8'))
sftp.close()
print('[OK] Script enviado para /tmp/analise_status.py')

# Executa no VPS
print('[...] Executando coleta de status otimizada...')
stdin, stdout, stderr = client.exec_command(
    'python3 /tmp/analise_status.py 2>/tmp/analise_status_err.txt',
    timeout=60
)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f'[VPS] {out}')

# Lê stderr para progress
stdin2, stdout2, _ = client.exec_command('cat /tmp/analise_status_err.txt')
print('[PROGRESS ERR]', stdout2.read().decode('utf-8', errors='replace').strip())

if 'OK' not in out:
    print('[ERRO] Script não terminou com OK')
    sys.exit(1)

# Baixa o resultado JSON
print('[...] Baixando resultado...')
sftp2 = client.open_sftp()
with sftp2.open('/tmp/status_wpp.json', 'r') as f:
    dados = json.loads(f.read().decode('utf-8'))
sftp2.close()
client.close()

print(f'[OK] Total registros de status baixados: {len(dados)}')

# Filtra apenas os que não chegaram (status = 'numero-nao-pertence' ou similares de falha)
falhas = []
for d in dados:
    st = d['status']
    # 'numero-nao-pertence' é o padrão do sistema para falha de entrega por número inválido
    if st in ['numero-nao-pertence', 'failed', 'error', 'invalido', 'sem-contato']:
        falhas.append(d)

print(f'Total de falhas encontradas: {len(falhas)}')

# Salva CSV local
ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
csv_path = rf'C:\Users\SVOBODA\Desktop\DASHBOARD\nao_entregues_{ts}.csv'
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Nome', 'Telefone', 'Status', 'Observacao', 'Data Falha'])
    for d in falhas:
        data_str = ''
        if d['ts']:
            try:
                # Se for milissegundos
                ts_val = d['ts'] / 1000 if d['ts'] > 1e11 else d['ts']
                data_str = dt.datetime.fromtimestamp(ts_val).strftime('%d/%m/%Y %H:%M')
            except:
                pass
        w.writerow([d['nome'], d['telefone'], d['status'], d['obs'], data_str])

print(f'[OK] CSV de falhas gerado: {csv_path}')
