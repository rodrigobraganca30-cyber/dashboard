#!/usr/bin/env python3
"""
Fix post_inject.py:
- inject_wa_mapping_modal: check muda de 'waShowMappingModal' para 'function waShowMappingModal('
  (evita falso positivo quando a função é chamada mas não definida)
"""
ARQUIVO = '/docker/dashboard/post_inject.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    src = f.read()

# Fix: muda o check de presença para verificar a DEFINIÇÃO da função
OLD = "    if 'waShowMappingModal' in html:\n        log(\"[11] waShowMappingModal OK\"); return html"
NEW = "    if 'function waShowMappingModal(' in html:\n        log(\"[11] waShowMappingModal OK\"); return html"

if OLD in src:
    src = src.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(src)
    print('[OK] Check corrigido: agora verifica definicao, nao apenas chamada')
else:
    print('[ERRO] Anchor nao encontrado')
    # Mostra o que está lá
    import re
    m = re.search(r'waShowMappingModal.*OK.*return html', src)
    if m:
        print('[DIAG]', repr(src[max(0,m.start()-20):m.end()+20]))
