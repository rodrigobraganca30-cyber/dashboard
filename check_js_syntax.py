import re, subprocess, tempfile, os

content = open('/docker/dashboard/html/index.html').read()

# Pega o maior bloco script (o principal)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print('Total blocos script:', len(scripts))
for i, s in enumerate(scripts):
    print(f'Script {i}: {len(s)} chars')

# Testa o maior script com node
biggest = max(scripts, key=len)
print(f'\nTestando maior script ({len(biggest)} chars) com node...')
with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(biggest)
    fname = f.name

result = subprocess.run(['node', '--check', fname], capture_output=True, text=True)
if result.returncode == 0:
    print('[OK] Sem erros de sintaxe JS!')
else:
    print('[ERRO] Erro de sintaxe JS:')
    print(result.stderr[:500])
os.unlink(fname)
