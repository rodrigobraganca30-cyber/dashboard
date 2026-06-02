"""
Investiga falhas de entrega (sem WhatsApp) no Redis do backend-agenda.
"""
import subprocess, json, sys, re
import paramiko, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# Verifica os valores de status possíveis (amostra de 50)
print('=== Valores de status únicos ===')
stdin, stdout, stderr = client.exec_command(
    'docker exec redis-agenda redis-cli KEYS "agenda:status:*" 2>/dev/null | head -100 | '
    'xargs -I{} docker exec redis-agenda redis-cli GET "{}" 2>/dev/null | '
    'python3 -c "import sys,json; data=[]; '
    '[data.append(json.loads(l.strip()).get(\'status\',\'\')) for l in sys.stdin if l.strip().startswith(\'{\')] ; '
    'from collections import Counter; [print(f\'{v}: {c}\') for v,c in Counter(data).most_common()]"'
)
print(stdout.read().decode('utf-8', errors='replace'))

# Verifica log de erros do backend-agenda
print('=== Logs de erro do backend-agenda ===')
stdin, stdout, stderr = client.exec_command(
    'docker logs backend-agenda --tail 50 2>&1 | grep -i "error\|fail\|invalid\|not_exist\|nao_existe\|sem_wpp" | head -20'
)
print(stdout.read().decode('utf-8', errors='replace'))

# Verifica no index.js como falhas são registradas
print('=== index.js grep failed/error/invalido ===')
stdin, stdout, stderr = client.exec_command(
    'grep -n "failed\|error\|invalido\|not_exist\|sem_wpp\|nao_tem\|status.*erro\|erro.*status" '
    '/docker/whatsapp-agenda/backend/index.js | head -30'
)
print(stdout.read().decode('utf-8', errors='replace'))

# Verifica campanhas salvas
print('=== Dados de campanhas ===')
stdin, stdout, stderr = client.exec_command(
    'docker exec redis-agenda redis-cli GET "agenda:campaigns" 2>/dev/null | '
    'python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d[:2] if isinstance(d,list) else d, indent=2, ensure_ascii=False))" 2>/dev/null | head -60'
)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
