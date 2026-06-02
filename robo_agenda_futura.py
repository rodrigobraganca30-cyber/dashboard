"""
robo_agenda_futura.py
=====================
Robô independente que navega no Oracle OFS dia a dia (D+1 até D+30),
exporta o CSV de cada dia e consolida tudo em AGENDA_FUTURA.xlsx.

Execução: todos os dias às 05:00 AM via cron.
Não interfere no robo_oracle.py (TV) de nenhuma forma.
"""
import os
import sys
import glob
import csv
import shutil
import time
import json
import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

# ── Importa configurações do projeto ────────────────────────────────────────
from config import (
    PROJECT_ROOT, DATA_DIR, CSV_DIR, AUTH_DIR, DEBUG_DIR,
    CSV_CDP, STATE_FILE, CRED_FILE, LOG_FILE,
    ORACLE_USUARIO, ORACLE_SENHA, TOTP_SECRET,
    IS_LINUX,
)

# Fix encoding para rodar em background
if sys.stdout is None or not hasattr(sys.stdout, 'reconfigure'):
    _log_af = open(str(PROJECT_ROOT / "src" / "log_agenda_futura.txt"), 'a',
                   encoding='utf-8', errors='replace', buffering=1)
    sys.stdout = _log_af
    sys.stderr = _log_af
else:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ── Pastas ──────────────────────────────────────────────────────────────────
RAW_DIR   = DATA_DIR / "agenda_futura_raw"   # CSVs individuais por dia
XLSX_OUT  = CSV_DIR  / "AGENDA_FUTURA.xlsx"  # Planilha consolidada
STATE_AF  = AUTH_DIR / "state_agenda_futura.json"  # Sessão separada (não conflita com TV)

# Colunas administrativas para ignorar
TIPOS_ADMIN = [
    'almoço', 'almoco', 'inventario', 'inventário', 'treinamento',
    'pausa', 'reunião', 'reuniao', 'abastecimento', 'checklist', 'descanso'
]

def sep(msg):
    print(f"\n{'='*56}\n {msg}\n{'='*56}")

def screenshot(page, name):
    path = str(DEBUG_DIR / f"af_{name}.png")
    try:
        page.screenshot(path=path)
        print(f"  [DBG] Screenshot: af_{name}.png")
    except Exception:
        pass

# ── Autenticação completa (reutiliza o mesmo fluxo SSO do robo_oracle) ──────
def fazer_login(page):
    """
    Retorna True se logou com sucesso ou já estava logado.
    Usa exatamente o mesmo fluxo SSO + MFA do robo_oracle.py.
    """
    url_ofsc = "https://alloha.fs.ocs.oraclecloud.com/"
    print("  Acessando Oracle OFSC...")
    page.goto(url_ofsc, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    screenshot(page, "login_01_inicial")

    # Detecta se precisa logar
    na_login = False
    try:
        if (page.locator('text="Conectar"').count() > 0 or
                page.locator('text="Entrar com SSO"').count() > 0 or
                page.locator('input[type="password"]').count() > 0 or
                page.locator('text="Nome de Usuário"').count() > 0 or
                page.locator('text="Bem-vindo a alloha"').count() > 0 or
                page.locator('text="Pick an account"').count() > 0 or
                page.locator('text="Escolher uma conta"').count() > 0 or
                page.locator('text="Escolha uma conta"').count() > 0 or
                'login.microsoftonline.com' in page.url):
            na_login = True
    except Exception:
        pass

    if not na_login:
        print("  Sessão ainda ativa, pulando login.")
        return True

    print("  Sessão expirada. Fazendo auto-login...")
    try:
        if ORACLE_USUARIO and ORACLE_SENHA:
            usuario, senha = ORACLE_USUARIO, ORACLE_SENHA
        else:
            with open(str(CRED_FILE), 'r', encoding='utf-8') as cf:
                creds = json.load(cf)
            usuario, senha = creds['usuario'], creds['senha']
    except Exception as ex:
        print(f"  [ERRO] Credenciais não encontradas: {ex}")
        return False

    # ── PASSO 1: Tela inicial Oracle — clica em "Entrar com SSO" ────────────
    try:
        btn_sso = page.locator('button:has-text("Entrar com SSO"), text="Entrar com SSO"').first
        if btn_sso.count() > 0 and btn_sso.is_visible():
            btn_sso.click(timeout=5000)
            print("  [ORACLE] Clicou em 'Entrar com SSO'")
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(3)
    except Exception:
        # Fallback: clica no botão por coordenada
        page.mouse.click(683, 527)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
    screenshot(page, "login_02_apos_sso_btn")

    # ── PASSO 2: Tela intermediária SSO Oracle ────────────────────────────────
    # "Preencha seu nome de usuário para continuar com a autenticação SSO"
    for _ in range(3):
        try:
            if (page.locator('text="Continuar com SSO"').count() > 0 or
                    page.locator('text="continuar com a autenticação SSO"').count() > 0):
                print("  [ORACLE-SSO] Tela intermediária detectada. Preenchendo e-mail...")
                # Usa o seletor do campo de nome de usuário
                campo_usuario = page.locator('input[name="username"], input[placeholder*="suário"], input[placeholder*="sario"], input[type="text"]').first
                if campo_usuario.count() > 0 and campo_usuario.is_visible():
                    campo_usuario.click(timeout=3000)
                    campo_usuario.fill('')
                    page.keyboard.type(usuario, delay=30)
                    print(f"  [ORACLE-SSO] E-mail digitado via seletor: {usuario}")
                else:
                    # Fallback por coordenada
                    page.mouse.click(683, 300); time.sleep(0.4)
                    page.keyboard.press("Control+a"); page.keyboard.press("Backspace")
                    page.keyboard.type(usuario, delay=30)
                    print(f"  [ORACLE-SSO] E-mail digitado via coordenada: {usuario}")
                time.sleep(0.5)

                # Clica em "Continuar com SSO"
                try:
                    btn_continuar = page.locator('button:has-text("Continuar com SSO"), input:has-text("Continuar")').first
                    if btn_continuar.count() > 0 and btn_continuar.is_visible():
                        btn_continuar.click(timeout=5000)
                        print("  [ORACLE-SSO] Clicou em 'Continuar com SSO' via seletor")
                    else:
                        page.mouse.click(638, 359)
                        print("  [ORACLE-SSO] Clicou em 'Continuar com SSO' via coordenada")
                except Exception:
                    page.keyboard.press("Enter")
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                break
        except Exception:
            time.sleep(2)

    # ── PASSO 3: "Pick an account" Microsoft ─────────────────────────────────
    for _ in range(3):
        try:
            na_pick = (page.locator('text="Pick an account"').count() > 0 or
                       page.locator('text="Escolher uma conta"').count() > 0 or
                       page.locator('text="Escolha uma conta"').count() > 0 or
                       page.locator('text="Use another account"').count() > 0 or
                       page.locator('text="Usar outra conta"').count() > 0)
            if na_pick:
                print("  [MS] Tela 'Pick an account' detectada! Selecionando conta...")
                clicou = False

                # Tenta clicar no item que contém o e-mail do usuário (estrutura: div com data-test-id ou li clicável)
                for sel in [
                    f'[data-test-id*="tile"] [title*="{usuario}"]',
                    f'[data-test-id*="tile"]:has-text("{usuario}")',
                    f'li:has-text("{usuario}")',
                    f'div.table div:has-text("{usuario}")',
                    f'small:has-text("{usuario}")',
                    f'span:has-text("{usuario}")',
                ]:
                    try:
                        el = page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.click(timeout=3000)
                            clicou = True
                            print(f"  [MS] Clicou na conta via: {sel}")
                            break
                    except Exception:
                        continue

                if not clicou:
                    # Fallback: clica na primeira conta listada (y=360)
                    print("  [MS] Usando coordenada para clicar na conta (683, 360)")
                    page.mouse.click(683, 360)

                time.sleep(3)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                time.sleep(3)
                break
        except Exception:
            time.sleep(2)

    # ── PASSO 4: Tela Microsoft — senha ──────────────────────────────────────
    try:
        # Campo de e-mail (caso apareça antes da senha)
        campo_em = page.locator('input[name="loginfmt"]')
        if campo_em.count() > 0 and campo_em.first.is_visible():
            print("  [MS] Campo e-mail detectado. Digitando...")
            campo_em.first.click(timeout=3000); time.sleep(0.3)
            campo_em.first.fill(usuario)
            page.keyboard.press("Enter"); time.sleep(3)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            time.sleep(2)
    except Exception:
        pass

    try:
        if ('login.microsoftonline' in page.url or
                page.locator('text="Enter password"').count() > 0 or
                page.locator('input[type="password"]').count() > 0):
            print("  [MS] Tela de senha detectada. Digitando senha...")
            try:
                campo_pw = page.locator('input[name="passwd"], input[type="password"]').first
                if campo_pw.count() > 0 and campo_pw.is_visible():
                    campo_pw.click(timeout=3000)
                    campo_pw.fill('')
            except Exception:
                pass
            page.keyboard.type(senha, delay=30); time.sleep(0.8)
            try:
                page.locator(
                    'input[type="submit"]:visible, button[type="submit"]:visible'
                ).first.click(timeout=3000)
            except Exception:
                page.keyboard.press("Enter")
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            time.sleep(5)
            screenshot(page, "login_03_apos_senha")
    except Exception:
        pass

    # ── PASSO 5: MFA (TOTP) ──────────────────────────────────────────────────
    try:
        mfa = (page.locator('input[name="otc"]').count() > 0 or
               page.locator('text="Inserir código"').count() > 0 or
               page.locator('text="Enter code"').count() > 0 or
               page.locator('#signInAnotherWay').count() > 0)
        if mfa:
            # Tenta trocar para código TOTP se necessário
            try:
                if page.locator('#signInAnotherWay').count() > 0:
                    page.locator('#signInAnotherWay').first.click(timeout=5000); time.sleep(2)
                page.locator(
                    'div[data-value="PhoneAppOTP"], div[data-value="VerificationCode"]'
                ).first.click(timeout=5000); time.sleep(2)
            except Exception:
                pass

            campo_otc = page.locator(
                'input[name="otc"], input[type="tel"], #idTxtBx_SAOTCC_OTC'
            ).first
            if campo_otc.count() > 0 and campo_otc.is_visible():
                import pyotp
                codigo = pyotp.TOTP(TOTP_SECRET).now()
                campo_otc.click(timeout=3000); time.sleep(0.3)
                page.keyboard.type(codigo, delay=30); time.sleep(0.8)
                try:
                    page.locator(
                        'input[type="submit"], button[type="submit"], #idSubmit_SAOTCC_Continue'
                    ).first.click(timeout=5000)
                except Exception:
                    page.keyboard.press("Enter")
                page.wait_for_load_state("networkidle", timeout=30000); time.sleep(5)
    except Exception:
        pass

    # ── PASSO 6: "Continuar conectado?" ──────────────────────────────────────
    try:
        if (page.locator('text="Stay signed in?"').count() > 0 or
                page.locator('text="Permanecer conectado?"').count() > 0):
            try:
                chk = page.locator('input[name="DontShowAgain"]').first
                if chk.count() > 0:
                    chk.check()
            except Exception:
                pass
            try:
                page.locator(
                    'input[value="Yes"], input[value="Sim"], #idSIButton9'
                ).first.click()
            except Exception:
                page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle", timeout=30000); time.sleep(5)
    except Exception:
        pass

    screenshot(page, "login_04_final")

    # ── Verifica resultado ────────────────────────────────────────────────────
    ainda_login = False
    try:
        url_atual = page.url
        if 'microsoftonline' in url_atual or 'login.oracle' in url_atual:
            ainda_login = True
        elif page.locator('text="Enter password"').count() > 0:
            ainda_login = True
        elif page.locator('text="Pick an account"').count() > 0:
            ainda_login = True
        elif (page.locator('text="Conectar"').count() > 0 and
              page.locator('input[type="password"]').count() > 0):
            ainda_login = True
    except Exception:
        pass

    if ainda_login:
        print("  [ERRO] Login falhou!")
        return False
    print("  Login realizado com sucesso!")
    return True

# ── Navega para o Console de Alocação ────────────────────────────────────────
def ir_para_console(page):
    """Clica no hamburguer e depois em Console de Alocação."""
    # Hamburguer
    try:
        page.locator(
            'button.head-burger-icon, .ofsc-head-burger, [class*="burger"]'
        ).first.click(timeout=3000)
    except Exception:
        try:
            page.locator('[aria-label="Menu"], [aria-label="menu"]').first.click(timeout=2000)
        except Exception:
            page.mouse.click(25, 25)
    time.sleep(2)

    # Console de Alocação
    try:
        page.locator('text="Console de Alocação"').first.click(timeout=5000)
        print("  Clicou em Console de Alocação!")
    except Exception:
        try:
            page.locator('text=/Console.*Aloca/i').first.click(timeout=3000)
        except Exception:
            page.mouse.click(100, 130)
    time.sleep(4)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass

# ── Navega para uma data alvo (YYYY-MM-DD) clicando seta > ──────────────────
def navegar_para_data(page, data_alvo: datetime.date, max_cliques=50) -> bool:
    """
    A partir da data atual no console, avança clicando '>' até atingir data_alvo.
    Retorna True se conseguiu, False se não achou em max_cliques tentativas.
    """
    hoje = datetime.date.today()
    dias_para_frente = (data_alvo - hoje).days  # D+1 = 1, D+2 = 2, etc.

    if dias_para_frente < 0:
        print(f"  [AVISO] Data {data_alvo} é passada, pulando.")
        return False

    print(f"  Navegando para {data_alvo.strftime('%d/%m/%Y')} (+{dias_para_frente} dias)...")

    # Verifica data atual na tela
    dia_alvo_str = str(data_alvo.day)  # "29", "1", etc.

    for tentativa in range(max_cliques):
        try:
            # Lê o elemento de data (ex: "Sexta-feira, Maio 29º, 2026" ou "Sábado, Maio 30º, 2026")
            # Usa regex com ano para funcionar com TODOS os dias (inclusive Sábado/Domingo)
            data_elem = page.locator('text=/.*202[0-9]/').first
            data_text = data_elem.inner_text(timeout=3000)

            # Verifica se já está na data certa
            # Testa "29º", "29," ou " 29 "
            achou = (
                f" {dia_alvo_str}º" in data_text or
                f" {dia_alvo_str}," in data_text or
                f" {dia_alvo_str} " in data_text or
                data_text.strip().startswith(f"{dia_alvo_str}")
            )
            if achou:
                # Confirma que o mês também bate (evita ambiguidade dia 1, 2...)
                meses_pt = {
                    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                }
                mes_pt = meses_pt.get(data_alvo.month, '')
                if mes_pt and mes_pt in data_text.lower():
                    print(f"  ✅ Data encontrada: {data_text.strip()}")
                    return True
                elif not mes_pt:
                    print(f"  ✅ Data encontrada: {data_text.strip()}")
                    return True

            # Clica na seta >
            box = data_elem.bounding_box()
            if box:
                page.mouse.click(
                    box['x'] + box['width'] + 25,
                    box['y'] + box['height'] / 2
                )
            time.sleep(1.5)
        except Exception as ex:
            print(f"  [AVISO] Erro ao navegar: {ex}")
            time.sleep(2)

    print(f"  [ERRO] Não conseguiu navegar até {data_alvo} em {max_cliques} tentativas.")
    return False

# ── Navega de volta para Hoje (para começar próximo dia) ────────────────────
def voltar_para_hoje(page, max_voltas=35):
    """Clica na seta < até chegar em Hoje."""
    hoje = datetime.date.today()
    dia_hoje = str(hoje.day)
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    mes_hoje_pt = meses_pt.get(hoje.month, '')

    for _ in range(max_voltas):
        try:
            data_elem = page.locator('text=/.*202[0-9]/').first
            data_text = data_elem.inner_text(timeout=3000)
            if (f" {dia_hoje}º" in data_text or f" {dia_hoje}," in data_text or
                    f" {dia_hoje} " in data_text):
                if mes_hoje_pt in data_text.lower():
                    print(f"  Voltou para hoje: {data_text.strip()}")
                    return True
            box = data_elem.bounding_box()
            if box:
                page.mouse.click(box['x'] - 25, box['y'] + box['height'] / 2)
            time.sleep(1.2)
        except Exception:
            time.sleep(2)
    return False

# ── Abre filtro "Exibir", marca hierárquico e Aplica ────────────────────────
def aplicar_filtro_exibir(page):
    """Garante que o filtro 'Aplicar de forma hierárquica' está marcado."""
    try:
        page.locator('text="Exibir"').first.click(timeout=5000)
    except Exception:
        page.mouse.click(990, 104)
    time.sleep(2)

    try:
        caixinha = page.locator(
            'label:has-text("Aplicar de forma") >> xpath=..'
        ).locator('input[type="checkbox"]').first
        caixinha.check(force=True, timeout=5000)
    except Exception:
        page.mouse.click(545, 355)
    time.sleep(0.8)

    try:
        page.get_by_role("button", name="Aplicar", exact=True).first.click()
    except Exception:
        page.mouse.click(695, 410)
    print("  Filtro 'Exibir' aplicado.")
    time.sleep(20)
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    time.sleep(10)

# ── Exporta o CSV do dia ─────────────────────────────────────────────────────
def exportar_csv(page, data_alvo: datetime.date, raw_dir: Path) -> str | None:
    """
    Abre menu Ações > Exportar, aguarda download e salva em raw_dir/YYYY-MM-DD.csv.
    Retorna o path do arquivo salvo ou None se falhou.
    """
    # Clica em Ações
    achou_acoes = False
    try:
        btn_acoes = page.locator(
            'button:has-text("Ações"), [title="Ações"], text="Ações"'
        ).first
        btn_acoes.wait_for(state="visible", timeout=3000)
        btn_acoes.click(force=True, timeout=3000)
        achou_acoes = True
    except Exception:
        try:
            btn_ap = page.get_by_role("button", name="Aplicar", exact=True).first
            box = btn_ap.bounding_box()
            if box:
                page.mouse.click(box['x'] + 150, box['y'] + box['height'] / 2)
                achou_acoes = True
        except Exception:
            pass

    if not achou_acoes:
        page.mouse.click(1090, 104)
    time.sleep(3)

    # Clica em Exportar
    try:
        export_btn = None
        try:
            b = page.locator('text="Exportar" >> visible=true').first
            b.wait_for(state="visible", timeout=4000)
            export_btn = b
        except Exception:
            try:
                b = page.locator(
                    '[title="Exportar"]:visible, a:has-text("Exportar"):visible'
                ).first
                b.wait_for(state="visible", timeout=4000)
                export_btn = b
            except Exception:
                pass

        nome_arquivo = data_alvo.strftime("%Y-%m-%d")
        destino = raw_dir / f"{nome_arquivo}.csv"

        with page.expect_download(timeout=30000) as dl_info:
            if export_btn:
                export_btn.click(force=True, timeout=5000)
            else:
                page.mouse.click(1090, 200)

        download = dl_info.value
        tmp = download.path()
        shutil.copy(tmp, str(destino))
        print(f"  ✅ CSV salvo: {nome_arquivo}.csv")
        return str(destino)

    except Exception as ex:
        print(f"  [ERRO] Falha ao exportar {data_alvo}: {ex}")
        screenshot(page, f"erro_export_{data_alvo}")
        return None

# ── Consolida todos os CSVs em AGENDA_FUTURA.xlsx ───────────────────────────
def consolidar(raw_dir: Path, xlsx_out: Path):
    """Lê todos os CSVs de raw_dir e grava AGENDA_FUTURA.xlsx."""
    try:
        import openpyxl
    except ImportError:
        print("[ERRO] openpyxl não disponível — instale com: pip install openpyxl")
        return

    sep("CONSOLIDAÇÃO → AGENDA_FUTURA.xlsx")

    csvs = sorted(glob.glob(str(raw_dir / "*.csv")))
    if not csvs:
        print("  Nenhum CSV encontrado para consolidar.")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AGENDA_FUTURA"

    # Header padrão
    HEADER = [
        'Data_Origem', 'Recurso', 'Data', 'Status da Atividade', 'Nome',
        'Endereço', 'Cidade', 'Estado', 'CEP/Código Postal', 'Telefone',
        'Telefone Celular', 'E-mail', 'Intervalo de Tempo', 'Janela de Serviço',
        'Janela de Serviço_1', 'Data Abertura Chamado', 'Início', 'Fim',
        'Início - Fim', 'Início do SLA', 'Fim do SLA', 'Duração',
        'Tempo de Deslocamento', 'Tipo de Atividade', 'Tipo de Atividade_2',
        'Ordem de Serviço', 'Número do Cliente', 'Habilidade de Trabalho',
        'Área de Trabalho', 'Chave Workzone', 'Posição na Rota',
        'Observações gerais', 'Observações', 'Atividade de Mídia Social',
        'Atividade de NPS', 'Atividade de Ouvidoria', 'Atividade de Origem',
        'Atividade de retenção', 'Motivo de Encerramento das atividades',
        'ID da Ordem de Serviço'
    ]
    ws.append(HEADER)

    total_inseridas = 0
    total_ignoradas = 0
    datas_processadas = []

    for csv_path in csvs:
        data_str = os.path.basename(csv_path).replace('.csv', '')  # "2026-06-01"
        try:
            data_dt = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
        except Exception:
            data_dt = None

        linhas_csv = []
        for enc in ('utf-8-sig', 'latin-1'):
            try:
                with open(csv_path, 'r', encoding=enc, errors='replace') as f:
                    reader = csv.reader(f)
                    cabecalho = next(reader, None)
                    linhas_csv = list(reader)
                break
            except UnicodeDecodeError:
                continue

        for row in linhas_csv:
            if len(row) < 3:
                total_ignoradas += 1
                continue

            status = row[2].strip().lower() if len(row) > 2 else ''
            tipo_at2 = row[24].strip().lower() if len(row) > 24 else ''

            # Ignora cancelados e atividades administrativas
            if 'cancelad' in status:
                total_ignoradas += 1
                continue
            if any(adm in tipo_at2 for adm in TIPOS_ADMIN):
                total_ignoradas += 1
                continue

            nova_linha = [data_str] + list(row)
            # Normaliza campo Data (índice 3 = original col 2 = Data)
            if len(nova_linha) > 3 and nova_linha[3]:
                _ds = str(nova_linha[3]).strip()
                for _fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
                    try:
                        nova_linha[3] = datetime.datetime.strptime(_ds[:10], _fmt)
                        break
                    except ValueError:
                        continue

            # Garante 40 colunas (1 Data_Origem + 39 do CSV)
            while len(nova_linha) < 40:
                nova_linha.append('')
            ws.append(nova_linha[:40])
            total_inseridas += 1

        if data_dt:
            datas_processadas.append(data_str)

    wb.save(str(xlsx_out))
    wb.close()

    print(f"\n  ✅ Consolidação concluída!")
    print(f"     CSVs processados : {len(csvs)}")
    print(f"     Linhas inseridas : {total_inseridas}")
    print(f"     Linhas ignoradas : {total_ignoradas}")
    print(f"     Período          : {datas_processadas[0] if datas_processadas else '-'}"
          f" → {datas_processadas[-1] if datas_processadas else '-'}")
    print(f"     Arquivo          : {xlsx_out}")

    # Copia para o Nginx (Linux) para ser baixável pelo dashboard
    if IS_LINUX:
        nginx_dest = "/docker/dashboard/html/AGENDA_FUTURA.xlsx"
        try:
            shutil.copy2(str(xlsx_out), nginx_dest)
            print(f"  ✅ Copiado para Nginx: {nginx_dest}")
        except Exception as ex:
            print(f"  [AVISO] Não copiou para Nginx: {ex}")

# ── Main: loop de D+1 até D+30 ───────────────────────────────────────────────
def main():
    sep("ROBÔ AGENDA FUTURA — INÍCIO")
    agora = datetime.datetime.now()
    print(f"  Data/hora: {agora.strftime('%d/%m/%Y %H:%M:%S')}")

    # Cria pastas necessárias
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Limpa CSVs antigos (reprocessa tudo a cada execução para garantir dados frescos)
    for old_csv in glob.glob(str(RAW_DIR / "*.csv")):
        try:
            os.remove(old_csv)
        except Exception:
            pass
    print(f"  Pasta raw limpa: {RAW_DIR}")

    hoje = datetime.date.today()
    datas_alvo = [hoje + datetime.timedelta(days=d) for d in range(1, 31)]  # D+1 a D+30

    csvs_salvos = []
    filtro_aplicado = False  # Aplicar o filtro Exibir apenas uma vez por sessão

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context_args = {"viewport": {"width": 1366, "height": 768}}
        # Usa sessão separada para não conflitar com o robô da TV
        if os.path.exists(str(STATE_AF)):
            try:
                context_args["storage_state"] = str(STATE_AF)
                print(f"  Usando sessão salva: {STATE_AF.name}")
            except Exception:
                pass

        context = browser.new_context(**context_args)
        page = context.new_page()

        # Login
        if not fazer_login(page):
            print("[ERRO CRÍTICO] Login falhou. Abortando.")
            browser.close()
            return

        # Salva nova sessão
        try:
            context.storage_state(path=str(STATE_AF))
            print(f"  Sessão salva em {STATE_AF.name}")
        except Exception:
            pass

        # Vai para Console de Alocação
        ir_para_console(page)
        screenshot(page, "console_alocacao")

        # Aplica filtro Exibir (só uma vez — permanece para todos os dias)
        aplicar_filtro_exibir(page)
        filtro_aplicado = True
        screenshot(page, "filtro_aplicado")

        # Volta para hoje (ponto de partida) e depois avança dia a dia
        print("\n  Voltando para Hoje como ponto de partida...")
        voltar_para_hoje(page)

        for i, data_alvo in enumerate(datas_alvo):
            sep(f"DIA {i+1}/30 → {data_alvo.strftime('%d/%m/%Y (%A)')}")

            # Navega até a data desejada
            if not navegar_para_data(page, data_alvo):
                print(f"  Pulando {data_alvo} — não foi possível navegar.")
                continue

            # Aguarda dados carregarem (o Oracle pode demorar)
            print("  Aguardando dados carregarem...")
            time.sleep(15)
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            time.sleep(8)

            screenshot(page, f"dia_{i+1:02d}_{data_alvo.strftime('%Y%m%d')}")

            # Verifica se sessão ainda está ativa
            if ('microsoftonline' in page.url or
                    'login.oracle' in page.url or
                    'Entrar' in page.title()):
                print("  [AVISO] Sessão expirou no meio! Re-logando...")
                if not fazer_login(page):
                    print("  [ERRO] Re-login falhou, abortando.")
                    break
                ir_para_console(page)
                aplicar_filtro_exibir(page)
                navegar_para_data(page, data_alvo)
                time.sleep(15)
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
                time.sleep(8)

            # Exporta CSV do dia
            csv_path = exportar_csv(page, data_alvo, RAW_DIR)
            if csv_path:
                csvs_salvos.append(csv_path)

            # Pequena pausa entre dias para não sobrecarregar
            time.sleep(5)

        browser.close()

    # Salva sessão final
    print(f"\n  CSVs baixados: {len(csvs_salvos)} de {len(datas_alvo)}")

    # Consolida em XLSX
    consolidar(RAW_DIR, XLSX_OUT)


    # Atualiza SOMENTE a aba Agenda Futura no dashboard (injeção cirúrgica)
    if IS_LINUX:
        import subprocess
        dash_dir = "/docker/dashboard"

        # Garante que os dados estejam acessíveis
        try:
            # Symlink AGENDA_FUTURA
            af_link = f"{dash_dir}/AGENDA_FUTURA.xlsx"
            af_src = f"{dash_dir}/html/AGENDA_FUTURA.xlsx"
            if os.path.exists(af_src) and not os.path.exists(af_link):
                os.symlink(af_src, af_link)
        except Exception as ex:
            print(f"  [AVISO] Erro ao preparar symlink: {ex}")

        # Roda o injetor cirúrgico (NÃO regenera o dashboard inteiro)
        script_injetor = f"{dash_dir}/injetar_agenda_futura.py"
        if os.path.exists(script_injetor):
            print("\n  [DASHBOARD] Injetando aba Agenda Futura...")
            try:
                res = subprocess.run(
                    [sys.executable, script_injetor],
                    capture_output=True, text=True, timeout=120,
                    cwd=dash_dir
                )
                if res.returncode == 0:
                    print("  ✅ Aba Agenda Futura atualizada!")
                    if res.stdout:
                        for line in res.stdout.strip().split('\n')[-5:]:
                            print(f"     {line}")
                else:
                    print(f"  [AVISO] Injetor retornou erro: {res.stderr[:300]}")
            except Exception as ex:
                print(f"  [AVISO] Não injetou agenda futura: {ex}")
        else:
            print(f"  [AVISO] Injetor não encontrado: {script_injetor}")

    sep("ROBÔ AGENDA FUTURA — CONCLUÍDO")


if __name__ == "__main__":
    main()
