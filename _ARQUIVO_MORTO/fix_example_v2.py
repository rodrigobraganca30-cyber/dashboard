#!/usr/bin/env python3
ARQUIVO = '/docker/whatsapp-agenda/backend/index.js'

with open(ARQUIVO) as f:
    content = f.read()

# Remove a versao anterior (com IIFE) e substitui por algo mais simples
OLD = """      components: [(() => {
        const comp = { type: 'BODY', text: body_text };
        const vars = body_text.match(/{{[0-9]+}}/g);
        if (vars) {
          comp.example = { body_text: [vars.map((_, i) => 'exemplo' + (i + 1))] };
        }
        return comp;
      })()]"""

NEW = """      components: [{
        type: 'BODY',
        text: body_text,
        example: { body_text: [Array.from({length: (body_text.match(/\\{\\{[0-9]+\\}\\}/g) || ['x']).length}, (_, i) => 'exemplo' + (i + 1))] }
      }]"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w') as f:
        f.write(content)
    print('[OK] Fix simplificado aplicado')
else:
    # tenta encontrar o bloco atual para diagnosticar
    idx = content.find('type: \'BODY\'')
    if idx >= 0:
        print('[DIAG] Bloco encontrado em:', content[max(0,idx-100):idx+200])
    else:
        print('[ERRO] Bloco BODY nao encontrado')
