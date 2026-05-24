"""Add _sctbl function to indicadores_html_gen.py"""
fp = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(fp, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find line 73 (return h of _etbl) and insert after it
sctbl_lines = [
    '\n',
    '    def _sctbl(data):\n',
    '        h = ""\n',
    '        for i, d in enumerate(data):\n',
    '            tc = "#22d3a0" if d["total"] >= 85 else "#00e5ff" if d["total"] >= 70 else "#fbbf24" if d["total"] >= 50 else "#ff4d6d"\n',
    '            def _nc(v, mx): return "#22d3a0" if v == mx else "#fbbf24" if v > 0 else "#ff4d6d"\n',
    '            cl = d.get("cluster","")\n',
    """            h += f'<tr data-cluster="{cl}"><td>{i+1}</td><td style="font-weight:600;color:#e8eaf6">{d["tecnico"]}</td><td style="text-align:center;font-size:11px;color:#64748b">{cl}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_aging"],15)};font-weight:600">{d["n_aging"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_rep24"],15)};font-weight:600">{d["n_rep24"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_outlier"],5)};font-weight:600">{d["n_outlier"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_ifi"],15)};font-weight:600">{d["n_ifi"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_irr"],20)};font-weight:600">{d["n_irr"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_ifime"],10)};font-weight:600">{d["n_ifime"]}</td>'\n""",
    """            h += f'<td style="text-align:center;color:{_nc(d["n_efetiv"],20)};font-weight:600">{d["n_efetiv"]}</td>'\n""",
    """            h += f'<td style="text-align:center"><span style="font-weight:800;font-size:16px;color:{tc}">{d["total"]}</span></td>'\n""",
    """            h += f'<td style="min-width:100px"><div style="display:flex;align-items:center;gap:4px"><div style="flex:1;background:rgba(255,255,255,.05);border-radius:3px;height:8px"><div style="width:{d["total"]}%;background:{tc};height:100%;border-radius:3px"></div></div></div></td></tr>\\n'\n""",
    '        return h\n',
    '\n',
]

# Insert after line 73 (index 72)
for i, l in enumerate(lines):
    if 'return h' in l and i >= 72 and i <= 74:
        insert_at = i + 1
        break

lines[insert_at:insert_at] = sctbl_lines
with open(fp, "w", encoding="utf-8") as f:
    f.writelines(lines)
print(f"Inserted _sctbl at line {insert_at+1}")
