"""
flow_api.py - Motor de Fluxos Automáticos WhatsApp para Dashboard SVOBODA
Porta: 5052 (nginx proxy em /api/flow/)

Funcionalidade:
- Armazena fluxos ativos em JSON no servidor
- Thread background verifica respostas a cada 30s (24/7)
- Ao detectar resposta, classifica (SIM/NÃO/OUTRO) e envia mensagem automática
"""
import os
import json
import uuid
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR        = '/docker/dashboard'
FLOW_CONFIG_FILE = os.path.join(BASE_DIR, 'flow_config.json')
FLOWS_FILE      = os.path.join(BASE_DIR, 'flows_ativos.json')
LOG_FILE        = '/tmp/flow_api.log'

# ── Palavras-chave SIM/NÃO ──────────────────────────────────────────────────
PALAVRAS_SIM = ['sim', ' s ', 'yes', 'ok', 'otimo', 'ótimo', 'funcionou',
                'funciona', 'certo', 'correto', 'bom', 'boa', 'tudo bem',
                'tudo certo', 'claro', 'perfeito', 'show', 'beleza', 'positivo']
PALAVRAS_NAO = ['nao', 'não', ' n ', 'no', 'ruim', 'parou', 'problema',
                'negativo', 'errado', 'errada', 'nunca', 'nenhum',
                'nenhuma', 'pessimo', 'péssimo', 'defeito', 'quebrou',
                'caiu', 'sem internet', 'sem conexao', 'nao funciona']


# ── Helpers de arquivo ───────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception:
        pass
    print(line, end='')


def ler_config():
    if not os.path.exists(FLOW_CONFIG_FILE):
        return {
            "ativo": False,
            "delay_segundos": 10,
            "wa_backend": "",
            "wa_key": "",
            "msg_sim": "Que ótimo! Ficamos felizes que tudo correu bem. 😊 Qualquer dúvida, estamos à disposição!",
            "msg_nao": "Lamentamos o ocorrido! Nossa equipe de suporte será acionada para resolver o problema.",
            "msg_outro": "Obrigado pelo retorno! Em breve um de nossos atendentes entrará em contato."
        }
    with open(FLOW_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_config(cfg):
    with open(FLOW_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def ler_flows():
    if not os.path.exists(FLOWS_FILE):
        return []
    with open(FLOWS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_flows(flows):
    with open(FLOWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(flows, f, ensure_ascii=False, indent=2, default=str)


# ── Classificação de resposta ────────────────────────────────────────────────
def classificar_resposta(texto):
    t = texto.lower().strip()
    for p in PALAVRAS_SIM:
        if p in t:
            return 'sim'
    for p in PALAVRAS_NAO:
        if p in t:
            return 'nao'
    return 'outro'


# ── Motor de Fluxo (thread background) ──────────────────────────────────────
def fetch_msgs(wa_backend, wa_key, phone):
    """Busca mensagens de um telefone no backend WhatsApp."""
    url = f"{wa_backend.rstrip('/')}/msgs/{phone}?apikey={wa_key}"
    try:
        req = urllib.request.Request(url, headers={'x-api-key': wa_key})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        log(f"[ERRO] fetch_msgs {phone}: {e}")
        return []


def send_reply(wa_backend, wa_key, phone, text):
    """Envia resposta automática via backend WhatsApp."""
    url = f"{wa_backend.rstrip('/')}/send-reply?apikey={wa_key}"
    payload = json.dumps({"phone": phone, "text": text}).encode('utf-8')
    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={'Content-Type': 'application/json', 'x-api-key': wa_key},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        log(f"[ERRO] send_reply {phone}: {e}")
        return None


def motor_fluxo():
    """Thread principal do motor de fluxo — roda indefinidamente."""
    log("[MOTOR] Motor de fluxo iniciado (polling a cada 30s)")
    while True:
        try:
            cfg = ler_config()
            if not cfg.get('ativo') or not cfg.get('wa_backend'):
                time.sleep(30)
                continue

            wa_backend = cfg['wa_backend']
            wa_key     = cfg.get('wa_key', '')
            delay      = int(cfg.get('delay_segundos', 10))
            flows      = ler_flows()
            mudou      = False

            for fl in flows:
                if fl.get('status') != 'aguardando':
                    continue

                phone      = fl.get('phone', '')
                enviado_em = fl.get('enviado_em', '')
                if not phone:
                    continue

                try:
                    enviado_ts = datetime.fromisoformat(enviado_em)
                except Exception:
                    continue

                msgs = fetch_msgs(wa_backend, wa_key, phone)
                # Filtra mensagens recebidas DEPOIS do disparo
                novas = []
                for m in msgs:
                    if m.get('from') == 'me':
                        continue
                    ts = m.get('ts')
                    if not ts:
                        continue
                    try:
                        msg_ts = datetime.fromtimestamp(ts / 1000) if ts > 1e10 else datetime.fromtimestamp(ts)
                    except Exception:
                        continue
                    if msg_ts > enviado_ts:
                        novas.append(m)

                if not novas:
                    continue

                # Pega o texto da primeira nova mensagem
                primeiro_texto = (novas[0].get('text') or '').strip()
                classificacao  = classificar_resposta(primeiro_texto)

                msg_key = f"msg_{classificacao}"
                msg_enviar = cfg.get(msg_key, cfg.get('msg_outro', ''))

                log(f"[MOTOR] Resposta de {phone}: '{primeiro_texto[:60]}' → {classificacao.upper()}")

                if delay > 0:
                    time.sleep(delay)

                resultado = send_reply(wa_backend, wa_key, phone, msg_enviar)
                if resultado:
                    log(f"[MOTOR] Resposta automática enviada para {phone} ✓")
                    fl['status']            = 'respondido'
                    fl['resposta_recebida'] = primeiro_texto
                    fl['classificacao']     = classificacao
                    fl['respondido_em']     = datetime.now().isoformat()
                    mudou = True
                else:
                    log(f"[MOTOR] Falha ao enviar resposta para {phone}")

            if mudou:
                salvar_flows(flows)

        except Exception as e:
            log(f"[MOTOR] Erro inesperado: {e}")

        time.sleep(30)


# ── HTTP Handler ─────────────────────────────────────────────────────────────
class FlowHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        return json.loads(raw.decode('utf-8')) if raw else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0].rstrip('/')

        if path in ('/flow-config', ''):
            self._json(ler_config())

        elif path == '/flows':
            flows = ler_flows()
            self._json(flows)

        elif path == '/logs':
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]
                self._json({"logs": ''.join(lines)})
            except Exception:
                self._json({"logs": ""})

        elif path == '/status':
            flows = ler_flows()
            aguardando  = sum(1 for f in flows if f.get('status') == 'aguardando')
            respondidos = sum(1 for f in flows if f.get('status') == 'respondido')
            cancelados  = sum(1 for f in flows if f.get('status') == 'cancelado')
            self._json({
                "motor": "ativo",
                "aguardando": aguardando,
                "respondidos": respondidos,
                "cancelados": cancelados,
                "total": len(flows)
            })

        else:
            self._json({'erro': 'Rota nao encontrada'}, 404)

    def do_POST(self):
        path = self.path.split('?')[0].rstrip('/')

        if path == '/flow-config':
            try:
                data = self._body()
                cfg  = ler_config()
                for k in ['ativo', 'delay_segundos', 'wa_backend', 'wa_key',
                          'msg_sim', 'msg_nao', 'msg_outro']:
                    if k in data:
                        cfg[k] = data[k]
                salvar_config(cfg)
                log(f"[CONFIG] Configuração atualizada. Ativo={cfg.get('ativo')}")
                self._json({'ok': True})
            except Exception as e:
                self._json({'error': str(e)}, 500)

        elif path == '/flows':
            try:
                data  = self._body()
                flows = ler_flows()
                novos = data if isinstance(data, list) else [data]
                criados = []
                for item in novos:
                    phone = (item.get('phone') or '').replace(' ', '').replace('-', '')
                    if not phone:
                        continue
                    fl = {
                        "id":          str(uuid.uuid4())[:8],
                        "phone":       phone,
                        "nome":        item.get('nome', ''),
                        "enviado_em":  item.get('enviado_em', datetime.now().isoformat()),
                        "status":      "aguardando",
                        "resposta_recebida": None,
                        "classificacao":     None,
                        "respondido_em":     None
                    }
                    flows.append(fl)
                    criados.append(fl)
                    log(f"[FLOW] Novo fluxo criado: {phone} ({fl['nome']})")
                salvar_flows(flows)
                self._json({'ok': True, 'criados': len(criados), 'flows': criados})
            except Exception as e:
                self._json({'error': str(e)}, 500)

        else:
            self._json({'erro': 'Rota nao encontrada'}, 404)

    def do_DELETE(self):
        path = self.path.split('?')[0].rstrip('/')
        if path.startswith('/flows/'):
            flow_id = path.split('/')[-1]
            try:
                flows = ler_flows()
                for fl in flows:
                    if fl.get('id') == flow_id:
                        fl['status'] = 'cancelado'
                        log(f"[FLOW] Cancelado: {flow_id}")
                        break
                salvar_flows(flows)
                self._json({'ok': True})
            except Exception as e:
                self._json({'error': str(e)}, 500)
        elif path == '/flows':
            # Limpa todos os concluídos/cancelados
            try:
                flows = ler_flows()
                flows = [f for f in flows if f.get('status') == 'aguardando']
                salvar_flows(flows)
                self._json({'ok': True, 'mantidos': len(flows)})
            except Exception as e:
                self._json({'error': str(e)}, 500)
        else:
            self._json({'erro': 'Rota nao encontrada'}, 404)

    def log_message(self, format, *args):
        pass  # Silencia logs HTTP


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Inicia motor de fluxo em thread background
    t = threading.Thread(target=motor_fluxo, daemon=True)
    t.start()

    # Inicia servidor HTTP
    server = HTTPServer(('0.0.0.0', 5052), FlowHandler)
    log("[API] Flow API rodando na porta 5052")
    server.serve_forever()
