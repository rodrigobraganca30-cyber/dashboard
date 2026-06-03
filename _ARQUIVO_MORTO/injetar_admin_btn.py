"""
injetar_admin_btn.py — Injeta botao de admin e logout no index.html.
Roda no servidor: python3 /docker/dashboard/injetar_admin_btn.py
"""
import os

INDEX_HTML = '/docker/dashboard/html/index.html'
ADMIN_MARKER = '<!-- TF_ADMIN_BTNS -->'

ADMIN_BTNS = '''<!-- TF_ADMIN_BTNS -->
<div style="position:fixed;top:12px;right:16px;z-index:9999;display:flex;gap:8px;align-items:center;">
  <span id="tf-user-label" style="font-size:11px;color:#7d8590;font-family:'Inter',sans-serif;margin-right:4px;"></span>
  <a href="admin_usuarios.html" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:8px;background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.25);color:#a78bfa;font-size:12px;font-weight:600;font-family:'Inter',sans-serif;text-decoration:none;transition:all 0.2s;cursor:pointer;" onmouseover="this.style.background='rgba(124,58,237,0.25)'" onmouseout="this.style.background='rgba(124,58,237,0.12)'"><i class="fas fa-users-cog"></i> Usuários</a>
  <button onclick="sessionStorage.clear();window.location.href='login.html'" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:8px;background:rgba(255,77,109,0.1);border:1px solid rgba(255,77,109,0.2);color:#ff6b81;font-size:12px;font-weight:600;font-family:'Inter',sans-serif;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,77,109,0.2)'" onmouseout="this.style.background='rgba(255,77,109,0.1)'"><i class="fas fa-sign-out-alt"></i> Sair</button>
</div>
<script>
  var _u = sessionStorage.getItem('tf_user');
  if (_u) document.getElementById('tf-user-label').textContent = 'Olá, ' + _u;
</script>
'''

def main():
    # DEPRECATED: botoes admin agora sao injetados exclusivamente pelo post_inject.py
    print("[SKIP] injetar_admin_btn.py DEPRECATED — botoes admin sao injetados pelo post_inject.py")
    return

    # Codigo abaixo nunca executa (mantido para referencia)
    if not os.path.exists(INDEX_HTML):
        print(f"[ERRO] {INDEX_HTML} nao encontrado!")
        return

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    if ADMIN_MARKER in html:
        print("[OK] Botoes de admin ja estao no index.html")
        return

    # Se o post_inject.py já injetou os botões (melhor versão), não duplicar
    if 'btn-logout-dash' in html:
        print("[OK] Botoes de admin ja injetados pelo post_inject.py — pulando")
        return

    # Injeta logo apos <body>
    for tag in ['<body>\r\n', '<body>\n', '<body>']:
        pos = html.find(tag)
        if pos != -1:
            insert_pos = pos + len(tag)
            html = html[:insert_pos] + ADMIN_BTNS + html[insert_pos:]
            break
    else:
        print("[ERRO] Nao encontrou <body> no index.html")
        return

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print("[OK] Botoes de 'Usuarios' e 'Sair' injetados no index.html!")

if __name__ == '__main__':
    main()
