"""Patch indicadores_html_gen.py to replace IFI section and add IFIME"""
import sys

filepath = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find IFI section (line 203) and EFETIVIDADE section
ifi_start = None
efetiv_start = None
for i, line in enumerate(lines):
    if "<!-- SUB: IFI -->" in line and ifi_start is None:
        ifi_start = i
    if "<!-- SUB: EFETIVIDADE -->" in line:
        efetiv_start = i

print(f"IFI starts at line {ifi_start+1}, EFETIVIDADE at line {efetiv_start+1}")

new_ifi_section = '''  <!-- SUB: IFI -->
  <div class="ind-sub" id="ind-ifi">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IFI</div><div class="kpi-value red">{{_tf}}</div><div class="kpi-sub">garantia 15 dias</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IFI Equipe</div><div class="kpi-value yellow">{{round(sum(d['qtd'] for d in tec_ifi)/max(sum(d.get('altas',0) for d in tec_ifi),1)*100,2)}}%</div><div class="kpi-sub">meta: &lt;2,7%</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{{sum(1 for d in tec_ifi if d.get('pct_ifi',0)<d.get('meta100',2.7))}}</div><div class="kpi-sub">t\\u00e9cnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{{sum(1 for d in tec_ifi if d.get('pct_ifi',0)>=d.get('meta100',2.7) and d['qtd']>0)}}</div><div class="kpi-sub">t\\u00e9cnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-ifi','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-ifi','C.18',this)">C.18</div></div>
    <div class="section-title">\\u26a0\\ufe0f IFI por T\\u00e9cnico \\u2014 Garantia 15 dias (Ativa\\u00e7\\u00e3o)</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-ifi"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-ifi',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',1,'str')">T\\u00e9cnico</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',3,'num')" style="text-align:center">Ativa\\u00e7\\u00f5es</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',4,'num')" style="text-align:center">Casos</th>
        <th class="sortable desc" onclick="sortTable('tbl-ifi',5,'num')" style="text-align:center">% IFI</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-ifi',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">\\ud83d\\udd0d</th>
      </tr></thead><tbody>{{_ftbl(tec_ifi)}}</tbody></table>
    </div>
  </div>

  <!-- SUB: IFIME -->
  <div class="ind-sub" id="ind-ifime">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card red"><div class="kpi-label">Total IFIME</div><div class="kpi-value red">{{sum(d['qtd'] for d in tec_ifime)}}</div><div class="kpi-sub">garantia 30 dias</div></div>
      <div class="kpi-card yellow"><div class="kpi-label">% IFIME Equipe</div><div class="kpi-value yellow">{{round(sum(d['qtd'] for d in tec_ifime)/max(sum(d.get('mes_total',0) for d in tec_ifime),1)*100,2)}}%</div><div class="kpi-sub">meta: &lt;3,25%</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Dentro da Meta</div><div class="kpi-value green">{{sum(1 for d in tec_ifime if d.get('pct_ifime',0)<d.get('meta100',3.25))}}</div><div class="kpi-sub">t\\u00e9cnicos</div></div>
      <div class="kpi-card" style="border-color:rgba(255,77,109,.4)"><div class="kpi-label">Acima da Meta</div><div class="kpi-value red">{{sum(1 for d in tec_ifime if d.get('pct_ifime',0)>=d.get('meta100',3.25) and d['qtd']>0)}}</div><div class="kpi-sub">t\\u00e9cnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-ifime','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-ifime','C.18',this)">C.18</div></div>
    <div class="section-title">\\ud83d\\udce6 IFIME por T\\u00e9cnico \\u2014 Garantia 30 dias (Mud. Endere\\u00e7o)</div>
    <div class="table-wrap" style="max-height:600px;overflow:auto;">
      <table class="data-table" id="tbl-ifime"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-ifime',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',1,'str')">T\\u00e9cnico</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',2,'str')" style="text-align:center">Cluster</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',3,'num')" style="text-align:center">Mud. End.</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',4,'num')" style="text-align:center">Casos</th>
        <th class="sortable desc" onclick="sortTable('tbl-ifime',5,'num')" style="text-align:center">% IFIME</th>
        <th style="text-align:center">Meta</th>
        <th class="sortable" onclick="sortTable('tbl-ifime',7,'num')" style="text-align:center">Nota</th>
        <th style="text-align:center">\\ud83d\\udd0d</th>
      </tr></thead><tbody>{{_fmtbl(tec_ifime)}}</tbody></table>
    </div>
  </div>

'''

# Replace lines from ifi_start to efetiv_start (exclusive)
new_lines = lines[:ifi_start] + [new_ifi_section] + lines[efetiv_start:]

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("PATCHED OK")
