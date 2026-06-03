import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar quais scripts do pipeline existem no VPS
scripts = ['gerar_dashboard_v2.py', 'injetar_auth.py', 'injetar_templates.py', 
           'inject_estoque.py', 'injetar_melhorias.py', 'post_inject.py', 'pos_pipeline_bot.py']

print("=== SCRIPTS DO PIPELINE NO VPS ===")
for s in scripts:
    i, o, e = c.exec_command(f"ls -la /docker/dashboard/{s} 2>&1")
    out = o.read().decode().strip()
    exists = "NO SUCH FILE" not in out.upper()
    print(f"  {'EXISTE' if exists else 'FALTA'}: {s}")

# O post_inject.py mexe na agenda?
print("\n=== POST_INJECT.PY MEXE NA AGENDA? ===")
i, o, e = c.exec_command("grep -i 'agenda\\|whatsapp' /docker/dashboard/post_inject.py 2>/dev/null | head -10")
out = o.read().decode().strip()
print(out if out else "(nao encontrado ou nao menciona agenda)")

# O que cada inject faz?
print("\n=== O QUE CADA INJECT MODIFICA? ===")
for s in ['injetar_auth.py', 'injetar_templates.py', 'inject_estoque.py', 'injetar_melhorias.py']:
    i, o, e = c.exec_command(f"grep -i 'index.html\\|agenda' /docker/dashboard/{s} 2>/dev/null | head -3")
    out = o.read().decode().strip()
    print(f"\n{s}:")
    print(f"  {out[:200] if out else '(nao encontrado)'}")

c.close()
