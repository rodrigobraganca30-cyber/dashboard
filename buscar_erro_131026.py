"""
buscar_erro_131026.py
Busca nos logs do container backend-agenda e em outros locais do VPS qualquer ocorrência do erro 131026.
"""
import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

print('[...] Procurando nos logs do container backend-agenda pelo erro 131026...')
stdin, stdout, stderr = client.exec_command(
    'docker logs backend-agenda 2>&1 | grep -i "131026"'
)
out1 = stdout.read().decode('utf-8', errors='replace')

print('[...] Procurando em todos os logs de containers por 131026...')
stdin, stdout, stderr = client.exec_command(
    'docker ps -q | xargs -I {} sh -c "echo Container: {}; docker logs {} 2>&1 | grep -i 131026"'
)
out2 = stdout.read().decode('utf-8', errors='replace')

client.close()

print('\n=== Resultados no container backend-agenda ===')
if out1.strip():
    print(out1)
else:
    print('Nenhuma correspondência direta encontrada no backend-agenda.')

print('\n=== Resultados em outros containers ===')
if out2.strip():
    print(out2)
else:
    print('Nenhuma correspondência em outros containers.')
