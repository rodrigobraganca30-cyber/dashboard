"""Patch IRR table function and HTML section in indicadores_html_gen.py"""
filepath = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace _itbl function
old_itbl = '''    def _itbl(data):
        h = ""
        for i, d in enumerate(data):
            c = "#ff4d6d" if d["qtd"] >= 5 else "#fbbf24" if d["qtd"] >= 3 else "#22d3a0"
            h += f\'<tr><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-weight:700;color:{c}">{d["qtd"]}</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\\\'irr\\\',\\\'{d["tecnico"].replace(chr(39),"")}\\\')">\N{LEFT-POINTING MAGNIFYING GLASS} Ver</td></tr>\\n\'
        return h'''

new_itbl = '''    def _itbl(data):
        h = ""
        for i, d in enumerate(data):
            pct = d.get("pct_irr", 0)
            m = d.get("meta100", 6.2)
            pc = "#22d3a0" if pct < m else "#fbbf24" if pct < m*1.05 else "#ff4d6d"
            nc = "#22d3a0" if d.get("nota",0) > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            h += f\'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td><td style="text-align:center">{d.get("reparos",0)}</td><td style="text-align:center;font-weight:700;color:{pc}">{d["qtd"]}</td><td style="text-align:center;font-weight:700;color:{pc}">{pct}%</td><td style="text-align:center;font-size:11px">&lt;{m}%</td><td style="text-align:center;color:{nc};font-weight:700">{d.get("nota",0)}/20</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\\\'irr\\\',\\\'{d["tecnico"].replace(chr(39,""))}\\\')">\N{LEFT-POINTING MAGNIFYING GLASS}</td></tr>\\n\'
        return h'''

if old_itbl in content:
    content = content.replace(old_itbl, new_itbl)
    print("_itbl replaced OK")
else:
    print("WARNING: _itbl not found, trying line-based approach")
    lines = content.split('\n')
    itbl_start = None
    itbl_end = None
    for i, line in enumerate(lines):
        if 'def _itbl(data):' in line:
            itbl_start = i
        if itbl_start and i > itbl_start and 'return h' in line and 'def ' not in line:
            itbl_end = i + 1
            break
    if itbl_start and itbl_end:
        new_lines = [
            '    def _itbl(data):',
            '        h = ""',
            '        for i, d in enumerate(data):',
            '            pct = d.get("pct_irr", 0)',
            '            m = d.get("meta100", 6.2)',
            '            pc = "#22d3a0" if pct < m else "#fbbf24" if pct < m*1.05 else "#ff4d6d"',
            '            nc = "#22d3a0" if d.get("nota",0) > 0 else "#ff4d6d"',
            '            cl = d.get("cluster","")',
            """            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td><td style="text-align:center">{d.get("reparos",0)}</td><td style="text-align:center;font-weight:700;color:{pc}">{d["qtd"]}</td><td style="text-align:center;font-weight:700;color:{pc}">{pct}%</td><td style="text-align:center;font-size:11px">&lt;{m}%</td><td style="text-align:center;color:{nc};font-weight:700">{d.get("nota",0)}/20</td><td style="text-align:center;cursor:pointer;color:var(--accent)" onclick="showDrill(\\\'irr\\\',\\\'{ d["tecnico"].replace(chr(39),"") }\\\')">\U0001f50d</td></tr>\\n'""",
            '        return h',
        ]
        lines[itbl_start:itbl_end] = new_lines
        content = '\n'.join(lines)
        print(f"_itbl replaced via line splice ({itbl_start}-{itbl_end})")
    else:
        print("ERROR: Could not find _itbl boundaries")

# 2. Replace IRR HTML section
# Find the IRR section boundaries
irr_start_marker = '  <!-- SUB: IRR -->'
ifi_start_marker = '  <!-- SUB: IFI -->'
idx_irr = content.find(irr_start_marker)
idx_ifi = content.find(ifi_start_marker)
if idx_irr >= 0 and idx_ifi > idx_irr:
    new_irr_section = """  <!-- SUB: IRR -->
  <div class="ind-sub" id="ind-irr">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IRR</div><div class="kpi-value red">{_ti}</div><div class="kpi-sub">reincid\u00eancias reparo</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IRR Equipe</div><div class="kpi-value yellow">{round(sum(d['qtd'] for d in tec_irr)/max(sum(d.get('reparos',0) for d in tec_irr),1)*100,2)}%</div><div class="kpi-sub">meta por cluster</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{sum(1 for d in tec_irr if d.get('pct_irr',0)<d.get('meta100',6.2))}</div><div class="kpi-sub">t\u00e9cnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{sum(1 for d in tec_irr if d.get('pct_irr',0)>=d.get('meta100',6.2) and d['qtd']>0)}</div><div class="kpi-sub">t\u00e9cnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-irr','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-irr','C.18',this)">C.18</div></div>
    <div class="section-title">\U0001f501 IRR por T\u00e9cnico \u2014 Reincid\u00eancia Reparo</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-irr"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-irr',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-irr',1,'str')">T\u00e9cnico</th>
        <th class="sortable" onclick="sortTable('tbl-irr',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-irr',3,'num')" style="text-align:center">Reparos</th>
        <th class="sortable" onclick="sortTable('tbl-irr',4,'num')" style="text-align:center">Casos IRR</th>
        <th class="sortable desc" onclick="sortTable('tbl-irr',5,'num')" style="text-align:center">% IRR</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-irr',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">\U0001f50d</th>
      </tr></thead><tbody>{_itbl(tec_irr)}</tbody></table>
    </div>
  </div>

"""
    content = content[:idx_irr] + new_irr_section + content[idx_ifi:]
    print("IRR HTML section replaced OK")
else:
    print(f"ERROR: IRR section not found (irr={idx_irr}, ifi={idx_ifi})")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("DONE")
