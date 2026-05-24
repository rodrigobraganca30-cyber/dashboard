"""Patch indicadores_html_gen.py to add Comparativo tab"""
fp = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update signature to accept tec_scorecard
old_sig = "                           tec_ifime=None, raw_ifime=None):"
new_sig = "                           tec_ifime=None, raw_ifime=None, tec_scorecard=None):\n    if tec_scorecard is None: tec_scorecard = []"
c = c.replace(old_sig, new_sig)
print("Signature updated")

# 2. Add scorecard table function after _etbl
# Find end of _etbl function
etbl_end = c.find("        return h\n\n    irr_json")
if etbl_end < 0:
    etbl_end = c.find("        return h\r\n\r\n    irr_json")
if etbl_end >= 0:
    insert_pos = etbl_end + len("        return h\n") if "\r\n" not in c[etbl_end:etbl_end+20] else etbl_end + len("        return h\r\n")
    scorecard_func = '''
    def _sctbl(data):
        h = ""
        for i, d in enumerate(data):
            tc = "#22d3a0" if d["total"] >= 85 else "#00e5ff" if d["total"] >= 70 else "#fbbf24" if d["total"] >= 50 else "#ff4d6d"
            def _nc(v, mx): return "#22d3a0" if v == mx else "#fbbf24" if v > 0 else "#ff4d6d"
            cl = d.get("cluster","")
            bar_w = d["total"]
            h += f\'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_aging"],15)};font-weight:600">{d["n_aging"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_rep24"],15)};font-weight:600">{d["n_rep24"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_outlier"],5)};font-weight:600">{d["n_outlier"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_ifi"],15)};font-weight:600">{d["n_ifi"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_irr"],20)};font-weight:600">{d["n_irr"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_ifime"],10)};font-weight:600">{d["n_ifime"]}</td>\'
            h += f\'<td style="text-align:center;color:{_nc(d["n_efetiv"],20)};font-weight:600">{d["n_efetiv"]}</td>\'
            h += f\'<td style="text-align:center"><span style="font-weight:800;font-size:16px;color:{tc}">{d["total"]}</span></td>\'
            h += f\'<td style="min-width:100px"><div style="display:flex;align-items:center;gap:4px"><div style="flex:1;background:rgba(255,255,255,.05);border-radius:3px;height:8px"><div style="width:{bar_w}%;background:{tc};height:100%;border-radius:3px;transition:width .3s"></div></div></div></td></tr>\\n\'
        return h

'''
    c = c[:insert_pos] + scorecard_func + c[insert_pos:]
    print("Scorecard function added")
else:
    print("ERROR: could not find _etbl end")

# 3. Add Comparativo tab button
old_efetiv_tab = "onclick=\"showIndSub('ind-efetiv',this)\">"
idx = c.find(old_efetiv_tab)
if idx >= 0:
    # Find end of the efetiv tab div
    end_div = c.find("</div>\n", idx)
    if end_div < 0:
        end_div = c.find("</div>\r\n", idx)
    insert_after = end_div + len("</div>\n") if "\r\n" not in c[end_div:end_div+10] else end_div + len("</div>\r\n")
    comp_tab = '    <div class="ind-tab" onclick="showIndSub(\'ind-comparativo\',this)">\U0001f4ca Comparativo</div>\n'
    c = c[:insert_after] + comp_tab + c[insert_after:]
    print("Comparativo tab button added")

# 4. Add Comparativo section before the drill-down modal
drill_marker = "  <!-- DRILL-DOWN MODAL -->"
idx_drill = c.find(drill_marker)
if idx_drill >= 0:
    _sc_len = "{len(tec_scorecard)}"
    _sc_avg = "{round(sum(d['total'] for d in tec_scorecard)/max(len(tec_scorecard),1),1)}"
    _sc_best = "{tec_scorecard[0]['tecnico'] if tec_scorecard else '-'}"
    _sc_best_n = "{tec_scorecard[0]['total'] if tec_scorecard else 0}"
    _sc_worst = "{tec_scorecard[-1]['tecnico'] if tec_scorecard else '-'}"
    _sc_worst_n = "{tec_scorecard[-1]['total'] if tec_scorecard else 0}"
    _sc_above85 = "{sum(1 for d in tec_scorecard if d['total']>=85)}"

    comp_section = f"""
  <!-- SUB: COMPARATIVO -->
  <div class="ind-sub" id="ind-comparativo">
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px;">
      <div class="kpi-card purple"><div class="kpi-label">Nota M\\u00e9dia</div><div class="kpi-value white">{_sc_avg}</div><div class="kpi-sub">{_sc_len} t\\u00e9cnicos</div></div>
      <div class="kpi-card green"><div class="kpi-label">Melhor</div><div class="kpi-value green" style="font-size:18px">{_sc_best}</div><div class="kpi-sub">{_sc_best_n} pts</div></div>
      <div class="kpi-card red"><div class="kpi-label">Pior</div><div class="kpi-value red" style="font-size:18px">{_sc_worst}</div><div class="kpi-sub">{_sc_worst_n} pts</div></div>
      <div class="kpi-card" style="border-color:rgba(34,211,160,.4)"><div class="kpi-label">Acima de 85</div><div class="kpi-value green">{_sc_above85}</div><div class="kpi-sub">t\\u00e9cnicos</div></div>
    </div>
    <div class="cluster-filter"><div class="cluster-btn active" onclick="filterCluster('tbl-comp','ALL',this)">Todos</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.15',this)">C.15</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.16',this)">C.16</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.17',this)">C.17</div><div class="cluster-btn" onclick="filterCluster('tbl-comp','C.18',this)">C.18</div></div>
    <div class="section-title">\\U0001f4ca Scorecard Comparativo \\u2014 Nota Total por T\\u00e9cnico (m\\u00e1x 100)</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;font-size:11px;color:#64748b">
      <span>\\u26a0\\ufe0f Aging48h /15</span><span>|</span><span>\\U0001f527 Rep24h /15</span><span>|</span><span>\\u274c Outlier /5</span><span>|</span><span>\\u26a0\\ufe0f IFI /15</span><span>|</span><span>\\U0001f501 IRR /20</span><span>|</span><span>\\U0001f4e6 IFIME /10</span><span>|</span><span>\\U0001f3af Efetiv /20</span>
    </div>
    <div class="table-wrap" style="max-height:650px;overflow:auto;">
      <table class="data-table" id="tbl-comp"><thead><tr>
        <th class="sortable" onclick="sortTable('tbl-comp',0,'num')">#</th>
        <th class="sortable" onclick="sortTable('tbl-comp',1,'str')">T\\u00e9cnico</th>
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
      </tr></thead><tbody>{{_sctbl(tec_scorecard)}}</tbody></table>
    </div>
  </div>

"""
    c = c[:idx_drill] + comp_section + c[idx_drill:]
    print("Comparativo section added")
else:
    print("ERROR: drill marker not found")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("ALL DONE")
