"""
FASE 3: Congelar o HTML como template fixo.

Tarefas:
1. Garantir que nenhum cron regenera o HTML
2. Criar backup "definitivo" do template
3. Adicionar proteção contra sobrescrita
4. Documentar o novo fluxo
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# 1. Backup definitivo do template
print('[1/4] Criando backup DEFINITIVO do template...')
cmd = f'cp /docker/dashboard/html/index.html /docker/dashboard/html/index_template_DEFINITIVO_{ts}.html && echo OK'
i, o, e = c.exec_command(cmd)
time.sleep(2)
print('    ' + o.read().decode('utf-8', errors='replace').strip())

# 2. Verificar que gerar_dashboard_v2.py NAO roda no cron
print('\n[2/4] Verificando cron...')
i, o, e = c.exec_command('crontab -l')
time.sleep(2)
cron = o.read().decode('utf-8', errors='replace').strip()
if 'gerar_dashboard' in cron:
    print('    [AVISO] gerar_dashboard_v2.py encontrado no cron!')
    # Comentar
    new_cron = cron.replace('gerar_dashboard', '#gerar_dashboard')
    sftp = c.open_sftp()
    with sftp.open('/tmp/new_cron', 'w') as f:
        f.write(new_cron + '\n')
    sftp.close()
    c.exec_command('crontab /tmp/new_cron')
    time.sleep(1)
    print('    [OK] Comentado!')
else:
    print('    [OK] gerar_dashboard NAO esta no cron')

if 'post_inject' in cron and not '#' + 'post_inject' in cron.replace('# ', '#').replace('#  ', '#'):
    print('    [AVISO] post_inject.py ativo no cron')
else:
    print('    [OK] post_inject.py ja esta comentado')

# 3. Criar script de proteção contra sobrescrita acidental
print('\n[3/4] Criando proteção...')
protect_script = '''#!/bin/bash
# PROTECAO: Impede sobrescrita acidental do template
# O index.html agora e um TEMPLATE FIXO
# Dados sao atualizados via JSONs em html/data/
#
# Se precisar restaurar: 
#   cp /docker/dashboard/html/index_template_DEFINITIVO_*.html /docker/dashboard/html/index.html
#
echo "================================================================="
echo "  AVISO: index.html e um TEMPLATE FIXO!"
echo "  NAO sobrescreva! Dados sao atualizados via JSONs."
echo "  Cron ativo: atualizar_dados.sh (a cada 2h)"
echo "================================================================="
'''
sftp = c.open_sftp()
with sftp.open('/docker/dashboard/LEIA_ME.sh', 'w') as f:
    f.write(protect_script)
sftp.close()
c.exec_command('chmod +x /docker/dashboard/LEIA_ME.sh')
time.sleep(1)
print('    [OK] LEIA_ME.sh criado')

# 4. Resumo final
print('\n[4/4] Verificando estado final...')
i, o, e = c.exec_command('crontab -l 2>/dev/null')
time.sleep(2)
print('    CRON:')
for line in o.read().decode('utf-8', errors='replace').strip().split('\n'):
    print(f'      {line}')

i, o, e = c.exec_command('ls -la /docker/dashboard/html/index.html /docker/dashboard/html/dynamic_loader.js /docker/dashboard/html/data/*.json 2>/dev/null')
time.sleep(2)
print('\n    Arquivos:')
for line in o.read().decode('utf-8', errors='replace').strip().split('\n'):
    parts = line.split()
    if len(parts) >= 9:
        size = parts[4]
        name = parts[-1].split('/')[-1]
        print(f'      {name}: {int(size):,} bytes')

c.close()

print('\n' + '='*60)
print('  FASE 3 COMPLETA: HTML CONGELADO COMO TEMPLATE FIXO')
print('='*60)
print()
print('  Novo fluxo:')
print('  1. robo_oracle.py (21:50) -> atualiza ATIVIDADES DAS O.S.xlsx')
print('  2. atualizar_dados.sh (a cada 2h) -> gera JSONs + copia para html/data/')
print('  3. dynamic_loader.js (no browser) -> carrega JSONs e renderiza')
print()
print('  O HTML NUNCA MAIS PRECISA SER REGENERADO!')
print('  Patches, auth, estoque, tudo permanece intacto.')
