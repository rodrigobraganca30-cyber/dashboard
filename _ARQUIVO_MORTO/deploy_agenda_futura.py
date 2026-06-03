"""
deploy_agenda_futura.py
=======================
Faz upload do robo_agenda_futura.py e setup_cron_agenda_futura.sh para o VPS,
cria a pasta de dados e configura o cron job automaticamente.
"""
import paramiko
import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VPS_HOST = "187.77.240.87"
VPS_USER = "root"
SSH_KEY  = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')

PASTA_LOCAL = os.path.dirname(os.path.abspath(__file__))
REMOTO_SRC  = "/opt/painel_robo/src"

ARQUIVOS = [
    ("robo_agenda_futura.py",       f"{REMOTO_SRC}/robo_agenda_futura.py"),
    ("setup_cron_agenda_futura.sh", f"{REMOTO_SRC}/setup_cron_agenda_futura.sh"),
]

def sep(msg):
    print(f"\n{'='*50}\n {msg}\n{'='*50}")

pkey = paramiko.RSAKey.from_private_key_file(SSH_KEY)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(VPS_HOST, username=VPS_USER, pkey=pkey)

sep("Upload dos arquivos")
sftp = c.open_sftp()
for local_name, remoto_path in ARQUIVOS:
    local_path = os.path.join(PASTA_LOCAL, local_name)
    if os.path.exists(local_path):
        sftp.put(local_path, remoto_path)
        print(f"  ✅ {local_name} → {remoto_path}")
    else:
        print(f"  [AVISO] Arquivo não encontrado: {local_path}")
sftp.close()

sep("Configurando permissões e cron")
cmds = [
    f"chmod +x {REMOTO_SRC}/setup_cron_agenda_futura.sh",
    f"chmod +x {REMOTO_SRC}/robo_agenda_futura.py",
    f"bash {REMOTO_SRC}/setup_cron_agenda_futura.sh",
]
for cmd in cmds:
    print(f"\n  CMD: {cmd}")
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace').strip()
    err = e.read().decode('utf-8', errors='replace').strip()
    if out:
        print(f"  {out}")
    if err:
        print(f"  [ERR] {err[:300]}")

c.close()
print("\n✅ Deploy concluído!")
print(f"   Robô: {REMOTO_SRC}/robo_agenda_futura.py")
print("   Cron: 05:00 AM diário")
print(f"\n   Para rodar agora:")
print(f"   python3 {REMOTO_SRC}/robo_agenda_futura.py")
