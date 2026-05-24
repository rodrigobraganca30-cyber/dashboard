#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para compilar o README.md (PRD) do Dashboard Svoboda Telecomunicações em um PDF corporativo elegante.
"""
import os
import re
from datetime import datetime
from fpdf import FPDF

class PRDPDF(FPDF):
    def header(self):
        # Apenas exibe cabeçalho a partir da página 2
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, 'SVOBODA TELECOMUNICAÇÕES - DOCUMENTO DE REQUISITOS (PRD)', align='R', new_x='LMARGIN', new_y='NEXT')
            self.set_draw_color(220, 220, 220)
            self.set_line_width(0.3)
            self.line(10, 16, 200, 16)
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.3)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        
        # Numeração de página
        self.cell(0, 10, f'Página {self.page_no()}', align='C')


def sanitize(text):
    """Remove emojis e formata para codificação latin-1 padrão."""
    emojis = {
        '📊': '[BI] ', '🚀': '[PRD] ', '🏗️': '[ARQ] ', '📁': '[DIR] ', '🤖': '[JARVIS] ',
        '💬': '[WA] ', '📈': '[SHEETS] ', '🔐': '[SEC] ', '🛠️': '[DEV] ', '💻': '[PC] ',
        '⚙️': '[CFG] ', '🔄': '[RUN] ', '🧠': '[AI] ', '💾': '[MEM] ', '📝': '[DOC] ',
        '🐳': '[DOCKER] ', '🔑': '[KEY] ', '🛡️': '[SEC] ', '✅': '[OK] ', '❌': '[ERRO] ',
        '📌': '[INFO] ', '📍': '[LOC] ', '🚗': '[CAR] ', '⛽': '[FUEL] ', '🛣️': '[DESL] ',
        '🗓️': '[CAL] ', '🗓': '[CAL] ', '🔧': '[MANUT] ', '💡': '[TIP] ', '👉': '-> ',
        '⭐': '[*] ', '👥': '[USER] ', '🚪': '[SAIR] ', '🗣️': '[CHAT] '
    }
    for emoji, replacement in emojis.items():
        text = text.replace(emoji, replacement)
    
    # Substituir aspas tipográficas comuns que dão erro no FPDF latin-1
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'", '–': '-', '—': '--', '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    return text.encode('latin-1', 'replace').decode('latin-1')


def parse_markdown_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        print(f"Erro: {md_path} não encontrado!")
        return False
        
    print(f"Lendo Markdown de: {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Cria o PDF
    pdf = PRDPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # --- CAPA / CABEÇALHO DO TÍTULO ---
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 12, 'SVOBODA TELECOMUNICAÇÕES', align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'ECOSSISTEMA DE AUTOMAÇÃO E BUSINESS INTELLIGENCE', align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, 'Documento de Requisitos do Produto (PRD) & Especificação Técnica Completa', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 6, f'Gerado em: {datetime.now().strftime("%d/%m/%Y")} | Versão 3.5 Premium', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(8)
    
    # Linha divisória de título
    pdf.set_draw_color(30, 60, 120)
    pdf.set_line_width(1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Estado do parser
    lines = content.strip().split('\n')
    in_code_block = False
    in_table = False
    table_headers = []
    table_rows = []
    
    # Processa linha por linha
    for i, line in enumerate(lines):
        # Ignorar as primeiras linhas que já serviram como título da capa
        if i < 4 and (line.startswith('#') or line.startswith('###')):
            continue
            
        stripped = line.strip()
        
        # --- BLOCOS DE CÓDIGO / DIAGRAMAS ---
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                pdf.set_font('Helvetica', '', 10)
                pdf.ln(2)
            else:
                in_code_block = True
                pdf.set_font('Courier', '', 8.5)
                pdf.set_text_color(60, 60, 60)
                pdf.set_fill_color(245, 245, 245)
            continue

        if in_code_block:
            # Exibir código com fonte mono e fundo cinza claro
            sanitized_line = sanitize(line)
            # Evita linhas muito compridas
            sanitized_line = sanitized_line[:85]
            pdf.cell(0, 4.5, sanitized_line, fill=True, new_x='LMARGIN', new_y='NEXT')
            continue

        # --- TABELAS ---
        if stripped.startswith('|'):
            if not in_table:
                in_table = True
                table_headers = [c.strip() for c in stripped.split('|')[1:-1]]
                table_rows = []
            else:
                # É divisor de header? (ex: | --- | --- |)
                if '---' in stripped:
                    continue
                # É uma linha de dados
                cols = [c.strip() for c in stripped.split('|')[1:-1]]
                if len(cols) == len(table_headers):
                    table_rows.append(cols)
            continue
        elif in_table:
            # Fim da tabela, renderiza agora no PDF
            in_table = False
            pdf.ln(2)
            
            # Determina larguras de coluna
            num_cols = len(table_headers)
            col_width = 190 / num_cols if num_cols > 0 else 190
            
            # Header
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_fill_color(30, 60, 120)
            pdf.set_text_color(255, 255, 255)
            for h in table_headers:
                pdf.cell(col_width, 8, sanitize(h), border=1, fill=True, align='C')
            pdf.ln(8)
            
            # Linhas de dados
            pdf.set_font('Helvetica', '', 8.5)
            pdf.set_text_color(0, 0, 0)
            for idx, r in enumerate(table_rows):
                fill = idx % 2 == 0
                pdf.set_fill_color(240, 245, 250) if fill else pdf.set_fill_color(255, 255, 255)
                for col in r:
                    pdf.cell(col_width, 7, sanitize(col), border=1, fill=True, align='L')
                pdf.ln(7)
            pdf.ln(4)
            # Reset
            table_headers = []
            table_rows = []

        # --- LINHA VAZIA ---
        if not stripped:
            pdf.ln(2)
            continue

        # --- DIVISOR DO PRODUTO (---) ---
        if stripped == '---':
            pdf.ln(4)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
            continue

        # --- TÍTULO DO PRODUTO (#) ---
        if stripped.startswith('# '):
            pdf.ln(6)
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(30, 60, 120)
            title = sanitize(stripped[2:])
            pdf.cell(0, 12, title, new_x='LMARGIN', new_y='NEXT')
            pdf.ln(2)
            continue

        # --- SUBTÍTULO 1 (##) ---
        if stripped.startswith('## '):
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 13)
            pdf.set_text_color(30, 60, 120)
            title = sanitize(stripped[3:])
            pdf.cell(0, 9, title, new_x='LMARGIN', new_y='NEXT')
            # Linha sutil abaixo de subtítulos maiores
            pdf.set_draw_color(30, 60, 120)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 100, pdf.get_y())
            pdf.ln(3)
            continue

        # --- SUBTÍTULO 2 (###) ---
        if stripped.startswith('### '):
            pdf.ln(3)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(50, 80, 150)
            title = sanitize(stripped[4:])
            pdf.cell(0, 7, title, new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            continue

        # --- ALERTAS OPERACIONAIS (> [!IMPORTANT] etc.) ---
        if stripped.startswith('>'):
            pdf.set_font('Helvetica', 'I', 9.5)
            pdf.set_text_color(180, 80, 0) if 'IMPORTANT' in stripped or 'WARNING' in stripped else pdf.set_text_color(100, 100, 100)
            cleaned_alert = stripped.replace('> [!IMPORTANT]', 'IMPORTANTE:').replace('> [!TIP]', 'DICA:').replace('>', '').strip()
            # Injeta caixa colorida sutil ao fundo
            pdf.set_fill_color(255, 248, 235)
            pdf.multi_cell(0, 5.5, sanitize(cleaned_alert), border=1, fill=True, new_x='LMARGIN', new_y='NEXT')
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            continue

        # --- LISTAS E BULLETS (* ou - ou 1.) ---
        list_match = re.match(r'^(\s*)([\*\-\d\.]+)(\s+)(.*)', line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            bullet_sym = '-' if list_match.group(2) in ('*', '-') else list_match.group(2)
            list_text = list_match.group(4)
            
            # Identação do bullet
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            # Recuo
            pdf.cell(5 + indent_spaces, 6, '')
            pdf.cell(5, 6, bullet_sym)
            
            # Tratamento de negritos em listas
            clean_list_text = list_text.replace('**', '')
            pdf.multi_cell(0, 6, sanitize(clean_list_text), new_x='LMARGIN', new_y='NEXT')
            continue

        # --- CORPO DE TEXTO PADRÃO ---
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(20, 20, 20)
        
        # Substitui negritos para exibição plana limpa no PDF
        clean_line = stripped.replace('**', '')
        pdf.multi_cell(0, 5.5, sanitize(clean_line), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)

    print(f"Salvando PDF em: {pdf_path}...")
    pdf.output(pdf_path)
    print("PDF concluído com sucesso!")
    return True


if __name__ == "__main__":
    PASTA_DASH = r"C:\Users\SVOBODA\Desktop\DASHBOARD"
    README_FILE = os.path.join(PASTA_DASH, "README.md")
    OUT_PDF_DASH = os.path.join(PASTA_DASH, "PRD_Ecossistema_Svoboda.pdf")
    OUT_PDF_DESKTOP = r"C:\Users\SVOBODA\Desktop\PRD_Ecossistema_Svoboda.pdf"
    
    # Gera nas duas localizações solicitadas
    sucesso = parse_markdown_to_pdf(README_FILE, OUT_PDF_DASH)
    if sucesso:
        import shutil
        shutil.copy2(OUT_PDF_DASH, OUT_PDF_DESKTOP)
        print(f"[OK] Cópia criada no Desktop: {OUT_PDF_DESKTOP}")
