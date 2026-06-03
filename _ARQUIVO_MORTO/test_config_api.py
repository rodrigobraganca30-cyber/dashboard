import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ip = '172.22.0.7'

# 1. Backend logs (check if it started correctly)
print("=== BACKEND LOGS ===")
i, o, e = c.exec_command("docker logs backend-agenda --tail 10 2>&1")
print(o.read().decode().strip())

# Get actual IP
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
ip = o.read().decode().strip()
print(f"\nIP: {ip}")

# 2. Test /config endpoint
print("\n=== GET /config ===")
i, o, e = c.exec_command(f"curl -s -H 'Referer: https://svoboda.rtflowapp.com/' http://{ip}:3001/config")
out = o.read().decode('utf-8', errors='replace').strip()
print(out[:800])

# 3. Test /config/btn_status_map
print("\n\n=== GET /config/btn_status_map ===")
i, o, e = c.exec_command(f"curl -s -H 'Referer: https://svoboda.rtflowapp.com/' http://{ip}:3001/config/btn_status_map")
print(o.read().decode('utf-8', errors='replace').strip()[:500])

# 4. Test /config/keywords_status
print("\n\n=== GET /config/keywords_status ===")
i, o, e = c.exec_command(f"curl -s -H 'Referer: https://svoboda.rtflowapp.com/' http://{ip}:3001/config/keywords_status")
print(o.read().decode('utf-8', errors='replace').strip()[:500])

c.close()
