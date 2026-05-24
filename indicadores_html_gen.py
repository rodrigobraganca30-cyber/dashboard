import json

def gerar_indicadores_html(tec_altas, tec_reparo, tec_irr, tec_ifi, tec_efetiv,
                           raw_irr, raw_ifi, indicadores_data, gen_indicadores_table,
                           eq_total_os, eq_media_prod, eq_pontuacao, eq_nota_ifi,
                           eq_nota_irr, eq_combustivel, _nota_color, list_tec=None,
                           tec_ifime=None, raw_ifime=None, tec_scorecard=None):
    if tec_scorecard is None: tec_scorecard = []
    if tec_ifime is None: tec_ifime = []
    if raw_ifime is None: raw_ifime = []
    _ta = sum(d["qtd"] for d in tec_altas)
    _tr = sum(d["qtd"] for d in tec_reparo)
    _ti = sum(d["qtd"] for d in tec_irr)
    _tf = sum(d["qtd"] for d in tec_ifi)
    _te = sum(d["qtd"] for d in tec_efetiv)

    def _atbl(data):
        h = ""
        for i, d in enumerate(data):
            ag_c = "#22d3a0" if d["aging_medio"] <= 24 else "#fbbf24" if d["aging_medio"] <= 48 else "#ff4d6d"
            p48_c = "#22d3a0" if d["pct_48h"] >= 80 else "#fbbf24" if d["pct_48h"] >= 50 else "#ff4d6d"
            out_c = "#22d3a0" if d["pct_outlier"] <= 5 else "#fbbf24" if d["pct_outlier"] <= 15 else "#ff4d6d"
            h += f'<tr><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-weight:700;color:var(--accent)">{d["qtd"]}</td><td style="text-align:center;color:{ag_c};font-weight:600">{d["aging_medio"]}h</td><td style="text-align:center;color:{p48_c};font-weight:600">{d["pct_48h"]}%</td><td style="text-align:center;color:{out_c};font-weight:600">{d["pct_outlier"]}%</td></tr>\n'
        return h

    def _rtbl(data):
        h = ""
        for i, d in enumerate(data):
            ag_c = "#22d3a0" if d["aging_medio"] <= 18 else "#fbbf24" if d["aging_medio"] <= 24 else "#ff4d6d"
            p24_c = "#22d3a0" if d["pct_24h"] >= 80 else "#fbbf24" if d["pct_24h"] >= 50 else "#ff4d6d"
            h += f'<tr><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-weight:700;color:var(--accent)">{d["qtd"]}</td><td style="text-align:center;color:{ag_c};font-weight:600">{d["aging_medio"]}h</td><td style="text-align:center;color:{p24_c};font-weight:600">{d["pct_24h"]}%</td></tr>\n'
        return h

    def _itbl(data):
        h = ""
        for i, d in enumerate(data):
            pct = d.get("pct_irr", 0)
            m = d.get("meta100", 6.2)
            pc = "#22d3a0" if pct < m else "#fbbf24" if pct < m*1.05 else "#ff4d6d"
            nc = "#22d3a0" if d.get("nota",0) > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td><td style="text-align:center">{d.get("reparos",0)}</td><td style="text-align:center;font-weight:700;color:{pc}">{d["qtd"]}</td><td style="text-align:center;font-weight:700;color:{pc}">{pct}%</td><td style="text-align:center;font-size:11px">&lt;{m}%</td><td style="text-align:center;color:{nc};font-weight:700">{d.get("nota",0)}/20</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\'irr\',\'{d["tecnico"].replace(chr(39),"")}\')">🔍</td></tr>\n'
        return h

    def _ftbl(data):
        h = ""
        for i, d in enumerate(data):
            pct = d.get("pct_ifi", 0)
            m = d.get("meta100", 2.7)
            pc = "#22d3a0" if pct < m else "#fbbf24" if pct < m*1.22 else "#ff4d6d"
            nc = "#22d3a0" if d.get("nota",0) > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td><td style="text-align:center">{d.get("altas",0)}</td><td style="text-align:center;font-weight:700;color:{pc}">{d["qtd"]}</td><td style="text-align:center;font-weight:700;color:{pc}">{pct}%</td><td style="text-align:center;font-size:11px">&lt;{m}%</td><td style="text-align:center;color:{nc};font-weight:700">{d.get("nota",0)}/{d.get("meta100",15) if d.get("nota",0)>0 else 15}</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\'ifi\',\'{d["tecnico"].replace(chr(39),"")}\')">🔍</td></tr>\n'
        return h

    def _fmtbl(data):
        h = ""
        for i, d in enumerate(data):
            pct = d.get("pct_ifime", 0)
            m = d.get("meta100", 3.25)
            pc = "#22d3a0" if pct < m else "#fbbf24" if pct < m*1.2 else "#ff4d6d"
            nc = "#22d3a0" if d.get("nota",0) > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td><td style="text-align:center">{d.get("mes_total",0)}</td><td style="text-align:center;font-weight:700;color:{pc}">{d["qtd"]}</td><td style="text-align:center;font-weight:700;color:{pc}">{pct}%</td><td style="text-align:center;font-size:11px">&lt;{m}%</td><td style="text-align:center;color:{nc};font-weight:700">{d.get("nota",0)}/{d.get("meta100",10) if d.get("nota",0)>0 else 10}</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\'ifime\',\'{d["tecnico"].replace(chr(39),"")}\')">🔍</td></tr>\n'
        return h

    def _etbl(data):
        h = ""
        for i, d in enumerate(data):
            tc = "#22d3a0" if d["taxa"] >= 70 else "#00e5ff" if d["taxa"] >= 55 else "#fbbf24" if d["taxa"] >= 45 else "#ff4d6d"
            bar_bg = tc
            h += f'<tr><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d.get("Recurso",d.get("key",""))}</td><td style="text-align:center;font-family:var(--font-mono)">{d["total"]}</td><td style="text-align:center;color:#22d3a0;font-family:var(--font-mono)">{d["concluido"]}</td><td style="text-align:center;color:#fbbf24;font-family:var(--font-mono)">{d["nao_concluido"]}</td><td style="text-align:center;color:#ff4d6d;font-family:var(--font-mono)">{d["cancelado"]}</td><td style="text-align:center"><span class="badge" style="background:rgba({"34,211,160" if d["taxa"]>=70 else "0,229,255" if d["taxa"]>=55 else "251,191,36" if d["taxa"]>=45 else "255,77,109"},.15);color:{tc}">{d["taxa"]}%</span></td><td style="min-width:120px"><div style="display:flex;align-items:center;gap:6px"><div style="flex:1;background:rgba(255,255,255,.05);border-radius:3px;height:6px"><div style="width:{d["taxa"]}%;background:{bar_bg};height:100%;border-radius:3px"></div></div><span style="font-size:11px;font-family:var(--font-mono);color:var(--muted);width:34px">{d["taxa"]}%</span></div></td></tr>\n'
        return h

    def _sctbl(data):
        h = ""
        for i, d in enumerate(data):
            tc = "#22d3a0" if d["total"] >= 85 else "#00e5ff" if d["total"] >= 70 else "#fbbf24" if d["total"] >= 50 else "#ff4d6d"
            def _nc(v, mx): return "#22d3a0" if v == mx else "#fbbf24" if v > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_aging"],15)};font-weight:600">{d["n_aging"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_rep24"],15)};font-weight:600">{d["n_rep24"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_outlier"],5)};font-weight:600">{d["n_outlier"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_ifi"],15)};font-weight:600">{d["n_ifi"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_irr"],20)};font-weight:600">{d["n_irr"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_ifime"],10)};font-weight:600">{d["n_ifime"]}</td>'
            h += f'<td style="text-align:center;color:{_nc(d["n_efetiv"],20)};font-weight:600">{d["n_efetiv"]}</td>'
            h += f'<td style="text-align:center"><span style="font-weight:800;font-size:16px;color:{tc}">{d["total"]}</span></td>'
            h += f'<td style="min-width:100px"><div style="display:flex;align-items:center;gap:4px"><div style="flex:1;background:rgba(255,255,255,.05);border-radius:3px;height:8px"><div style="width:{d["total"]}%;background:{tc};height:100%;border-radius:3px"></div></div></div></td></tr>\n'
        return h

    tec_cluster_map = {d["tecnico"]: d.get("cluster", "") for d in tec_scorecard} if tec_scorecard else {}

    def _causas_tbl(data):
        h = ""
        for i, d in enumerate(data):
            tipo = d.get("tipo", "")
            cl = d.get("cluster", "")
            tc = "#ff4d6d" if tipo == "IFI" else "#fbbf24" if tipo == "IFIME" else "var(--accent)"
            h += f'<tr data-tipo="{tipo}" data-cluster="{cl}">'
            h += f'<td>{i+1}</td>'
            h += f'<td style="text-align:center"><span class="badge" style="background:rgba(255,255,255,0.1);color:{tc}">{tipo}</span></td>'
            h += f'<td style="text-align:center;font-size:11px;color:#64748b">{cl}</td>'
            h += f'<td style="font-weight:600;color:#e8eaf6">{d.get("tecnico","")}</td>'
            h += f'<td style="font-family:var(--font-mono)">{d.get("os","")}</td>'
            h += f'<td>{d.get("cidade","")}</td>'
            h += f'<td style="font-family:var(--font-mono)">{d.get("data","")}</td>'
            h += f'<td style="font-size:11px;max-width:300px;word-break:break-word">{d.get("motivo","")}</td>'
            h += '</tr>\n'
        return h

    todas_causas = []
    for d in raw_irr:
        dc = d.copy()
        dc["tipo"] = "IRR"
        dc["cluster"] = tec_cluster_map.get(dc["tecnico"], "")
        todas_causas.append(dc)
    for d in raw_ifi:
        dc = d.copy()
        dc["tipo"] = "IFIME" if d.get("ifme") else "IFI"
        dc["cluster"] = tec_cluster_map.get(dc["tecnico"], "")
        todas_causas.append(dc)
    for d in raw_ifime:
        dc = d.copy()
        dc["tipo"] = "IFIME"
        dc["cluster"] = tec_cluster_map.get(dc["tecnico"], "")
        todas_causas.append(dc)

    # Build GIGA+ existing table
    giga_table = gen_indicadores_table(sorted(indicadores_data, key=lambda x: x['pontuacao'], reverse=True))
    ifi_bc = 'rgba(34,211,160,.4)' if eq_nota_ifi >= 90 else 'rgba(251,191,36,.4)' if eq_nota_ifi >= 70 else 'rgba(255,77,109,.4)'
    irr_bc = 'rgba(34,211,160,.4)' if eq_nota_irr <= 5 else 'rgba(251,191,36,.4)' if eq_nota_irr <= 15 else 'rgba(255,77,109,.4)'

    irr_json = json.dumps(raw_irr, ensure_ascii=False)
    ifime_json = json.dumps(raw_ifime, ensure_ascii=False)
    ifi_json = json.dumps(raw_ifi, ensure_ascii=False)

    html = f"""
<!-- ==================== INDICADORES ==================== -->
<style>
  .ind-tabs {{display:flex;gap:8px;margin-bottom:24px;flex-wrap:wrap;}}
  .ind-tab {{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-family:var(--font-head);font-weight:600;transition:all 0.2s;}}
  .ind-tab:hover {{border-color:#7c3aed;color:#e8eaf6;}}
  .ind-tab.active {{background:#7c3aed;border-color:#7c3aed;color:white;box-shadow:0 4px 15px rgba(124,58,237,0.3);}}
  .ind-sub {{display:none;}}
  .ind-sub.active {{display:block;}}
  .drill-overlay {{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:9999;justify-content:center;align-items:center;}}
  .drill-overlay.show {{display:flex;}}
  .drill-box {{background:#111520;border:1px solid #1c2237;border-radius:16px;padding:28px;max-width:900px;width:95%;max-height:80vh;overflow-y:auto;position:relative;}}
  .drill-close {{position:absolute;top:14px;right:18px;font-size:20px;color:#94a3b8;cursor:pointer;}}
  .drill-close:hover {{color:#ff4d6d;}}
  .cluster-filter {{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap;}}
  .cluster-btn {{background:#0d1520;border:1px solid #1c2237;border-radius:6px;padding:6px 14px;font-size:12px;color:#64748b;cursor:pointer;font-weight:600;transition:all .2s;}}
  .cluster-btn:hover {{border-color:#7c3aed;color:#a78bfa;}}
  .cluster-btn.active {{background:#7c3aed;border-color:#7c3aed;color:#fff;}}
</style>
<div class="page" id="indicadores">
  <div class="ind-tabs">
    <div class="ind-tab active" onclick="showIndSub('ind-altas',this)">📈 Altas ({_ta})</div>
    <div class="ind-tab" onclick="showIndSub('ind-reparo',this)">🔧 Reparos ({_tr})</div>
    <div class="ind-tab" onclick="showIndSub('ind-irr',this)">🔁 IRR ({_ti})</div>
    <div class="ind-tab" onclick="showIndSub('ind-ifi',this)">⚠️ IFI ({_tf})</div>
    <div class="ind-tab" onclick="showIndSub('ind-ifime',this)">📦 IFIME ({sum(d['qtd'] for d in tec_ifime)})</div>
    <div class="ind-tab" onclick="showIndSub('ind-efetiv',this)">🎯 Efetividade ({len(list_tec) if list_tec else 0})</div>
    <div class="ind-tab" onclick="showIndSub('ind-comparativo',this)">📊 Comparativo</div>
    <div class="ind-tab" onclick="showIndSub('ind-causas',this)">📋 Consolidado Causas</div>
  </div>

  <!-- SUB: ALTAS -->
  <div class="ind-sub active" id="ind-altas">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card blue"><div class="kpi-label">Total Altas</div><div class="kpi-value blue">{_ta}</div><div class="kpi-sub">{len(tec_altas)} técnicos</div></div>
      <div class="kpi-card green"><div class="kpi-label">M\u00e9dia por T\u00e9c.</div><div class="kpi-value green">{round(_ta/len(tec_altas)) if tec_altas else 0}</div><div class="kpi-sub">altas/técnico</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">Aging M\u00e9dio</div><div class="kpi-value yellow">{round(sum(d['aging_medio']*d['qtd'] for d in tec_altas)/_ta,1) if _ta else 0}h</div><div class="kpi-sub">horas</div></div>
      <div class="kpi-card red"><div class="kpi-label">Outliers</div><div class="kpi-value red">{sum(round(d['qtd']*d['pct_outlier']/100) for d in tec_altas)}</div><div class="kpi-sub">fora do prazo</div></div>
    </div>
    <div class="section-title">📈 Ranking Altas por Técnico</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-altas"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-altas',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-altas',1,'str')">Técnico</th>
        <th class="sortable desc" onclick="sortTable('tbl-altas',2,'num')" style="text-align:center">Qtd</th>
        <th class="sortable" onclick="sortTable('tbl-altas',3,'num')" style="text-align:center">Aging M\u00e9dio</th>
        <th class="sortable" onclick="sortTable('tbl-altas',4,'num')" style="text-align:center">% No Prazo</th>
        <th class="sortable" onclick="sortTable('tbl-altas',5,'num')" style="text-align:center">% Outlier</th>
      </tr></thead><tbody>{_atbl(tec_altas)}</tbody></table>
    </div>
  </div>

  <!-- SUB: REPARO -->
  <div class="ind-sub" id="ind-reparo">
    <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:24px;">
      <div class="kpi-card blue"><div class="kpi-label">Total Reparos</div><div class="kpi-value blue">{_tr}</div><div class="kpi-sub">{len(tec_reparo)} técnicos</div></div>
      <div class="kpi-card green"><div class="kpi-label">M\u00e9dia por T\u00e9c.</div><div class="kpi-value green">{round(_tr/len(tec_reparo)) if tec_reparo else 0}</div><div class="kpi-sub">reparos/técnico</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">Aging M\u00e9dio</div><div class="kpi-value yellow">{round(sum(d['aging_medio']*d['qtd'] for d in tec_reparo)/_tr,1) if _tr else 0}h</div><div class="kpi-sub">horas</div></div>
    </div>
    <div class="section-title">🔧 Ranking Reparos por Técnico</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-reparos"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-reparos',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-reparos',1,'str')">Técnico</th>
        <th class="sortable desc" onclick="sortTable('tbl-reparos',2,'num')" style="text-align:center">Qtd</th>
        <th class="sortable" onclick="sortTable('tbl-reparos',3,'num')" style="text-align:center">Aging M\u00e9dio</th>
        <th class="sortable" onclick="sortTable('tbl-reparos',4,'num')" style="text-align:center">% Dentro 24h</th>
      </tr></thead><tbody>{_rtbl(tec_reparo)}</tbody></table>
    </div>
  </div>

  <!-- SUB: IRR -->
  <div class="ind-sub" id="ind-irr">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IRR</div><div class="kpi-value red">{_ti}</div><div class="kpi-sub">reincidências reparo</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IRR Equipe</div><div class="kpi-value yellow">{round(sum(d['qtd'] for d in tec_irr)/max(sum(d.get('reparos',0) for d in tec_irr),1)*100,2)}%</div><div class="kpi-sub">meta por cluster</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{sum(1 for d in tec_irr if d.get('pct_irr',0)<d.get('meta100',6.2))}</div><div class="kpi-sub">técnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{sum(1 for d in tec_irr if d.get('pct_irr',0)>=d.get('meta100',6.2) and d['qtd']>0)}</div><div class="kpi-sub">técnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-irr','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.18',this)">C.18</div></div>
    <div class="section-title">🔁 IRR por Técnico — Reincidência Reparo</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-irr"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-irr',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-irr',1,'str')">Técnico</th>
        <th class="sortable" onclick="sortTable('tbl-irr',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-irr',3,'num')" style="text-align:center">Reparos</th>
        <th class="sortable" onclick="sortTable('tbl-irr',4,'num')" style="text-align:center">Casos IRR</th>
        <th class="sortable desc" onclick="sortTable('tbl-irr',5,'num')" style="text-align:center">% IRR</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-irr',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">🔍</th>
      </tr></thead><tbody>{_itbl(tec_irr)}</tbody></table>
    </div>
  </div>

  <!-- SUB: IFI -->
  <div class="ind-sub" id="ind-ifi">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IFI</div><div class="kpi-value red">{_tf}</div><div class="kpi-sub">garantia 15 dias</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IFI Equipe</div><div class="kpi-value yellow">{round(sum(d['qtd'] for d in tec_ifi)/max(sum(d.get('altas',0) for d in tec_ifi),1)*100,2)}%</div><div class="kpi-sub">meta: &lt;2,7%</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{sum(1 for d in tec_ifi if d.get('pct_ifi',0)<d.get('meta100',2.7))}</div><div class="kpi-sub">técnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{sum(1 for d in tec_ifi if d.get('pct_ifi',0)>=d.get('meta100',2.7) and d['qtd']>0)}</div><div class="kpi-sub">técnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-ifi','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.18',this)">C.18</div></div>
    <div class="section-title">⚠️ IFI por Técnico — Garantia 15 dias (Ativação)</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-ifi"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-ifi',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',1,'str')">Técnico</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',3,'num')" style="text-align:center">Ativações</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',4,'num')" style="text-align:center">Casos</th>
        <th class="sortable desc" onclick="sortTable('tbl-ifi',5,'num')" style="text-align:center">% IFI</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">🔍</th>
      </tr></thead><tbody>{_ftbl(tec_ifi)}</tbody></table>
    </div>
  </div>

  <!-- SUB: IFIME -->
  <div class="ind-sub" id="ind-ifime">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IFIME</div><div class="kpi-value red">{sum(d['qtd'] for d in tec_ifime)}</div><div class="kpi-sub">garantia 30 dias</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IFIME Equipe</div><div class="kpi-value yellow">{round(sum(d['qtd'] for d in tec_ifime)/max(sum(d.get('mes_total',0) for d in tec_ifime),1)*100,2)}%</div><div class="kpi-sub">meta: &lt;3,25%</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{sum(1 for d in tec_ifime if d.get('pct_ifime',0)<d.get('meta100',3.25))}</div><div class="kpi-sub">técnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{sum(1 for d in tec_ifime if d.get('pct_ifime',0)>=d.get('meta100',3.25) and d['qtd']>0)}</div><div class="kpi-sub">técnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-ifime','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.18',this)">C.18</div></div>
    <div class="section-title">📦 IFIME por Técnico — Garantia 30 dias (Mud. Endereço)</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-ifime"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-ifime',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',1,'str')">Técnico</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',3,'num')" style="text-align:center">Mud. End.</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',4,'num')" style="text-align:center">Casos</th>
        <th class="sortable desc" onclick="sortTable('tbl-ifime',5,'num')" style="text-align:center">% IFIME</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">🔍</th>
      </tr></thead><tbody>{_fmtbl(tec_ifime)}</tbody></table>
    </div>
  </div>

  <!-- SUB: EFETIVIDADE -->
  <div class="ind-sub" id="ind-efetiv">
    <div class="kpi-grid" style="grid-template-columns:repeat(5,1fr);margin-bottom:24px;">
      <div class="kpi-card blue"><div class="kpi-label">Total O.S.</div><div class="kpi-value blue">{sum(d['total'] for d in list_tec) if list_tec else 0}</div><div class="kpi-sub">{len(list_tec) if list_tec else 0} técnicos</div></div>
      <div class="kpi-card green"><div class="kpi-label">Conclu\u00eddas</div><div class="kpi-value green">{sum(d['concluido'] for d in list_tec) if list_tec else 0}</div><div class="kpi-sub">finalizadas</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">N\u00e3o Conclu\u00eddas</div><div class="kpi-value yellow">{sum(d['nao_concluido'] for d in list_tec) if list_tec else 0}</div><div class="kpi-sub">pendentes</div></div>
      <div class="kpi-card red"><div class="kpi-label">Canceladas</div><div class="kpi-value red">{sum(d['cancelado'] for d in list_tec) if list_tec else 0}</div><div class="kpi-sub">cancelamentos</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Melhor Taxa</div><div class="kpi-value green" style="font-size:24px">{list_tec[0].get('Recurso','') if list_tec else '-'}</div><div class="kpi-sub">{list_tec[0]['taxa'] if list_tec else 0}%</div></div>
    </div>
    <div class="section-title">🎯 Ranking Efetividade por Técnico — Taxa de Conclus\u00e3o</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-efetiv"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-efetiv',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',1,'str')">Técnico</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',2,'num')" style="text-align:center">Total OS</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',3,'num')" style="text-align:center">Conclu\u00eddas</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',4,'num')" style="text-align:center">N\u00e3o Conc.</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',5,'num')" style="text-align:center">Canceladas</th>
        <th class="sortable desc" onclick="sortTable('tbl-efetiv',6,'num')" style="text-align:center">Taxa</th>
        <th class="sortable" onclick="sortTable('tbl-efetiv',7,'num')" style="text-align:center">Performance</th>
      </tr></thead><tbody>{_etbl(list_tec if list_tec else [])}</tbody></table>
    </div>
  </div>


  <!-- SUB: COMPARATIVO -->
  <div class="ind-sub" id="ind-comparativo">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card purple"><div class="kpi-label">Nota M\u00e9dia</div><div class="kpi-value white">{round(sum(d['total'] for d in tec_scorecard)/max(len(tec_scorecard),1),1)}</div><div class="kpi-sub">{len(tec_scorecard)} t\u00e9cnicos</div></div>
      <div class="kpi-card green"><div class="kpi-label">Melhor</div><div class="kpi-value green" style="font-size:18px">{tec_scorecard[0]['tecnico'] if tec_scorecard else '-'}</div><div class="kpi-sub">{tec_scorecard[0]['total'] if tec_scorecard else 0} pts</div></div>
      <div class="kpi-card red"><div class="kpi-label">Pior</div><div class="kpi-value red" style="font-size:18px">{tec_scorecard[-1]['tecnico'] if tec_scorecard else '-'}</div><div class="kpi-sub">{tec_scorecard[-1]['total'] if tec_scorecard else 0} pts</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Acima de 85</div><div class="kpi-value green">{sum(1 for d in tec_scorecard if d['total']>=85)}</div><div class="kpi-sub">t\u00e9cnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-comp','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.18',this)">C.18</div></div>
    <div class="section-title">\U0001f4ca Scorecard Comparativo \u2014 Nota Total por T\u00e9cnico (m\u00e1x 100)</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;font-size:11px;color:#64748b">
      <span>\u26a0\ufe0f Aging48h /15</span><span>|</span><span>\U0001f527 Rep24h /15</span><span>|</span><span>\u274c Outlier /5</span><span>|</span><span>\u26a0\ufe0f IFI /15</span><span>|</span><span>\U0001f501 IRR /20</span><span>|</span><span>\U0001f4e6 IFIME /10</span><span>|</span><span>\U0001f3af Efetiv /20</span>
    </div>
    <div class="table-wrap" style="max-height:650px;overflow:auto;">
      <table class="data-table" id="tbl-comp"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-comp',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-comp',1,'str')">T\u00e9cnico</th>
        <th class="sortable" onclick="sortTable('tbl-comp',2,'str')" style="text-align:center">CL</th>
        <th class="sortable" onclick="sortTable('tbl-comp',3,'num')" style="text-align:center">Ag48h</th>
        <th class="sortable" onclick="sortTable('tbl-comp',4,'num')" style="text-align:center">Rep24</th>
        <th class="sortable" onclick="sortTable('tbl-comp',5,'num')" style="text-align:center">Out</th>
        <th class="sortable" onclick="sortTable('tbl-comp',6,'num')" style="text-align:center">IFI</th>
        <th class="sortable" onclick="sortTable('tbl-comp',7,'num')" style="text-align:center">IRR</th>
        <th class="sortable" onclick="sortTable('tbl-comp',8,'num')" style="text-align:center">IFME</th>
        <th class="sortable" onclick="sortTable('tbl-comp',9,'num')" style="text-align:center">Efet</th>
        <th class="sortable desc" onclick="sortTable('tbl-comp',10,'num')" style="text-align:center">TOTAL</th>
        <th style="text-align:center">Progresso</th>
      </tr></thead><tbody>{_sctbl(tec_scorecard)}</tbody></table>
    </div>
  </div>

  <!-- SUB: CAUSAS CONSOLIDADAS -->
  <div class="ind-sub" id="ind-causas">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card purple"><div class="kpi-label">Total Causas</div><div class="kpi-value white" id="kpi-causas-total">{len(todas_causas)}</div><div class="kpi-sub">ocorrências</div></div>
      <div class="kpi-card red"><div class="kpi-label">Casos IFI</div><div class="kpi-value red" id="kpi-causas-ifi">{sum(1 for d in todas_causas if d['tipo']=='IFI')}</div><div class="kpi-sub">garantia 15 dias</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">Casos IFIME</div><div class="kpi-value yellow" id="kpi-causas-ifime">{sum(1 for d in todas_causas if d['tipo']=='IFIME')}</div><div class="kpi-sub">mudança endereço</div></div>
      <div class="kpi-card blue"><div class="kpi-label">Casos IRR</div><div class="kpi-value blue" id="kpi-causas-irr">{sum(1 for d in todas_causas if d['tipo']=='IRR')}</div><div class="kpi-sub">reincidência reparo</div></div>
    </div>
    <div class="cluster-filter">
      <div style="display:flex;gap:6px;">
        <div class="cluster-btn active" onclick="filterCausas('tipo','ALL',this)">Todos Tipos</div>
        <div class="cluster-btn" onclick="filterCausas('tipo','IFI',this)">IFI</div>
        <div class="cluster-btn" onclick="filterCausas('tipo','IFIME',this)">IFIME</div>
        <div class="cluster-btn" onclick="filterCausas('tipo','IRR',this)">IRR</div>
      </div>
      <span style="color:#475569;margin:4px 8px;">|</span>
      <div style="display:flex;gap:6px;">
        <div class="cluster-btn active" onclick="filterCausas('cluster','ALL',this)">Todos Clusters</div>
        <div class="cluster-btn" onclick="filterCausas('cluster','C.15',this)">C.15</div>
        <div class="cluster-btn" onclick="filterCausas('cluster','C.16',this)">C.16</div>
        <div class="cluster-btn" onclick="filterCausas('cluster','C.17',this)">C.17</div>
        <div class="cluster-btn" onclick="filterCausas('cluster','C.18',this)">C.18</div>
      </div>
    </div>
    <div class="section-title">📋 Consolidado de Causas (IFI, IFIME, IRR)</div>
    <div class="table-wrap" style="max-height:650px;overflow:auto;">
      <table class="data-table" id="tbl-causas"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-causas',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-causas',1,'str')" style="text-align:center">Indicador</th>
        <th class="sortable" onclick="sortTable('tbl-causas',2,'str')" style="text-align:center">CL</th>
        <th class="sortable" onclick="sortTable('tbl-causas',3,'str')">Técnico</th>
        <th class="sortable" onclick="sortTable('tbl-causas',4,'str')">O.S.</th>
        <th class="sortable" onclick="sortTable('tbl-causas',5,'str')">Cidade</th>
        <th class="sortable" onclick="sortTable('tbl-causas',6,'str')">Data</th>
        <th class="sortable" onclick="sortTable('tbl-causas',7,'str')">Motivo</th>
      </tr></thead><tbody>{_causas_tbl(todas_causas)}</tbody></table>
    </div>
  </div>

  <!-- DRILL-DOWN MODAL -->
  <div class="drill-overlay" id="drill-overlay" onclick="if(event.target===this)closeDrill()">
    <div class="drill-box">
      <span class="drill-close" onclick="closeDrill()">&times;</span>
      <div id="drill-content"></div>
    </div>
  </div>

  <script>
  var _rawIRR = {irr_json};
  var _rawIFI = {ifi_json};
  var _rawIFIME = {ifime_json};
  function showIndSub(id, btn) {{
    document.querySelectorAll('.ind-sub').forEach(function(s){{ s.classList.remove('active'); }});
    document.querySelectorAll('.ind-tab').forEach(function(b){{ b.classList.remove('active'); }});
    document.getElementById(id).classList.add('active');
    if(btn) btn.classList.add('active');
  }}
  function filterCluster(tableId, cluster, btn) {{
    var tbl = document.getElementById(tableId);
    if(!tbl) return;
    var rows = tbl.querySelectorAll('tbody tr');
    rows.forEach(function(r){{
      if(cluster === 'ALL') {{ r.style.display=''; }}
      else {{ r.style.display = r.getAttribute('data-cluster') === cluster ? '' : 'none'; }}
    }});
    btn.parentElement.querySelectorAll('.cluster-btn').forEach(function(b){{ b.classList.remove('active'); }});
    btn.classList.add('active');
  }}
  var _fcState = {{ tipo: 'ALL', cluster: 'ALL' }};
  function filterCausas(tipoFiltro, valor, btn) {{
    _fcState[tipoFiltro] = valor;
    var tbl = document.getElementById('tbl-causas');
    if(!tbl) return;
    var rows = tbl.querySelectorAll('tbody tr');
    var countTotal = 0, countIFI = 0, countIFIME = 0, countIRR = 0;
    rows.forEach(function(r){{
      var matchTipo = _fcState.tipo === 'ALL' || r.getAttribute('data-tipo') === _fcState.tipo;
      var matchCluster = _fcState.cluster === 'ALL' || r.getAttribute('data-cluster') === _fcState.cluster;
      var isVisible = (matchTipo && matchCluster);
      r.style.display = isVisible ? '' : 'none';
      if(isVisible) {{
        countTotal++;
        var t = r.getAttribute('data-tipo');
        if(t==='IFI') countIFI++;
        else if(t==='IFIME') countIFIME++;
        else if(t==='IRR') countIRR++;
      }}
    }});
    btn.parentElement.querySelectorAll('.cluster-btn').forEach(function(b){{ b.classList.remove('active'); }});
    btn.classList.add('active');
    var elTot = document.getElementById('kpi-causas-total'); if(elTot) elTot.innerText = countTotal;
    var elIfi = document.getElementById('kpi-causas-ifi'); if(elIfi) elIfi.innerText = countIFI;
    var elIfime = document.getElementById('kpi-causas-ifime'); if(elIfime) elIfime.innerText = countIFIME;
    var elIrr = document.getElementById('kpi-causas-irr'); if(elIrr) elIrr.innerText = countIRR;
  }}
  function showDrill(tipo, tec) {{
    var data = tipo === 'irr' ? _rawIRR : tipo === 'ifime' ? _rawIFIME : _rawIFI;
    var filtered = data.filter(function(d){{ return d.tecnico === tec; }});
    var title = tipo === 'irr' ? '🔁 IRR - ' + tec : '⚠️ IFI - ' + tec;
    var h = '<div class="section-title" style="margin-bottom:16px;">' + title + ' (' + filtered.length + ' registros)</div>';
    h += '<table class="data-table"><thead><tr><th>O.S.</th><th>Cidade</th><th>Motivo</th><th>Data</th>';
    if(tipo === 'ifi') h += '<th>IFME</th>';
    h += '</tr></thead><tbody>';
    filtered.forEach(function(d) {{
      h += '<tr><td style="font-family:var(--font-mono)">' + d.os + '</td><td>' + d.cidade + '</td><td style="font-size:11px;max-width:300px;word-break:break-word">' + d.motivo + '</td><td style="font-family:var(--font-mono)">' + d.data + '</td>';
      if(tipo === 'ifi') h += '<td style="text-align:center">' + (d.ifme ? '<span class="badge red">Sim</span>' : '<span class="badge green">N\\u00e3o</span>') + '</td>';
      h += '</tr>';
    }});
    h += '</tbody></table>';
    document.getElementById('drill-content').innerHTML = h;
    document.getElementById('drill-overlay').classList.add('show');
  }}
  function closeDrill() {{
    document.getElementById('drill-overlay').classList.remove('show');
  }}
  </script>
</div>
"""
    return html
