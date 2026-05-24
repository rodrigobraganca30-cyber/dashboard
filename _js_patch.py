"""Patch JS section of indicadores_html_gen.py"""
filepath = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the script section
old_script = """  <script>
  var _rawIRR = {irr_json};
  var _rawIFI = {ifi_json};"""

new_script = """  <script>
  var _rawIRR = {irr_json};
  var _rawIFI = {ifi_json};
  var _rawIFIME = {ifime_json};"""

content = content.replace(old_script, new_script)

# Add ifime_json generation before irr_json
old_json = "    irr_json = json.dumps(raw_irr, ensure_ascii=False)"
new_json = """    irr_json = json.dumps(raw_irr, ensure_ascii=False)
    ifime_json = json.dumps(raw_ifime, ensure_ascii=False)"""
content = content.replace(old_json, new_json)

# Replace showDrill to handle 'ifime' type
old_drill = """  function showDrill(tipo, tec) {{
    var data = tipo === 'irr' ? _rawIRR : _rawIFI;
    var filtered = data.filter(function(d){{ return d.tecnico === tec; }});
    var title = tipo === 'irr' ? '\\xf0\\x9f\\x94\\x81 IRR - ' + tec : '\\xe2\\x9a\\xa0\\xef\\xb8\\x8f IFI - ' + tec;"""

# Actually let me just search for the function signature
old_func = "function showDrill(tipo, tec) {{"
new_func = """function filterCluster(tableId, cluster, btn) {{
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
  function showDrill(tipo, tec) {{"""

content = content.replace(old_func, new_func, 1)

# Update drill to handle ifime
old_data_line = "    var data = tipo === 'irr' ? _rawIRR : _rawIFI;"
new_data_line = "    var data = tipo === 'irr' ? _rawIRR : tipo === 'ifime' ? _rawIFIME : _rawIFI;"
content = content.replace(old_data_line, new_data_line)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("JS PATCHED OK")
