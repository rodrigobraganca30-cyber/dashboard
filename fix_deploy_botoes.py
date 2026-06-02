"""
fix_deploy_botoes.py — Deploy dos scripts corrigidos para VPS + cleanup dos botoes duplicados.
Uso unico. Pode deletar apos rodar.
"""
import paramiko, json, os

PASTA = r"C:\Users\SVOBODA\Desktop\DASHBOARD"
cfg = json.load(open(os.path.join(PASTA, "config_servidor.json")))

print("=" * 50)
print("FIX: Deploy scripts corrigidos para VPS")
print("=" * 50)

# Conectar SFTP
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Tenta chave privada primeiro, fallback para senha
pkey = None
key_path = os.path.expanduser("~/.ssh/id_rsa")
if os.path.exists(key_path):
    try:
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
    except:
        pass

if pkey:
    client.connect(cfg['HOST'], port=int(cfg['PORT']), username=cfg['USER'], pkey=pkey)
else:
    client.connect(cfg['HOST'], port=int(cfg['PORT']), username=cfg['USER'], password=cfg.get('PASS',''))

sftp = client.open_sftp()

# 1. Upload post_inject.py corrigido
local_pi = os.path.join(PASTA, "post_inject.py")
remote_pi = "/docker/dashboard/post_inject.py"
print(f"[SFTP] Enviando post_inject.py corrigido...")
sftp.put(local_pi, remote_pi)
print(f"[OK] post_inject.py enviado ({os.path.getsize(local_pi)} bytes)")

# 2. Upload injetar_admin_btn.py (deprecated)
local_ab = os.path.join(PASTA, "injetar_admin_btn.py")
remote_ab = "/docker/dashboard/injetar_admin_btn.py"
print(f"[SFTP] Enviando injetar_admin_btn.py (deprecated)...")
sftp.put(local_ab, remote_ab)
print(f"[OK] injetar_admin_btn.py enviado ({os.path.getsize(local_ab)} bytes)")

# 3. Upload run_dashboard_pipeline.sh corrigido
local_sh = os.path.join(PASTA, "run_dashboard_pipeline.sh")
remote_sh = "/docker/dashboard/run_dashboard_pipeline.sh"
print(f"[SFTP] Enviando run_dashboard_pipeline.sh corrigido...")
sftp.put(local_sh, remote_sh)
print(f"[OK] run_dashboard_pipeline.sh enviado ({os.path.getsize(local_sh)} bytes)")

sftp.close()

# 4. Rodar post_inject.py no servidor para limpar duplicacao existente
print("\n[...] Rodando post_inject.py no servidor para cleanup...")
stdin, stdout, stderr = client.exec_command(
    "cd /docker/dashboard && python3 post_inject.py 2>&1",
    timeout=60
)
out = stdout.read().decode('utf-8', errors='replace')
print(out)

# 5. Verificar resultado: contar quantos botoes "Sair" existem no HTML
print("\n[...] Verificando resultado...")
stdin, stdout, stderr = client.exec_command(
    'grep -c "Sair" /docker/dashboard/html/index.html',
    timeout=10
)
count_sair = stdout.read().decode().strip()
print(f"[CHECK] Quantidade de 'Sair' no HTML: {count_sair}")

stdin, stdout, stderr = client.exec_command(
    'grep -c "TF_ADMIN_BTNS" /docker/dashboard/html/index.html',
    timeout=10
)
count_tf = stdout.read().decode().strip()
print(f"[CHECK] Quantidade de 'TF_ADMIN_BTNS' no HTML: {count_tf}")

if count_tf == "0" and int(count_sair) <= 2:
    print("\n[SUCESSO] Botoes duplicados corrigidos! Apenas 1 conjunto de botoes admin.")
else:
    print(f"\n[AVISO] Verificar manualmente — TF_ADMIN_BTNS={count_tf}, Sair={count_sair}")

client.close()
print("\n[DONE] Deploy concluido!")
