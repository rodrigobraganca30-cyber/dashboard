import re

content = open('/docker/dashboard/html/index.html').read()
lines = content.split('\n')

# Encontra o script block que contem waHandleFile
start_line = None
end_line = None
in_block = False
for i, line in enumerate(lines):
    if not in_block and '<script>' in line and i > 3100 and i < 3200:
        start_line = i
        in_block = True
    if in_block and '</script>' in line and i > start_line:
        end_line = i
        break

print(f'Script block: linha {start_line+1} ate {end_line+1}')
inner = '\n'.join(lines[start_line+1:end_line])
print(f'Tamanho do bloco: {len(inner)} chars')

# Procura por </script> dentro do bloco (causaria fechamento prematuro no browser)
matches = list(re.finditer(r'</script>', inner, re.IGNORECASE))
print(f'</script> internos: {len(matches)}')
for m in matches[:5]:
    ctx = inner[max(0,m.start()-80):m.end()+20]
    print(f'  -> Contexto: {repr(ctx)}')

# Tambem verifica se waHandleFile esta no bloco
if 'waHandleFile' in inner:
    print('[OK] waHandleFile encontrado no bloco')
else:
    print('[ERRO] waHandleFile NAO encontrado no bloco!')

# Verifica erro de sintaxe com node
import subprocess, tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(inner)
    fname = f.name
result = subprocess.run(['node', '--check', fname], capture_output=True, text=True)
if result.returncode == 0:
    print('[OK] Sem erro de sintaxe JS no bloco')
else:
    print('[ERRO JS]', result.stderr[:300])
os.unlink(fname)
