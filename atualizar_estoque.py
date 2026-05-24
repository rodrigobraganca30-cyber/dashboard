"""
atualizar_estoque.py - Atualiza a secao de Estoque no index.html do dashboard.
Roda no servidor Linux apos cada geracao de inventario ou via cron.
Caminho: /docker/dashboard/atualizar_estoque.py
"""
import os
import re
import glob
import shutil

INDEX_HTML = '/docker/dashboard/html/index.html'
INV_DIR_CSV = '/opt/painel_robo/data/csv'
INV_DIR_HTML = '/docker/dashboard/html'


def copiar_inventarios():
    """Copia inventario_*.xlsx de csv/ para html/ (download via Nginx)."""
    copiados = 0
    for xlsx in glob.glob(os.path.join(INV_DIR_CSV, 'inventario_*.xlsx')):
        dest = os.path.join(INV_DIR_HTML, os.path.basename(xlsx))
        if not os.path.exists(dest) or os.path.getmtime(xlsx) > os.path.getmtime(dest):
            shutil.copy2(xlsx, dest)
            print(f"  [ESTOQUE] Copiado {os.path.basename(xlsx)}")
            copiados += 1
    return copiados


def gerar_estoque_html():
    """Lista arquivos inventario_*.xlsx e gera HTML da secao Estoque."""
    inventarios = sorted(
        glob.glob(os.path.join(INV_DIR_HTML, 'inventario_*.xlsx')),
        key=os.path.getmtime, reverse=True
    )
    total = len(inventarios)

    rows_html = ''
    for inv in inventarios:
        nome = os.path.basename(inv)
        m = re.search(r'inventario_(.+)\.xlsx', nome)
        data_label = m.group(1).replace('-', '/') if m else nome
        tamanho_kb = os.path.getsize(inv) / 1024
        if tamanho_kb > 1024:
            tamanho_str = f'{tamanho_kb/1024:.1f} MB'
        else:
            tamanho_str = f'{tamanho_kb:.0f} KB'
        rows_html += f'<tr><td>{data_label}</td><td>{tamanho_str}</td>'
        rows_html += f'<td><a href="{nome}" download class="estoque-btn"><i class="fas fa-download"></i> Baixar</a></td></tr>\n'

    if not rows_html:
        rows_html = '<tr><td colspan="3" style="color:#6b7280;text-align:center;padding:24px;">Nenhum inventário disponível ainda. O robô gera inventários diariamente após o expediente.</td></tr>\n'

    estoque_html = '<div class="page" id="estoque">\n'
    estoque_html += '  <div class="kpi-grid" style="grid-template-columns:1fr; margin-bottom:24px;">\n'
    estoque_html += '    <div class="kpi-card blue" style="display:flex; justify-content:space-between; align-items:center;">\n'
    estoque_html += '      <div>\n'
    estoque_html += '        <div class="kpi-label">Base de Inventário</div>\n'
    estoque_html += f'        <div class="kpi-value blue">{total}</div>\n'
    estoque_html += '        <div class="kpi-sub">relatórios diários salvos no servidor</div>\n'
    estoque_html += '      </div>\n'
    estoque_html += '      <i class="fas fa-boxes" style="font-size:40px; color:rgba(0,229,255,0.2);"></i>\n'
    estoque_html += '    </div>\n'
    estoque_html += '  </div>\n'
    estoque_html += '  <div class="section-title"><i class="fas fa-download" style="color:var(--accent)"></i> Download de Inventários</div>\n'
    estoque_html += '  <div class="chart-card table-scroll" style="max-height:500px;overflow-y:auto;">\n'
    estoque_html += '    <table class="data-table">\n'
    estoque_html += '      <thead><tr><th>Data do Relatório</th><th>Tamanho Estimado</th><th>Ação</th></tr></thead>\n'
    estoque_html += '      <tbody>\n'
    estoque_html += rows_html
    estoque_html += '      </tbody>\n'
    estoque_html += '    </table>\n'
    estoque_html += '  </div>\n'
    estoque_html += '</div>'
    return estoque_html


def atualizar_index():
    """Substitui a secao de estoque no index.html pela versao atualizada."""
    if not os.path.exists(INDEX_HTML):
        print(f"[ERRO] {INDEX_HTML} nao encontrado!")
        return False

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    novo_estoque = gerar_estoque_html()

    # Regex para encontrar a secao de estoque existente (suporta \r\n)
    pattern = r'<div class="page" id="estoque">[\s\S]*?</div>\s*</div>\s*</div>\s*</div>'
    match = re.search(pattern, html)

    if match:
        html = html[:match.start()] + novo_estoque + html[match.end():]
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] Secao de Estoque atualizada no index.html!")
        return True

    # Fallback: tenta encontrar por marcadores mais simples
    start_marker = '<div class="page" id="estoque">'
    end_marker = '</div>\r\n<div class="footer">'
    alt_end_marker = '</div>\n<div class="footer">'
    
    start_pos = html.find(start_marker)
    if start_pos != -1:
        end_pos = html.find(end_marker, start_pos)
        if end_pos == -1:
            end_pos = html.find(alt_end_marker, start_pos)
        if end_pos != -1:
            html = html[:start_pos] + novo_estoque + '\n' + html[end_pos:]
            with open(INDEX_HTML, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[OK] Secao de Estoque atualizada no index.html (fallback)!")
            return True
    
    print("[AVISO] Secao de estoque nao encontrada no index.html")
    return False


if __name__ == '__main__':
    print("=" * 50)
    print(" Atualizando Estoque no Dashboard")
    print("=" * 50)

    copiados = copiar_inventarios()
    print(f"  Inventarios copiados: {copiados}")

    inventarios = glob.glob(os.path.join(INV_DIR_HTML, 'inventario_*.xlsx'))
    print(f"  Total de inventarios disponiveis: {len(inventarios)}")

    ok = atualizar_index()
    if ok:
        print("[SUCESSO] Dashboard atualizado com secao de Estoque!")
    else:
        print("[AVISO] Verifique o index.html manualmente")
