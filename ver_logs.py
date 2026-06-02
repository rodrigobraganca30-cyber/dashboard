"""
ver_logs.py
Conecta no VPS, lê os logs de erro do container backend-agenda e faz uma análise completa
de todos os tipos de erros de envio que aconteceram no histórico.
"""
import paramiko, os, sys, re, json
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

print('[...] Coletando logs de "Falha envio" do container backend-agenda...')
stdin, stdout, stderr = client.exec_command(
    'docker logs backend-agenda 2>&1 | grep -i "Falha envio"'
)
logs_raw = stdout.read().decode('utf-8', errors='replace')
client.close()

linhas = [l for l in logs_raw.split('\n') if l.strip()]
print(f'Total de logs de falha encontrados: {len(linhas)}')

errors_parsed = []
for l in linhas:
    try:
        data = json.loads(l)
        nome = data.get('nome', 'Desconhecido')
        err = data.get('error', {})
        
        err_msg = ""
        err_code = 0
        
        if isinstance(err, dict):
            # Formato Meta API
            meta_err = err.get('error', {})
            if isinstance(meta_err, dict):
                err_msg = meta_err.get('message', '')
                err_code = meta_err.get('code', 0)
            else:
                err_msg = str(err)
        else:
            err_msg = str(err)
            
        errors_parsed.append({
            'nome': nome,
            'code': err_code,
            'message': err_msg,
            'raw': err
        })
    except Exception as e:
        # Tenta extrair com regex se não for JSON puro
        m = re.search(r'"nome":"([^"]+)".*?"error":(.*)', l)
        if m:
            errors_parsed.append({
                'nome': m.group(1),
                'code': 0,
                'message': m.group(2)[:100],
                'raw': m.group(2)
            })

# Conta tipos de erros
print('\n=== Contagem de Tipos de Erro ===')
err_types = Counter(e['message'] for e in errors_parsed)
for k, v in err_types.most_common():
    print(f'  - "{k}": {v} vezes')

# Mostra exemplos de erros de número inválido (Receiver is not a valid WhatsApp user)
print('\n=== Exemplos de erros por número não existente ===')
invalid_numbers = [e for e in errors_parsed if 'valid' in e['message'].lower() or 'not a valid' in e['message'].lower() or e['code'] == 131026]
print(f'Total de disparos bloqueados por número não ativo: {len(invalid_numbers)}')
for e in invalid_numbers[:20]:
    print(f"  - {e['nome']}: {e['message']}")
