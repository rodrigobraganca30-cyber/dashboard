#!/usr/bin/env python3
ARQUIVO = '/docker/whatsapp-agenda/backend/index.js'

with open(ARQUIVO) as f:
    content = f.read()

OLD = """      components: [{
        type: 'BODY',
        text: body_text
      }]"""

NEW = """      components: [(() => {
        const comp = { type: 'BODY', text: body_text };
        const vars = body_text.match(/{{[0-9]+}}/g);
        if (vars) {
          comp.example = { body_text: [vars.map((_, i) => 'exemplo' + (i + 1))] };
        }
        return comp;
      })()]"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w') as f:
        f.write(content)
    print('[OK] Fix do campo example aplicado no backend')
else:
    print('[ERRO] Ancora nao encontrada')
