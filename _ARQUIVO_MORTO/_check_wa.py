#!/usr/bin/env python3
import json, urllib.request

API = "https://svoboda.rtflowapp.com/api/agenda"
NOME = "CAMERINO"

# 1. Buscar clientes
try:
    r = urllib.request.urlopen(f"{API}/clients?apikey=")
    data = json.loads(r.read())
    matches = [c for c in data if NOME.upper() in c.get("nome","").upper()]
    if not matches:
        print(f"Cliente '{NOME}' nao encontrado na lista de clientes")
        # Tentar buscar nos logs de mensagens
    else:
        for c in matches:
            print(f"Cliente: {c.get('nome')} | Tel: {c.get('telefone','')} | Status: {c.get('status','?')}")
            print(f"  Fase: {c.get('fase','')} | Ultimo disparo: {c.get('ultimo_disparo','')}")
            print(f"  Mensagens: {json.dumps(c.get('mensagens', c.get('historico', [])), indent=2, ensure_ascii=False)}")
            print()
except Exception as e:
    print(f"Erro ao buscar clientes: {e}")

# 2. Buscar logs de disparo
try:
    r2 = urllib.request.urlopen(f"{API}/logs?apikey=")
    logs = json.loads(r2.read())
    msg_logs = [l for l in logs if NOME.upper() in json.dumps(l).upper()]
    if msg_logs:
        print(f"\n--- LOGS DE DISPARO ({len(msg_logs)} entradas) ---")
        for l in msg_logs[-10:]:
            print(json.dumps(l, indent=2, ensure_ascii=False))
    else:
        print(f"\nNenhum log de disparo encontrado para '{NOME}'")
except Exception as e:
    print(f"Logs nao disponiveis: {e}")
