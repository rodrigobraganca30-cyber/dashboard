f = open(r"C:\Users\SVOBODA\Desktop\DASHBOARD\dashboard_svoboda_atualizado.html","r",encoding="utf-8")
c = f.read()
f.close()
idx = c.find('id="tbl-comp"')
tbody_idx = c.find('<tbody>', idx)
print(f"tbody at {tbody_idx}")
snippet = c[tbody_idx:tbody_idx+500]
with open(r"C:\Users\SVOBODA\Desktop\DASHBOARD\_debug_comp.txt","w",encoding="utf-8") as out:
    out.write(snippet)
