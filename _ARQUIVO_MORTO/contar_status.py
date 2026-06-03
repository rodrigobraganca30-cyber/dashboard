"""
contar_status.py
Baixa /tmp/status_wpp.json do VPS e conta todos os status diferentes para sabermos
quais são os status de erro reais salvos no banco.
"""
import paramiko, os, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

sftp = client.open_sftp()
local_json = r'C:\Users\SVOBODA\Desktop\DASHBOARD\status_wpp.json'
sftp.get('/tmp/status_wpp.json', local_json)
sftp.close()
client.close()

print(f'[OK] Arquivo baixado para: {local_json}')

with open(local_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

print(f'Total de registros: {len(dados)}')

# Conta todos os status
status_counts = Counter(d.get('status', '') for d in dados)
print('\n=== Contagem de Status Únicos ===')
for k, v in status_counts.most_common():
    print(f'  "{k}": {v}')

# Vê se tem algum com obs indicando erro
erro_obs = []
for d in dados:
    obs = d.get('obs', '').lower()
    if 'erro' in obs or 'falha' in obs or 'inválido' in obs or 'invalido' in obs or 'não' in obs or 'nao' in obs:
        erro_obs.append(d)

print(f'\nTotal de registros com observação de erro/falha: {len(erro_obs)}')
if erro_obs:
    print('Amostra de observações:')
    for d in erro_obs[:10]:
        print(f"  {d['nome']} ({d['status']}): {d['obs']}")
