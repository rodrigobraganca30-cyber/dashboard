#!/usr/bin/env python3
"""
Adiciona chamada a injetar_templates.py no final do post_inject.py
para que o template Meta seja injetado junto com os outros patches.
"""
ARQUIVO = '/docker/dashboard/post_inject.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    src = f.read()

if 'injetar_templates' in src:
    print('[OK] injetar_templates já presente no post_inject.py')
    exit(0)

# Adiciona import subprocess no topo se necessário
if 'import subprocess' not in src:
    src = src.replace('import os\n', 'import os\nimport subprocess\n', 1)

# Adiciona função inject_meta_templates
FUNC = '''
# 12. META TEMPLATES (injetar_templates.py)
def inject_meta_templates(html):
    import subprocess, sys, os
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "injetar_templates.py")
    if not os.path.exists(script):
        log("[12] AVISO: injetar_templates.py nao encontrado"); return html
    r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                       cwd=os.path.dirname(script))
    if r.returncode == 0:
        log("[12] Meta Templates INJETADO")
        # Relê o arquivo pois injetar_templates salva direto no disco
        with open(DASH, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        log("[12] AVISO injetar_templates: " + r.stderr[:100])
    return html

'''

# Insere antes de # MAIN
MAIN_MARKER = "# MAIN\nif __name__ == \"__main__\":"
src = src.replace(MAIN_MARKER, FUNC + MAIN_MARKER, 1)

# Adiciona chamada no main
OLD_SAVE = "    html = inject_wa_mapping_modal(html)\n    save(DASH, html)"
NEW_SAVE = ("    html = inject_wa_mapping_modal(html)\n"
            "    html = inject_meta_templates(html)\n"
            "    save(DASH, html)")

if OLD_SAVE in src:
    src = src.replace(OLD_SAVE, NEW_SAVE, 1)
    print('[OK] inject_meta_templates adicionado ao main()')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(src)

print('[DONE] post_inject.py atualizado com Meta Templates')
