import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Extrair o bloco de JS para verificar erros
# Pegar as linhas próximas de onde pode haver erro de f-string (chave solta)
print('[1] Verificando chaves não balanceadas no JS do HTML:')
i, o, e = c.exec_command(r"""python3 -c "
import re
with open('/docker/dashboard/html/index.html','r',encoding='utf-8') as f:
    html = f.read()
# Encontrar todos os blocos <script>
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
print(f'Total de blocos script: {len(scripts)}')
for idx, s in enumerate(scripts):
    # Verificar chaves
    opens = s.count('{')
    closes = s.count('}')
    if opens != closes:
        print(f'  BLOCO {idx}: DESEQUILIBRADO! {{ = {opens}, }} = {closes} (diff: {opens-closes})')
        # Encontrar a linha com o problema
        lines = s.split('\n')
        balance = 0
        for li, line in enumerate(lines):
            balance += line.count('{') - line.count('}')
            if balance < 0:
                print(f'    Possível erro na linha JS {li}: {line[:100]}')
                break
    else:
        print(f'  Bloco {idx}: OK ({opens} chaves)')
"
""")
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

# 2. Verificar se WA_STATUS_LABELS tem chaves corretas
print('\n[2] WA_STATUS_LABELS no HTML:')
i, o, e = c.exec_command("grep 'WA_STATUS_LABELS' /docker/dashboard/html/index.html | head -c 500")
time.sleep(2)
out = o.read().decode('utf-8', errors='replace').strip()
# Contar chaves
opens = out.count('{')
closes = out.count('}')
print(f'    Chaves: {{ = {opens}, }} = {closes}')
if opens != closes:
    print('    ⚠️ DESEQUILIBRADO!')
print(f'    Conteúdo (primeiros 300 chars): {out[:300]}')

c.close()
