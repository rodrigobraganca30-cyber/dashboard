fp = r"C:\Users\SVOBODA\Desktop\DASHBOARD\indicadores_html_gen.py"
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove GIGA+ tab button
old_btn = '    <div class="ind-tab active" onclick="showIndSub(\'ind-giga\',this)">\U0001f3af Ranking GIGA+</div>\n'
c = c.replace(old_btn, '')
print("Tab button removed" if old_btn not in c else "WARN: button not found")

# 2. Make Altas the default active tab button  
c = c.replace(
    """<div class="ind-tab" onclick="showIndSub('ind-altas',this)">""",
    """<div class="ind-tab active" onclick="showIndSub('ind-altas',this)">"""
)

# 3. Remove GIGA+ section content
m1 = '  <!-- SUB: GIGA+ (existente) -->'
m2 = '  <!-- SUB: ALTAS -->'
i1 = c.find(m1)
i2 = c.find(m2)
if i1 >= 0 and i2 > i1:
    c = c[:i1] + c[i2:]
    print(f"Removed GIGA+ section ({i2-i1} chars)")
else:
    print(f"WARN: GIGA+ section not found (i1={i1}, i2={i2})")

# 4. Make Altas div active
c = c.replace(
    '<div class="ind-sub" id="ind-altas">',
    '<div class="ind-sub active" id="ind-altas">'
)

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Done")
