"""
injetar_auth.py — Injeta verificacao de autenticacao no index.html.
Roda no servidor: python3 /docker/dashboard/injetar_auth.py
"""
import os

INDEX_HTML = '/docker/dashboard/html/index.html'
AUTH_MARKER = '<!-- TF_AUTH_CHECK -->'

AUTH_SCRIPT = '''<!-- TF_AUTH_CHECK -->
<script>
if (sessionStorage.getItem('tf_auth') !== 'ok') {
  window.location.replace('login.html');
}
</script>
'''

def main():
    if not os.path.exists(INDEX_HTML):
        print(f"[ERRO] {INDEX_HTML} nao encontrado!")
        return

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    if AUTH_MARKER in html:
        print("[OK] Verificacao de auth ja esta no index.html")
        return

    # Injeta logo apos <head>
    target = '<head>'
    # Tambem funciona com \r\n
    for t in ['<head>\r\n', '<head>\n', '<head>']:
        pos = html.find(t)
        if pos != -1:
            insert_pos = pos + len(t)
            html = html[:insert_pos] + AUTH_SCRIPT + html[insert_pos:]
            break
    else:
        print("[ERRO] Nao encontrou <head> no index.html")
        return

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print("[OK] Verificacao de autenticacao injetada no index.html!")
    print("     Usuarios sem sessao serao redirecionados para login.html")

if __name__ == '__main__':
    main()
