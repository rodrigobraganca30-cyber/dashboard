"""
auth_api.py - Micro API para gerenciar usuarios do dashboard.
Roda no servidor: python3 /docker/dashboard/auth_api.py
Porta: 5050 (interno, Nginx faz proxy para /api/auth/)
"""
import os
import json
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler

AUTH_DIR = '/docker/dashboard/html/_auth'
USUARIOS_FILE = os.path.join(AUTH_DIR, 'usuarios.json')

os.makedirs(AUTH_DIR, exist_ok=True)


def sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def ler_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)


class AuthHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        return json.loads(body.decode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ('/usuarios', '/usuarios/'):
            usuarios = ler_usuarios()
            safe = [{"usuario": u["usuario"], "nome": u["nome"], "perfil": u.get("perfil", "user")} for u in usuarios]
            self._json_response(safe)
        else:
            self._json_response({'erro': 'Rota nao encontrada'}, 404)

    def do_POST(self):
        if self.path in ('/login', '/login/'):
            try:
                data = self._read_body()
                usuario = data.get('usuario', '').strip().lower()
                senha = data.get('senha', '').strip()
                if not usuario or not senha:
                    self._json_response({'ok': False, 'error': 'Preencha todos os campos'}, 400)
                    return
                usuarios = ler_usuarios()
                for u in usuarios:
                    if u['usuario'] == usuario and u['hash'] == sha256(senha):
                        self._json_response({'ok': True, 'nome': u['nome'], 'perfil': u.get('perfil', 'user')})
                        return
                self._json_response({'ok': False, 'error': 'Usuario ou senha incorretos'}, 401)
            except Exception as e:
                self._json_response({'ok': False, 'error': str(e)}, 500)

        elif self.path in ('/usuarios', '/usuarios/'):
            try:
                data = self._read_body()
                usuario = data.get('usuario', '').strip().lower()
                senha = data.get('senha', '').strip()
                nome = data.get('nome', '').strip()
                perfil = data.get('perfil', 'user')
                if not usuario or not senha or not nome:
                    self._json_response({'error': 'Campos obrigatorios: usuario, senha, nome'}, 400)
                    return
                usuarios = ler_usuarios()
                for u in usuarios:
                    if u['usuario'] == usuario:
                        self._json_response({'error': 'Usuario ja existe'}, 409)
                        return
                usuarios.append({'usuario': usuario, 'hash': sha256(senha), 'nome': nome, 'perfil': perfil})
                salvar_usuarios(usuarios)
                self._json_response({'ok': True, 'message': f'Usuario {usuario} criado'}, 201)
            except Exception as e:
                self._json_response({'error': str(e)}, 500)
        else:
            self._json_response({'erro': 'Rota nao encontrada'}, 404)

    def do_PUT(self):
        if self.path.startswith('/usuarios/'):
            try:
                target = self.path.split('/')[-1].lower()
                data = self._read_body()
                usuarios = ler_usuarios()
                for u in usuarios:
                    if u['usuario'] == target:
                        if 'senha' in data and data['senha']:
                            u['hash'] = sha256(data['senha'])
                        if 'nome' in data:
                            u['nome'] = data['nome']
                        if 'perfil' in data:
                            u['perfil'] = data['perfil']
                        salvar_usuarios(usuarios)
                        self._json_response({'ok': True})
                        return
                self._json_response({'error': 'Usuario nao encontrado'}, 404)
            except Exception as e:
                self._json_response({'error': str(e)}, 500)
        else:
            self._json_response({'erro': 'Rota nao encontrada'}, 404)

    def do_DELETE(self):
        if self.path.startswith('/usuarios/'):
            try:
                target = self.path.split('/')[-1].lower()
                usuarios = ler_usuarios()
                usuarios = [u for u in usuarios if u['usuario'] != target]
                salvar_usuarios(usuarios)
                self._json_response({'ok': True})
            except Exception as e:
                self._json_response({'error': str(e)}, 500)
        else:
            self._json_response({'erro': 'Rota nao encontrada'}, 404)

    def log_message(self, format, *args):
        pass  # Silenciar logs

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5050), AuthHandler)
    print("Auth API rodando na porta 5050")
    server.serve_forever()
