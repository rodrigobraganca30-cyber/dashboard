#!/usr/bin/env python3
import json, urllib.request

API = "http://localhost:3001/agenda"
KEY = "svoboda-agenda-2025"
NOME = "CAMERINO"

# Buscar clientes
r = urllib.request.urlopen(f"{API}/clients?apikey={KEY}")
data = json.loads(r.read())
matches = [c for c in data if NOME.upper() in c.get("nome","").upper()]

if not matches:
    print(f"Cliente '{NOME}' nao encontrado entre {len(data)} clientes")
else:
    for c in matches:
        print(json.dumps(c, indent=2, ensure_ascii=False))

# Buscar logs
try:
    r2 = urllib.request.urlopen(f"{API}/logs?apikey={KEY}")
    logs = json.loads(r2.read())
    msg_logs = [l for l in logs if NOME.upper() in json.dumps(l).upper()]
    if msg_logs:
        print(f"\n--- LOGS ({len(msg_logs)}) ---")
        for l in msg_logs[-5:]:
            print(json.dumps(l, indent=2, ensure_ascii=False))
except:
    pass
