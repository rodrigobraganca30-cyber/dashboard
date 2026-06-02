import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\SVOBODA\Desktop\DASHBOARD\whatsapp_agenda_gen.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ['handlefile', 'csv-input', 'modal', 'mapear', 'xlsx', 'importar', 'drop', 'onchange', 'file', 'reader', 'sheetjs', 'xlsx', 'parse']
for i, l in enumerate(lines):
    ll = l.lower()
    if any(x in ll for x in keywords):
        print(f'{i+1}: {l.rstrip()[:150]}')
