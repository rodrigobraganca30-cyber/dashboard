#!/usr/bin/env python3
"""Injeta dados OS no index.html do servidor - executa no servidor"""
import json, re, sys, shutil
from datetime import datetime

HTML = "/docker/dashboard/html/index.html"
DATA = "/tmp/_os_inject.json"

# Backup
bak = f"{HTML}.bak.os_inject_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(HTML, bak)
print(f"[OK] Backup: {bak}")

with open(DATA, "r", encoding="utf-8") as f:
    d = json.load(f)

with open(HTML, "r", encoding="utf-8") as f:
    html = f.read()

orig_len = len(html)

# 1. Substituir tecData
p = re.compile(r'const tecData = \[.*?\](?:\s*//\s*\[.*?\])?;', re.DOTALL)
new_val = 'const tecData = ' + json.dumps(d["tecData"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] tecData: {n} substituicao(oes)")

# 2. Substituir cityData
p = re.compile(r'const cityData = \[.*?\](?:\s*//\s*\[.*?\])?;', re.DOTALL)
new_val = 'const cityData = ' + json.dumps(d["cityData"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] cityData: {n} substituicao(oes)")

# 3. Substituir tipoData
p = re.compile(r'const tipoData = \[.*?\](?:\s*//\s*\[.*?\])?;', re.DOTALL)
new_val = 'const tipoData = ' + json.dumps(d["tipoData"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] tipoData: {n} substituicao(oes)")

# 4. Substituir diaData
p = re.compile(r'const diaData = \[.*?\](?:\s*//\s*\[.*?\])?;', re.DOTALL)
new_val = 'const diaData = ' + json.dumps(d["diaData"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] diaData: {n} substituicao(oes)")

# 5. Substituir rawOSData
p = re.compile(r'var rawOSData = \[.*?\];', re.DOTALL)
new_val = 'var rawOSData = ' + json.dumps(d["rawOSData"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] rawOSData: {n} substituicao(oes)")

# 6. Substituir filterLists
p = re.compile(r'var filterLists = \{.*?\};', re.DOTALL)
new_val = 'var filterLists = ' + json.dumps(d["filterLists"], ensure_ascii=False) + ';'
html, n = p.subn(new_val, html, count=1)
print(f"[{'OK' if n else 'FALHA'}] filterLists: {n} substituicao(oes)")

# 7. Atualizar KPIs estáticos no HTML
sc = d["status_counts"]
total = d["total_os"]
conc = sc["Concluída"]
nc = sc["Não Concluída"]
ca = sc["Cancelada"]
su = sc["Suspensa"]
pe = sc["Pendente"]
taxa = round(conc / total * 100, 1) if total > 0 else 0

# Periodo label
periodo = d["periodo"]

# Tempo medio e deslocamento
tm = d["tempo_medio"]
dm = d["desl_medio"]
sla_e = d["sla_estourado"]

print(f"\n[RESUMO] {total} OS | {periodo}")
print(f"  Conc={conc} NC={nc} Ca={ca} Su={su} Pe={pe} Taxa={taxa}%")
print(f"  Tempo={tm}m Desl={dm}m SLA_est={sla_e}")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

new_len = len(html)
print(f"\n[SUCESSO] HTML atualizado: {orig_len:,} -> {new_len:,} bytes")
