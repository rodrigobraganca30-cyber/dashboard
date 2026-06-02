"""
BACKUP COMPLETO SVOBODA
=======================
Salva LOCAL + VPS em um único lugar seguro.
Rode com: python backup_completo.py
"""
import os, sys, shutil, datetime, hashlib, json, paramiko

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── CONFIG ───
DASHBOARD = r'C:\Users\SVOBODA\Desktop\DASHBOARD'
BACKUP_ROOT = r'C:\Users\SVOBODA\Desktop\DASHBOARD\BACKUPS'
VPS_HOST = '187.77.240.87'
VPS_USER = 'root'
SSH_KEY = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')

# Extensões a incluir no backup local
INCLUDE_EXT = {'.py', '.html', '.js', '.css', '.bat', '.sh', '.json', '.yml', '.yaml', '.md', '.txt', '.xlsx', '.csv', '.pdf', '.conf', '.zip'}

# Pastas a ignorar
SKIP_DIRS = {'BACKUPS', 'BACKUP_COMPLETO', 'BACKUP_DEFINITIVO', 'backup_', '__pycache__', '.git', 'node_modules'}

def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    ts_display = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    bkp_dir = os.path.join(BACKUP_ROOT, f'BKP_{ts}')
    
    print('=' * 60)
    print(f'  BACKUP COMPLETO SVOBODA — {ts_display}')
    print('=' * 60)
    
    os.makedirs(bkp_dir, exist_ok=True)
    manifest = {'timestamp': ts_display, 'local_files': [], 'vps_files': []}
    
    # ═══════════════════════════════════════════
    # PARTE 1: BACKUP LOCAL
    # ═══════════════════════════════════════════
    print('\n📁 [1/3] Salvando arquivos locais...')
    local_dir = os.path.join(bkp_dir, 'LOCAL')
    count_local = 0
    
    for root, dirs, files in os.walk(DASHBOARD):
        # Skip backup dirs
        dirs[:] = [d for d in dirs if not any(d.startswith(s) for s in SKIP_DIRS)]
        
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in INCLUDE_EXT:
                continue
            
            src = os.path.join(root, fname)
            rel = os.path.relpath(src, DASHBOARD)
            dst = os.path.join(local_dir, rel)
            
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count_local += 1
            manifest['local_files'].append({
                'path': rel,
                'size': os.path.getsize(src),
                'md5': md5(src)
            })
    
    print(f'    ✅ {count_local} arquivos locais salvos')
    
    # ═══════════════════════════════════════════
    # PARTE 2: BACKUP VPS (HTML + configs)
    # ═══════════════════════════════════════════
    print('\n🌐 [2/3] Baixando arquivos da VPS...')
    vps_dir = os.path.join(bkp_dir, 'VPS')
    os.makedirs(vps_dir, exist_ok=True)
    
    try:
        pkey = paramiko.RSAKey.from_private_key_file(SSH_KEY)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(VPS_HOST, username=VPS_USER, pkey=pkey)
        sftp = c.open_sftp()
        
        # Arquivos críticos da VPS
        vps_files = [
            '/docker/dashboard/html/index.html',
            '/docker/dashboard/html/login.html',
            '/docker/dashboard/html/admin_usuarios.html',
            '/docker/dashboard/html/monitor_os_tv.html',
            '/docker/dashboard/post_inject.py',
            '/docker/dashboard/html/index.js',
        ]
        
        count_vps = 0
        for remote_path in vps_files:
            try:
                local_name = os.path.basename(remote_path)
                local_path = os.path.join(vps_dir, local_name)
                sftp.get(remote_path, local_path)
                size = os.path.getsize(local_path)
                manifest['vps_files'].append({
                    'remote': remote_path,
                    'local': local_name,
                    'size': size,
                    'md5': md5(local_path)
                })
                count_vps += 1
                print(f'    ✅ {local_name} ({size:,} bytes)')
            except Exception as e:
                print(f'    ⚠️ {os.path.basename(remote_path)}: {e}')
        
        # Baixar inventários
        inv_dir = os.path.join(vps_dir, 'inventarios')
        os.makedirs(inv_dir, exist_ok=True)
        try:
            inv_files = sftp.listdir('/docker/dashboard/html/inventarios/')
            for inv in inv_files:
                if inv.endswith('.xlsx'):
                    remote = f'/docker/dashboard/html/inventarios/{inv}'
                    local = os.path.join(inv_dir, inv)
                    sftp.get(remote, local)
                    count_vps += 1
            print(f'    ✅ {len([f for f in inv_files if f.endswith(".xlsx")])} inventários baixados')
        except Exception as e:
            print(f'    ⚠️ Inventários: {e}')
        
        sftp.close()
        c.close()
        print(f'    ✅ Total VPS: {count_vps} arquivos')
        
    except Exception as e:
        print(f'    ❌ Erro VPS: {e}')
    
    # ═══════════════════════════════════════════
    # PARTE 3: MANIFESTO + VERIFICAÇÃO
    # ═══════════════════════════════════════════
    print('\n📋 [3/3] Gerando manifesto...')
    
    manifest_path = os.path.join(bkp_dir, 'MANIFESTO.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    # Resumo
    total = count_local + count_vps
    bkp_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(bkp_dir)
        for filename in filenames
    )
    
    # Create a human-readable README
    readme = f"""# BACKUP SVOBODA — {ts_display}

## Conteúdo
- **LOCAL/**: {count_local} arquivos (scripts, planilhas, configs)
- **VPS/**: {count_vps} arquivos (HTML em produção, inventários)
- **MANIFESTO.json**: checksums MD5 de todos os arquivos

## Como Restaurar

### Restaurar LOCAL (scripts e configs):
```
xcopy /E /Y "LOCAL\\*" "C:\\Users\\SVOBODA\\Desktop\\DASHBOARD\\"
```

### Restaurar VPS (HTML em produção):
```python
# Rodar dentro do DASHBOARD:
python -c "
import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)
sftp = c.open_sftp()
sftp.put('VPS/index.html', '/docker/dashboard/html/index.html')
sftp.close()
c.close()
print('VPS restaurada!')
"
```

## Tamanho Total: {bkp_size:,} bytes
"""
    with open(os.path.join(bkp_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f'\n{"=" * 60}')
    print(f'  ✅ BACKUP COMPLETO!')
    print(f'  📂 {bkp_dir}')
    print(f'  📊 {total} arquivos | {bkp_size/1024/1024:.1f} MB')
    print(f'  📁 LOCAL: {count_local} arquivos')
    print(f'  🌐 VPS:   {count_vps} arquivos')
    print(f'{"=" * 60}')

if __name__ == '__main__':
    main()
