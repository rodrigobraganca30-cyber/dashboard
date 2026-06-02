"""
importar_blacklist_inicial.py
Lê relatorio_wpp.json, filtra os números inválidos (os mesmos 531 identificados)
e os importa diretamente para o Set agenda:blacklist no Redis do VPS.
"""
import paramiko, os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Caminho do relatório local
local_json = r'C:\Users\SVOBODA\Desktop\DASHBOARD\relatorio_wpp.json'
if not os.path.exists(local_json):
    print('[ERRO] relatorio_wpp.json não encontrado. Rode relatorio_sem_retorno.py primeiro.')
    sys.exit(1)

with open(local_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Analisa e separa os números que apresentam anomalias (os 531)
numeros_invalidos = []
for d in dados:
    phone_full = d.get('telefone', '')
    if not phone_full:
        continue
        
    num = phone_full.replace('+', '').replace('-', '').replace(' ', '')
    
    invalid = False
    
    # Regras de invalidação
    if len(num) > 13 or (not num.startswith('55') and len(num) > 11):
        invalid = True
    elif num.startswith('55'):
        ddd_e_numero = num[2:]
        if len(ddd_e_numero) < 10:
            invalid = True
        elif len(ddd_e_numero) == 10:
            primeiro_digito = ddd_e_numero[2]
            if primeiro_digito in ['2', '3', '4', '5']:
                invalid = True # Fixo
            else:
                invalid = True # Falta do 9º dígito
        elif len(ddd_e_numero) == 11:
            primeiro_digito = ddd_e_numero[2]
            if primeiro_digito != '9':
                invalid = True # Celular não começa com 9
    else:
        if len(num) < 10:
            invalid = True
        else:
            invalid = True # Sem 55

    if invalid:
        # Limpa caracteres não numéricos em Python:
        clean_num = ''.join(c for c in phone_full if c.isdigit())
        if not clean_num.startswith('55') and len(clean_num) >= 10:
            clean_num = '55' + clean_num
        numeros_invalidos.append(clean_num)

# Remove duplicados
numeros_invalidos = list(set(numeros_invalidos))
print(f'[OK] Total de números inválidos mapeados para Blacklist: {len(numeros_invalidos)}')

# Conecta no VPS via SSH para importar no Redis
ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# Envia comandos SADD em chunks de 100 para não estourar limite do buffer de comando
chunk_size = 100
total_adicionados = 0

print('[...] Gravando números na blacklist do Redis...')
for i in range(0, len(numeros_invalidos), chunk_size):
    chunk = numeros_invalidos[i:i+chunk_size]
    # SADD agenda:blacklist num1 num2 ...
    cmd = f'docker exec redis-agenda redis-cli SADD agenda:blacklist {" ".join(chunk)}'
    stdin, stdout, stderr = client.exec_command(cmd)
    res = stdout.read().decode('utf-8').strip()
    try:
        added = int(res) if res.isdigit() else 0
        total_adicionados += added
    except:
        pass

# Verifica quantidade total de elementos na Blacklist agora
stdin, stdout, stderr = client.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
total_blacklist = stdout.read().decode('utf-8').strip()

client.close()

print(f'\n=== SUCESSO ===')
print(f'  - Chunks enviados.')
print(f'  - Total de números únicos importados nesta sessão: {len(numeros_invalidos)}')
print(f'  - Total atual de números na Blacklist no VPS: {total_blacklist}')
