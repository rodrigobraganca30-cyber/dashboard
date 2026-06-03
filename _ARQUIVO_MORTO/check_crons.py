import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("=== CRONTAB ROOT ===")
i, o, e = c.exec_command("crontab -l 2>&1")
print(o.read().decode().strip())

print("\n=== CRONTAB DE OUTROS USERS ===")
i, o, e = c.exec_command("cat /etc/crontab 2>/dev/null")
print(o.read().decode().strip())

print("\n=== CRON.D ===")
i, o, e = c.exec_command("ls -la /etc/cron.d/ 2>/dev/null")
print(o.read().decode().strip())

print("\n=== PROCURA 'whatsapp_agenda_gen' EM CRONS ===")
i, o, e = c.exec_command("grep -r 'whatsapp_agenda_gen' /etc/cron* /var/spool/cron* 2>/dev/null")
out = o.read().decode().strip()
print(out if out else "(nenhuma referencia encontrada)")

print("\n=== PROCURA 'post_inject' EM CRONS ===")
i, o, e = c.exec_command("grep -r 'post_inject\\|inject' /etc/cron* /var/spool/cron* 2>/dev/null")
out = o.read().decode().strip()
print(out if out else "(nenhuma referencia encontrada)")

print("\n=== PROCURA POR PROCESSAR_DADOS CRON ===")
i, o, e = c.exec_command("grep -r 'processar_dados' /etc/cron* /var/spool/cron* 2>/dev/null")
out = o.read().decode().strip()
print(out if out else "(nenhuma referencia encontrada)")

c.close()
