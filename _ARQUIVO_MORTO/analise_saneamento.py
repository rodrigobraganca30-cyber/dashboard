"""
analise_saneamento.py
Analisa todos os clientes no banco de dados para identificar números inválidos
que causam o erro 131026 (Receiver is not a valid WhatsApp user).
Gera um PDF executivo bem elaborado com esta análise.
"""
import paramiko, os, sys, json, re, datetime as dt
from fpdf import FPDF
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def safe_str(s):
    if not s:
        return ""
    s = str(s).replace('ã', 'a').replace('õ', 'o').replace('ç', 'c').replace('é', 'e').replace('á', 'a').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    s = s.replace('Â', 'A').replace('Ê', 'E').replace('Î', 'I').replace('Ô', 'O').replace('Û', 'U')
    s = s.replace('â', 'a').replace('ê', 'e').replace('î', 'i').replace('ô', 'o').replace('û', 'u')
    s = s.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    s = s.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
    s = s.replace('\xaa', 'a').replace('\xba', 'o')
    return s.encode('latin-1', errors='replace').decode('latin-1')

# Carrega os dados locais do banco de dados (baixados anteriormente)
local_json = r'C:\Users\SVOBODA\Desktop\DASHBOARD\relatorio_wpp.json'
if not os.path.exists(local_json):
    print('[ERRO] relatorio_wpp.json nao encontrado localmente.')
    sys.exit(1)

with open(local_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Saneamento e Análise de Números
clientes_invalidos = []
for d in dados:
    nome = d.get('nome') or 'Sem nome'
    phone_full = d.get('telefone', '')
    enviadas = d.get('enviadas', 0)
    
    # Limpa o número para analisar
    num = phone_full.replace('+', '').replace('-', '').replace(' ', '')
    
    motivo = ""
    
    # 1. Verifica números muito longos ou estranhos (internacionais malformados)
    if len(num) > 13 or (not num.startswith('55') and len(num) > 11):
        motivo = "Tamanho Invalido (Muito longo/Malformado)"
    # 2. Números brasileiros
    elif num.startswith('55'):
        ddd_e_numero = num[2:]
        if len(ddd_e_numero) < 10:
            motivo = "Tamanho Invalido (Muito curto)"
        elif len(ddd_e_numero) == 10:
            # DDD (2) + Número (8)
            primeiro_digito = ddd_e_numero[2]
            if primeiro_digito in ['2', '3', '4', '5']:
                motivo = "Numero Fixo (Sem WhatsApp ativo)"
            else:
                motivo = "Falta do 9o digito (Celular antigo)"
        elif len(ddd_e_numero) == 11:
            # DDD (2) + Número (9)
            primeiro_digito = ddd_e_numero[2]
            if primeiro_digito != '9':
                motivo = "Celular Invalido (Nao comeca com 9)"
    else:
        # Sem código de país ou formato estranho
        if len(num) < 10:
            motivo = "Numero Incompleto/Faltando DDD"
        else:
            motivo = "Formato Estranho (Sem codigo de pais 55)"
            
    if motivo:
        clientes_invalidos.append({
            'nome': nome,
            'telefone': phone_full,
            'motivo': motivo,
            'enviadas': enviadas
        })

# Ordena por mensagens enviadas para sabermos quais gastaram mais disparos à toa
clientes_invalidos.sort(key=lambda x: x['enviadas'], reverse=True)

total_invalidos = len(clientes_invalidos)
total_geral = len(dados)
hoje  = dt.datetime.now().strftime('%d/%m/%Y as %H:%M')

print(f'Total de números com suspeita de erro 131026: {total_invalidos} de {total_geral}')

# ── PDF ──────────────────────────────────────────────────────────────────────
class PDF(FPDF):
    def header(self):
        # Top Header
        self.set_fill_color(15, 23, 42)       # dark navy
        self.rect(0, 0, 210, 28, 'F')
        self.set_y(6)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, safe_str('SVOBODA | Auditoria de Numeros & Erro Meta 131026'), align='C', ln=True)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, safe_str(f'Relatorio de Saneamento de Banco de Dados * Gerado em {hoje}'), align='C', ln=True)
        self.set_y(32)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-13)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, safe_str(f'Pagina {self.page_no()} / {{nb}} - Relatorio Técnico de Erros Meta - Confidencial'), align='C')

pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=16)

# ── CARDS DE RESUMO ──────────────────────────────────────────────────────────
def card(x, y, w, h, titulo, valor, cor_fundo, cor_texto=(255,255,255)):
    pdf.set_fill_color(*cor_fundo)
    pdf.set_draw_color(*cor_fundo)
    pdf.rect(x, y, w, h, 'F')
    pdf.set_xy(x, y + 4)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*cor_texto)
    pdf.set_x(x)
    pdf.cell(w, 8, safe_str(valor), align='C')
    pdf.set_xy(x, y + 13)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(220, 230, 240)
    pdf.cell(w, 5, safe_str(titulo), align='C')

y0 = 35
card(10,  y0, 43, 22, 'TOTAL DE CONTATOS',   total_geral, (30, 41, 59))
card(58,  y0, 43, 22, 'NUMEROS SUSPEITOS',    total_invalidos, (220, 38, 38))
card(106, y0, 43, 22, 'TAXA DE ERRO 131026',  f"{round(total_invalidos/total_geral*100, 1)}%" if total_geral else "0%", (249, 115, 22))
card(154, y0, 43, 22, 'DISPAROS PERDIDOS',    sum(c['enviadas'] for c in clientes_invalidos), (100, 116, 139))

# ── LINHA EXPLICATIVA ─────────────────────────────────────────────────────────
pdf.set_y(62)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(15, 23, 42)
pdf.cell(0, 6, safe_str('O que e o Erro Meta 131026?'), ln=True)
pdf.set_font('Helvetica', '', 9.5)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 5,
    safe_str('O erro 131026 ("Receiver is not a valid WhatsApp user") ocorre quando um disparo via API Oficial '
    'e enviado para um numero que nao possui WhatsApp ativo (como telefones fixos, numeros com formato incorreto '
    'ou sem o nono digito). Como o painel ignora os status assincronos, estes contatos continuam ativos consumindo '
    'disparos inutilmente. Este relatorio mapeia esses numeros por meio de analise de regras de formato.'),
    align='J')
pdf.ln(4)

# ── TABELA ───────────────────────────────────────────────────────────────────
COL = [8, 62, 38, 62, 24]   # larguras
HDR = ['#', 'Nome', 'Telefone', 'Motivo da Falha / Erro 131026', 'Disparos']

# Cabeçalho
pdf.set_fill_color(15, 23, 42)
pdf.set_text_color(255, 255, 255)
pdf.set_font('Helvetica', 'B', 8)
for w, h in zip(COL, HDR):
    pdf.cell(w, 7, safe_str(h), border=0, fill=True, align='C')
pdf.ln()

# Linhas
pdf.set_font('Helvetica', '', 8)
for i, row in enumerate(clientes_invalidos):
    mot = row['motivo']
    
    # Cores diferenciadas por criticidade
    if "Fixo" in mot or "Invalido" in mot:
        pdf.set_fill_color(254, 226, 226)   # vermelho claro
        pdf.set_text_color(185, 28, 28)
    else:
        pdf.set_fill_color(255, 237, 213)   # laranja claro
        pdf.set_text_color(154, 52, 18)
        
    if i % 2 == 0 and "Fixo" not in mot and "Invalido" not in mot:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(30, 41, 59)

    vals = [str(i+1), safe_str(row['nome'][:28]), safe_str(row['telefone']), safe_str(row['motivo']), str(row['enviadas'])]
    alns = ['C', 'L', 'L', 'L', 'C']
    for w, v, a in zip(COL, vals, alns):
        pdf.cell(w, 6, v, border=0, fill=True, align=a)
    pdf.ln()

    # Linha divisória leve
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

# Salva
ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
pdf_path = rf'C:\Users\SVOBODA\Desktop\DASHBOARD\relatorio_saneamento_erro_131026.pdf'
pdf.output(pdf_path)
print(f'\n[OK] PDF de saneamento gerado: {pdf_path}')
print(f'     {total_invalidos} clientes invalidos  |  {pdf.page} paginas')
