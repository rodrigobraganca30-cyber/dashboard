"""
gerar_pdf_relatorio.py
Gera PDF elaborado do relatório de clientes sem retorno.
"""
import csv, datetime as dt, os, sys
from fpdf import FPDF

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def safe_str(s):
    if not s:
        return ""
    # Substitui caracteres que podem vir corrompidos ou com acentos
    s = str(s).replace('ã', 'a').replace('õ', 'o').replace('ç', 'c').replace('é', 'e').replace('á', 'a').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    s = s.replace('Â', 'A').replace('Ê', 'E').replace('Î', 'I').replace('Ô', 'O').replace('Û', 'U')
    s = s.replace('â', 'a').replace('ê', 'e').replace('î', 'i').replace('ô', 'o').replace('û', 'u')
    s = s.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    s = s.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
    s = s.replace('\xaa', 'a').replace('\xba', 'o')
    return s.encode('latin-1', errors='replace').decode('latin-1')

# Localiza o CSV mais recente
PASTA = r'C:\Users\SVOBODA\Desktop\DASHBOARD'
csvs = sorted([f for f in os.listdir(PASTA) if f.startswith('sem_retorno_') and f.endswith('.csv')], reverse=True)
if not csvs:
    print('[ERRO] Nenhum CSV encontrado. Rode relatorio_sem_retorno.py primeiro.')
    sys.exit(1)

csv_path = os.path.join(PASTA, csvs[0])
print(f'[OK] Usando: {csv_path}')

# Lê os dados
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

rows.sort(key=lambda x: int(x.get('Msgs Enviadas', 0) or 0), reverse=True)
total = len(rows)
hoje  = dt.datetime.now().strftime('%d/%m/%Y as %H:%M')

# ── PDF ──────────────────────────────────────────────────────────────────────
class PDF(FPDF):
    def header(self):
        # Faixa de topo
        self.set_fill_color(15, 23, 42)       # dark navy
        self.rect(0, 0, 210, 28, 'F')
        self.set_y(6)
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, safe_str('SVOBODA | Relatorio de Disparos sem Retorno'), align='C', ln=True)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, safe_str(f'Gerado em {hoje} - WhatsApp Agenda'), align='C', ln=True)
        self.set_y(32)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-13)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, safe_str(f'Pagina {self.page_no()} / {{nb}} - Confidencial - uso interno'), align='C')

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

# Lê estatísticas totais de outro CSV se existir
total_historico = 2755
responderam     = 1522
sem_1msg        = 828
sem_2msg        = 218

y0 = 35
card(10,  y0, 43, 22, 'TOTAL HISTORICO',      total_historico, (30, 41, 59))
card(58,  y0, 43, 22, 'RESPONDERAM',          responderam,     (5,  150, 105))
card(106, y0, 43, 22, '1-2 DISPAROS S/ RET',  sem_1msg+sem_2msg, (100, 116, 139))
card(154, y0, 43, 22, '3+ DISP. SEM RETORNO', total,           (220, 38, 38))

# ── LINHA EXPLICATIVA ─────────────────────────────────────────────────────────
pdf.set_y(62)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 5.5,
    safe_str(f'Este relatorio lista {total} clientes que receberam 3 ou mais mensagens via WhatsApp Agenda '
    f'e nunca enviaram nenhuma resposta. Os dados foram extraidos do historico de conversas '
    f'em {hoje}. Clientes com numero inativo ou sem WhatsApp aparecem marcados como "Sem nome".'),
    align='J')
pdf.ln(3)

# ── TABELA ───────────────────────────────────────────────────────────────────
COL = [8, 68, 40, 28, 28, 28]   # larguras
HDR = ['#', 'Nome', 'Telefone', 'Enviadas', 'Recebidas', 'Ultima Msg']

# Cabeçalho
pdf.set_fill_color(15, 23, 42)
pdf.set_text_color(255, 255, 255)
pdf.set_font('Helvetica', 'B', 8)
for w, h in zip(COL, HDR):
    pdf.cell(w, 7, safe_str(h), border=0, fill=True, align='C')
pdf.ln()

# Linhas
pdf.set_font('Helvetica', '', 8)
for i, row in enumerate(rows):
    env = int(row.get('Msgs Enviadas', 0) or 0)

    # Cor da linha
    if env >= 8:
        pdf.set_fill_color(254, 226, 226)   # vermelho claro
        pdf.set_text_color(185, 28, 28)
    elif env >= 5:
        pdf.set_fill_color(255, 237, 213)   # laranja claro
        pdf.set_text_color(154, 52, 18)
    elif i % 2 == 0:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(30, 41, 59)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 41, 59)

    nome = (row.get('Nome') or 'Sem nome')[:30]
    tel  = row.get('Telefone', '')
    rec  = row.get('Msgs Recebidas', '0')
    ult  = row.get('Ultima Msg Enviada', '')

    vals = [str(i+1), safe_str(nome), safe_str(tel), str(env), str(rec), safe_str(ult)]
    alns = ['C', 'L', 'L', 'C', 'C', 'C']
    for w, v, a in zip(COL, vals, alns):
        pdf.cell(w, 6, v, border=0, fill=True, align=a)
    pdf.ln()

    # Linha divisória leve
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

# ── LEGENDA ──────────────────────────────────────────────────────────────────
pdf.ln(4)
pdf.set_font('Helvetica', 'B', 8)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 5, safe_str('Legenda:'), ln=True)
pdf.set_font('Helvetica', '', 8)

def legend_box(r, g, b, txt):
    pdf.set_fill_color(r, g, b)
    pdf.rect(pdf.get_x(), pdf.get_y()+1, 5, 4, 'F')
    pdf.set_x(pdf.get_x() + 7)
    pdf.cell(50, 6, safe_str(txt))

pdf.set_xy(10, pdf.get_y())
legend_box(254, 226, 226, '8+ disparos enviados')
pdf.set_xy(70, pdf.get_y())
legend_box(255, 237, 213, '5 a 7 disparos enviados')
pdf.set_xy(130, pdf.get_y())
legend_box(248, 250, 252, '3 a 4 disparos enviados')
pdf.ln(8)

pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(100, 116, 139)
pdf.multi_cell(0, 5,
    safe_str('Nota: Clientes com "Sem nome" podem indicar numeros sem WhatsApp ativo, '
    'numeros internacionais ou contatos nao cadastrados na agenda.'))

# Salva
ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
pdf_path = rf'C:\Users\SVOBODA\Desktop\DASHBOARD\relatorio_sem_retorno_{ts}.pdf'
pdf.output(pdf_path)
print(f'\n[OK] PDF gerado: {pdf_path}')
print(f'     {total} clientes  |  {pdf.page} paginas')
