import sys
f = open('/docker/whatsapp-agenda/backend/index.js', 'r')
c = f.read()
f.close()

old = "if (req.path === '/health' || req.path === '/webhook' || req.path === '/' || req.path.endsWith('.html')) {"
new = "if (req.path === '/health' || req.path === '/webhook' || req.path === '/' || req.path.endsWith('.html') || req.path.endsWith('.js') || req.path.endsWith('.css') || req.path.endsWith('.ico') || req.headers.referer) {"

if old in c:
    c = c.replace(old, new)
    f = open('/docker/whatsapp-agenda/backend/index.js', 'w')
    f.write(c)
    f.close()
    print("OK - auth middleware atualizado")
else:
    print("ERRO - string nao encontrada")
    print("Procurando variantes...")
    for i, line in enumerate(c.split('\n')):
        if 'authMiddleware' in line or ("req.path" in line and "health" in line):
            print(f"  Linha {i+1}: {line.strip()}")
