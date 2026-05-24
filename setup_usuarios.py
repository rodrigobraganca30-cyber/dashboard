"""
setup_usuarios.py — Gera o arquivo de usuarios com hash SHA-256.
Roda no servidor: python3 /docker/dashboard/setup_usuarios.py
"""
import json
import hashlib
import os

AUTH_DIR = '/docker/dashboard/html/_auth'
USUARIOS_FILE = os.path.join(AUTH_DIR, 'usuarios.json')

def sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

# ============ CADASTRO DE USUARIOS ============
# Adicione ou remova usuarios aqui e re-rode o script
USUARIOS = [
    {
        "usuario": "admin",
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "admin"
    },
    {
        "usuario": "svoboda",
        "senha": "svoboda123",
        "nome": "Svoboda",
        "perfil": "admin"
    },
]
# ================================================

def main():
    os.makedirs(AUTH_DIR, exist_ok=True)

    saida = []
    for u in USUARIOS:
        saida.append({
            "usuario": u["usuario"],
            "hash": sha256(u["senha"]),
            "nome": u["nome"],
            "perfil": u.get("perfil", "user")
        })

    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(" Usuarios configurados com sucesso!")
    print("=" * 50)
    for u in USUARIOS:
        print(f"  Usuario: {u['usuario']}  |  Senha: {u['senha']}  |  Perfil: {u.get('perfil', 'user')}")
    print(f"\n  Arquivo: {USUARIOS_FILE}")
    print(f"  Total: {len(saida)} usuario(s)")

if __name__ == '__main__':
    main()
