import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('[1] Modal de importação no HTML live:')
i, o, e = c.exec_command("grep -c 'wa-import-modal' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    wa-import-modal: {o.read().decode().strip()} refs')

print('\n[2] waHandleFile no HTML live:')
i, o, e = c.exec_command("grep -c 'waHandleFile' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    waHandleFile: {o.read().decode().strip()} refs')

print('\n[3] waParseCSV no HTML live:')
i, o, e = c.exec_command("grep -c 'waParseCSV' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    waParseCSV: {o.read().decode().strip()} refs')

print('\n[4] waShowImportModal:')
i, o, e = c.exec_command("grep -c 'waShowImportModal' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    waShowImportModal: {o.read().decode().strip()} refs')

print('\n[5] waFinishImport:')
i, o, e = c.exec_command("grep -c 'waFinishImport' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    waFinishImport: {o.read().decode().strip()} refs')

print('\n[6] XLSX lib:')
i, o, e = c.exec_command("grep -c 'xlsx' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    XLSX: {o.read().decode().strip()} refs')

print('\n[7] accept do input file:')
i, o, e = c.exec_command("grep -o 'accept=\"[^\"]*\"' /docker/dashboard/html/index.html | head -3")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

print('\n[8] Erros JS no console (se alguma func nao existe):')
i, o, e = c.exec_command("grep -n 'function waHandleFile\\|function waParseCSV\\|function waShowImport\\|function waFinishImport\\|function waCloseImport' /docker/dashboard/html/index.html | head -10")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip() or '    NENHUMA dessas funções encontrada!')

c.close()
