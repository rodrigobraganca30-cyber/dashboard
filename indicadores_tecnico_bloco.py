# --- 2h. INDICADORES POR TÉCNICO (ABAS DETALHADAS) ---
# Lê as 5 abas de detalhamento por técnico da mesma planilha premio_temp.xlsx

import re as _re3

def _norm_tec_name(nome):
    """Normaliza nome de técnico: remove sufixo empresa, aplica title case"""
    if not nome: return ""
    nome = str(nome).strip()
    # Remove sufixo " - SVOBODA TELECOMUNICAÇÕES" e variantes
    nome = re.sub(r'\s*-\s*SVOBODA.*$', '', nome, flags=re.IGNORECASE)
    nome = nome.strip().title()
    return nome

def _detect_month_suffix(sheetnames):
    """Detecta automaticamente o sufixo do mês mais recente nas abas"""
    meses_ord = ["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"]
    found = set()
    for sn in sheetnames:
        for m in meses_ord:
            if sn.upper().strip().endswith(m):
                found.add(m)
    # Retorna o mês mais recente encontrado
    for m in reversed(meses_ord):
        if m in found:
            return m
    return "ABR"

import re

tec_altas_data = []
tec_reparo_data = []
tec_irr_data = []
tec_ifi_data = []
tec_efetiv_data = []

# Dados brutos para drill-down
raw_irr_list = []
raw_ifi_list = []

if os.path.exists(GIGA2_FILE):
    _wb3 = openpyxl.load_workbook(GIGA2_FILE, read_only=True, data_only=True)
    _mes_suffix = _detect_month_suffix(_wb3.sheetnames)
    print(f"[DEBUG] Mês detectado para indicadores: {_mes_suffix}")

    # ── ALTAS ──
    _aba_altas = next((n for n in _wb3.sheetnames if n.upper().strip().startswith("ALTAS") and n.upper().strip().endswith(_mes_suffix)), None)
    if _aba_altas:
        _ws_a = _wb3[_aba_altas]
        _rows_a = list(_ws_a.iter_rows(values_only=True))
        _agg_a = {}
        for r in _rows_a[1:]:
            tec = _norm_tec_name(r[11] if len(r) > 11 else "")
            if not tec: continue
            aging_h = float(r[14]) if len(r) > 14 and r[14] else 0
            aging_cat = str(r[15]).strip() if len(r) > 15 and r[15] else ""
            outlier = str(r[17]).strip().upper() if len(r) > 17 and r[17] else ""
            if tec not in _agg_a:
                _agg_a[tec] = {"qtd": 0, "aging_sum": 0, "dentro_48h": 0, "outlier": 0}
            _agg_a[tec]["qtd"] += 1
            _agg_a[tec]["aging_sum"] += aging_h
            if "DENTRO" in aging_cat.upper() and ("18" in aging_cat or "24" in aging_cat or "36" in aging_cat or "48" in aging_cat):
                _agg_a[tec]["dentro_48h"] += 1
            if outlier in ["VERDADEIRO", "TRUE", "1", "SIM"]:
                _agg_a[tec]["outlier"] += 1
        for tec, d in sorted(_agg_a.items(), key=lambda x: x[1]["qtd"], reverse=True):
            tec_altas_data.append({
                "tecnico": tec,
                "qtd": d["qtd"],
                "aging_medio": round(d["aging_sum"] / d["qtd"], 1) if d["qtd"] > 0 else 0,
                "pct_48h": round(d["dentro_48h"] / d["qtd"] * 100, 1) if d["qtd"] > 0 else 0,
                "pct_outlier": round(d["outlier"] / d["qtd"] * 100, 1) if d["qtd"] > 0 else 0,
            })
        print(f"[OK] Altas: {len(tec_altas_data)} técnicos de {len(_rows_a)-1} registros")

    # ── REPARO ──
    _aba_rep = next((n for n in _wb3.sheetnames if n.upper().strip().startswith("REPARO") and n.upper().strip().endswith(_mes_suffix)), None)
    if _aba_rep:
        _ws_r = _wb3[_aba_rep]
        _rows_r = list(_ws_r.iter_rows(values_only=True))
        _agg_r = {}
        for r in _rows_r[1:]:
            tec = _norm_tec_name(r[11] if len(r) > 11 else "")
            if not tec: continue
            aging_h = float(r[13]) if len(r) > 13 and r[13] else 0
            aging_cat = str(r[14]).strip() if len(r) > 14 and r[14] else ""
            if tec not in _agg_r:
                _agg_r[tec] = {"qtd": 0, "aging_sum": 0, "dentro_24h": 0}
            _agg_r[tec]["qtd"] += 1
            _agg_r[tec]["aging_sum"] += aging_h
            if "18" in aging_cat or "24" in aging_cat:
                _agg_r[tec]["dentro_24h"] += 1
        for tec, d in sorted(_agg_r.items(), key=lambda x: x[1]["qtd"], reverse=True):
            tec_reparo_data.append({
                "tecnico": tec,
                "qtd": d["qtd"],
                "aging_medio": round(d["aging_sum"] / d["qtd"], 1) if d["qtd"] > 0 else 0,
                "pct_24h": round(d["dentro_24h"] / d["qtd"] * 100, 1) if d["qtd"] > 0 else 0,
            })
        print(f"[OK] Reparo: {len(tec_reparo_data)} técnicos de {len(_rows_r)-1} registros")

    # ── IRR ──
    _aba_irr = next((n for n in _wb3.sheetnames if n.upper().strip().startswith("IRR") and n.upper().strip().endswith(_mes_suffix)), None)
    if _aba_irr:
        _ws_i = _wb3[_aba_irr]
        _rows_i = list(_ws_i.iter_rows(values_only=True))
        _agg_i = {}
        for r in _rows_i[1:]:
            tec = _norm_tec_name(r[16] if len(r) > 16 else "")
            if not tec: continue
            cidade = str(r[4]).strip() if len(r) > 4 and r[4] else ""
            motivo = str(r[11]).strip() if len(r) > 11 and r[11] else ""
            os_cod = str(r[10]).strip() if len(r) > 10 and r[10] else ""
            data_str = ""
            if len(r) > 18 and r[18]:
                try: data_str = r[18].strftime("%d/%m/%Y") if hasattr(r[18], 'strftime') else str(r[18])[:10]
                except: data_str = str(r[18])[:10]
            raw_irr_list.append({"tecnico": tec, "cidade": cidade, "motivo": motivo, "os": os_cod, "data": data_str})
            if tec not in _agg_i:
                _agg_i[tec] = {"qtd": 0}
            _agg_i[tec]["qtd"] += 1
        for tec, d in sorted(_agg_i.items(), key=lambda x: x[1]["qtd"], reverse=True):
            tec_irr_data.append({"tecnico": tec, "qtd": d["qtd"]})
        print(f"[OK] IRR: {len(tec_irr_data)} técnicos de {len(_rows_i)-1} registros")

    # ── IFI ──
    _aba_ifi = next((n for n in _wb3.sheetnames if n.upper().strip().startswith("IFI") and n.upper().strip().endswith(_mes_suffix)), None)
    if _aba_ifi:
        _ws_f = _wb3[_aba_ifi]
        _rows_f = list(_ws_f.iter_rows(values_only=True))
        _agg_f = {}
        for r in _rows_f[1:]:
            tec = _norm_tec_name(r[14] if len(r) > 14 else "")
            if not tec: continue
            ifme = str(r[2]).strip().upper() if len(r) > 2 and r[2] else ""
            cidade = str(r[5]).strip() if len(r) > 5 and r[5] else ""
            motivo = str(r[12]).strip() if len(r) > 12 and r[12] else ""
            os_cod = str(r[11]).strip() if len(r) > 11 and r[11] else ""
            data_str = ""
            if len(r) > 16 and r[16]:
                try: data_str = r[16].strftime("%d/%m/%Y") if hasattr(r[16], 'strftime') else str(r[16])[:10]
                except: data_str = str(r[16])[:10]
            is_ifme = ifme in ["VERDADEIRO", "TRUE", "1", "SIM"]
            raw_ifi_list.append({"tecnico": tec, "cidade": cidade, "motivo": motivo, "os": os_cod, "data": data_str, "ifme": is_ifme})
            if tec not in _agg_f:
                _agg_f[tec] = {"qtd": 0, "qtd_ifme": 0}
            _agg_f[tec]["qtd"] += 1
            if is_ifme:
                _agg_f[tec]["qtd_ifme"] += 1
        for tec, d in sorted(_agg_f.items(), key=lambda x: x[1]["qtd"], reverse=True):
            tec_ifi_data.append({"tecnico": tec, "qtd": d["qtd"], "qtd_ifme": d["qtd_ifme"]})
        print(f"[OK] IFI: {len(tec_ifi_data)} técnicos de {len(_rows_f)-1} registros")

    # ── EFETIVIDADE ──
    _aba_efe = next((n for n in _wb3.sheetnames if n.upper().strip().startswith("EFETIVIDADE") and n.upper().strip().endswith(_mes_suffix)), None)
    if _aba_efe:
        _ws_e = _wb3[_aba_efe]
        _rows_e = list(_ws_e.iter_rows(values_only=True))
        _agg_e = {}
        for r in _rows_e[1:]:
            tec = _norm_tec_name(r[8] if len(r) > 8 else "")
            if not tec: continue
            conclusao = str(r[7]).strip() if len(r) > 7 and r[7] else ""
            if tec not in _agg_e:
                _agg_e[tec] = {"qtd": 0, "realizado": 0}
            _agg_e[tec]["qtd"] += 1
            if "realizado" in conclusao.lower():
                _agg_e[tec]["realizado"] += 1
        for tec, d in sorted(_agg_e.items(), key=lambda x: x[1]["qtd"], reverse=True):
            tec_efetiv_data.append({
                "tecnico": tec,
                "qtd": d["qtd"],
                "realizado": d["realizado"],
                "pct_realizado": round(d["realizado"] / d["qtd"] * 100, 1) if d["qtd"] > 0 else 0,
            })
        print(f"[OK] Efetividade: {len(tec_efetiv_data)} técnicos de {len(_rows_e)-1} registros")

    _wb3.close()
else:
    print("[AVISO] premio_temp.xlsx não encontrado para indicadores por técnico")

# KPIs globais dos indicadores por técnico
_total_altas = sum(d["qtd"] for d in tec_altas_data)
_total_reparos = sum(d["qtd"] for d in tec_reparo_data)
_total_irr = sum(d["qtd"] for d in tec_irr_data)
_total_ifi = sum(d["qtd"] for d in tec_ifi_data)
_total_efetiv = sum(d["qtd"] for d in tec_efetiv_data)
_avg_aging_altas = round(sum(d["aging_medio"]*d["qtd"] for d in tec_altas_data) / _total_altas, 1) if _total_altas > 0 else 0
_avg_aging_reparo = round(sum(d["aging_medio"]*d["qtd"] for d in tec_reparo_data) / _total_reparos, 1) if _total_reparos > 0 else 0
