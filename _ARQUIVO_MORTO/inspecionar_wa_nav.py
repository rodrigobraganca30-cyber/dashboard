import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
script_content = (
    "with open('/docker/dashboard/html/index.html','r',errors='replace') as f:\n"
    "    html = f.read()\n"
    "idx = html.find('function showPage')\n"
    "end = html.find(chr(125), idx) + 1\n"  # chr(125) = '}'
    "print('=== showPage ===')\n"
    "print(html[idx:idx+500])\n"
    "print()\n"
    "idx2 = html.find('.page{')\n"
    "if idx2 < 0: idx2 = html.find('.page ')\n"
    "print('=== .page CSS ===')\n"
    "print(html[idx2:idx2+300] if idx2 >= 0 else 'NOT FOUND')\n"
    "print()\n"
    "idx3 = html.find('class=\"nav\"')\n"
    "print('=== NAV (2500 chars) ===')\n"
    "print(html[idx3:idx3+2500] if idx3 >= 0 else 'NOT FOUND')\n"
    "idx4 = html.find('id=\"whatsapp-agenda\"')\n"
    "print('=== WA PAGE (200 chars) ===')\n"
    "print(html[idx4:idx4+200] if idx4 >= 0 else 'NOT FOUND')\n"
)

with sftp.open('/tmp/inspect_wa3.py', 'w') as f:
    f.write(script_content)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/inspect_wa3.py')
out = o.read().decode('utf-8', errors='replace')
err = e.read().decode('utf-8', errors='replace')
print(out[:8000])
if err: print("STDERR:", err[:400])
c.close()
