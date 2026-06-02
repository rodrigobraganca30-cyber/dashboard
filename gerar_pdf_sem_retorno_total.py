"""
gerar_pdf_sem_retorno_total.py
Gera um PDF completo de todos os clientes que receberam mensagens (1+) mas NUNCA responderam (0 recebidas).
"""
import paramiko, os, sys, json, datetime as dt
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

# Conecta no VPS para baixar o relatório bruto de mensagens
print('[...] Conectando ao VPS para baixar histórico de mensagens...')
ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

sftp = client.open_sftp()
local_json = r'C:\Users\SVOBODA\Desktop\DASHBOARD\relatorio_wpp.json'
try:
    sftp.get('/tmp/relatorio_wpp.json', local_json)
    print(f'[OK] Histórico baixado para: {local_json}')
except Exception as e:
    print('[AVISO] Relatório não estava no VPS. Gerando no VPS primeiro...')
    # Executa o script analise_wpp.py no VPS
    client.exec_command('python3 /tmp/analise_wpp.py')
    sftp.get('/tmp/relatorio_wpp.json', local_json)
    print(f'[OK] Histórico baixado com sucesso!')

sftp.close()
client.close()

# Carrega os dados
with open(local_json, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Filtra: enviadas >= 1 e recebidas == 0 (nunca responderam)
sem_retorno = [d for d in dados if d.get('enviadas', 0) >= 1 and d.get('recebidas', 0) == 0]
sem_retorno.sort(key=lambda x: x.get('enviadas', 0), reverse=True)

total = len(sem_retorno)
hoje  = dt.datetime.now().strftime('%d/%m/%Y as %H:%M')

print(f'Clientes que receberam mensagens mas nunca responderam: {total}')

# ── PDF ──────────────────────────────────────────────────────────────────────
class PDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)       # dark navy
        self.rect(0, 0, 210, 28, 'F')
        self.set_y(6)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, safe_str('SVOBODA | Clientes que Nunca Responderam'), align='C', ln=True)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, safe_str(f'Gerado em {hoje} - Total Geral de Clientes sem Retorno'), align='C', ln=True)
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

com_retorno = sum(1 for d in dados if d.get('recebidas', 0) > 0)
sem_retorno_total = total

y0 = 35
card(10,  y0, 43, 22, 'TOTAL HISTORICO',      len(dados), (30, 41, 59))
card(58,  y0, 43, 22, 'RESPONDERAM',          com_retorno,     (5,  150, 105))
card(106, y0, 43, 22, 'SEM RETORNO (1+ MSGS)', sem_retorno_total, (220, 38, 38))
card(154, y0, 43, 22, 'TAXA DE RETORNO',      f"{round(com_retorno/len(dados)*100, 1)}%" if len(dados) else "0%", (59, 130, 246))

# ── LINHA EXPLICATIVA ─────────────────────────────────────────────────────────
pdf.set_y(62)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 5.5,
    safe_str(f'Este relatorio lista todos os {total} clientes que receberam pelo menos 1 mensagem via '
    f'WhatsApp Agenda, mas nunca enviaram nenhuma resposta de volta. Os dados refletem o '
    f'historico completo de mensagens extraido em {hoje}.'),
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
for i, row in enumerate(sem_retorno):
    env = int(row.get('enviadas', 0) or 0)

    # Cor da linha conforme a quantidade de disparos sem resposta
    if env >= 5:
        pdf.set_fill_color(254, 226, 226)   # vermelho claro
        pdf.set_text_color(185, 28, 28)
    elif env >= 3:
        pdf.set_fill_color(255, 237, 213)   # laranja claro
        pdf.set_text_color(154, 52, 18)
    elif i % 2 == 0:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(30, 41, 59)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 41, 59)

    nome = (row.get('nome') or 'Sem nome')[:30]
    tel  = row.get('telefone', '')
    rec  = row.get('recebidas', 0)
    
    ult_ts = row.get('ultima_ts', 0)
    ult = ''
    if ult_ts:
        try:
            ult = dt.datetime.fromtimestamp(ult_ts/1000).strftime('%d/%m/%Y %H:%M')
        except:
            pass

    vals = [str(i+1), safe_str(nome), safe_str(tel), str(env), str(rec), safe_str(ult)]
    alns = ['C', 'L', 'L', 'C', 'C', 'C']
    for w, v, a in zip(COL, vals, alns):
        pdf.cell(w, 6, v, border=0, fill=True, align=a)
    pdf.ln()

    # Linha divisória leve
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

# Salva
ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
pdf_path = rf'C:\Users\SVOBODA\Desktop\DASHBOARD\todos_sem_retorno_{ts}.pdf'
pdf.output(pdf_path)
print(f'\n[OK] PDF Geral de sem retorno gerado: {pdf_path}')
print(f'     {total} clientes  |  {pdf.page} paginas')
