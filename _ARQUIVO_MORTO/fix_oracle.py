import sys

# Lê o arquivo
with open("/opt/painel_robo/src/robo_oracle.py", "r", encoding="utf-8") as f:
    content = f.read()

# O bloco antigo do PASSO 2 (entre os marcadores)
old_passo2 = '''        print("PASSO 2: Clicando em 'Console de Alocacao'...")
        try:
            # Tenta por texto exato
            page.locator('text="Console de Alocação"').first.click(timeout=5000)
            print("  Clicou em Console de Alocacao!")
        except:
            try:
                # Tenta por texto parcial
                page.locator('text=/Console.*Aloca/i').first.click(timeout=3000)
                print("  Clicou em Console de Alocacao (parcial)!")
            except:
                # Tenta pelo icone na barra lateral (4o item na sidebar)
                # No screenshot do usuario, Console de Alocacao e o 4o item com icone
                print("  Tentando clicar pelo icone na sidebar...")
                sidebar_items = page.locator('nav a, nav li, .sidebar a, .sidebar li, [class*="nav"] a, [class*="nav"] li')
                count = sidebar_items.count()
                print(f"  Encontrados {count} itens no menu lateral")
                if count >= 4:
                    sidebar_items.nth(3).click()  # 4o item (0-indexed = 3)
                    print("  Clicou no 4o item do menu!")
                else:
                    # Clica na posicao do "Console de Alocacao" baseado no screenshot
                    # Na sidebar expandida, fica aprox. na posicao y=130
                    page.mouse.click(100, 130)
                    print("  Clicou pela posicao estimada!")'''

new_passo2 = '''        print("PASSO 2: Clicando em 'Console de Alocacao'...")
        _clicou_console = False
        # Estrategia 1: seletor CSS exato (classe do Oracle OFSC)
        for _sel in [
            'a.global-navigation-item--activities',
            '[class*="navigation-item--activities"]',
            'a[title="Console de Alocação"]',
            'a[title*="Console"]',
            'text="Console de Alocação"',
            'text=/Console.*Aloca/i',
        ]:
            try:
                loc = page.locator(_sel).first
                if loc.is_visible(timeout=2000):
                    loc.click(timeout=5000)
                    print(f"  Clicou em Console de Alocacao via: {_sel}")
                    _clicou_console = True
                    break
            except:
                continue

        if not _clicou_console:
            # Fallback: busca todos os links de navegacao global
            print("  Seletores falharam. Buscando links de navegacao...")
            nav_links = page.locator('a.global-navigation-item')
            count = nav_links.count()
            print(f"  Encontrados {count} links de navegacao global")
            for i in range(count):
                try:
                    title = nav_links.nth(i).get_attribute("title", timeout=1000) or ""
                    cls = nav_links.nth(i).get_attribute("class", timeout=1000) or ""
                    print(f"    [{i}] title={title}, class={cls}")
                    if "activities" in cls or "Console" in title or "Aloca" in title:
                        nav_links.nth(i).click(timeout=5000)
                        print(f"  Clicou no item [{i}]!")
                        _clicou_console = True
                        break
                except:
                    continue

        if not _clicou_console:
            print("  [ERRO] Nao conseguiu clicar em Console de Alocacao!")
            screenshot(page, "erro_console_alocacao")'''

if old_passo2 in content:
    content = content.replace(old_passo2, new_passo2)
    with open("/opt/painel_robo/src/robo_oracle.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("OK - PASSO 2 atualizado com sucesso!")
else:
    print("ERRO - Nao encontrou o bloco antigo do PASSO 2")
    # Tenta achar parcial
    if "Clicou pela posicao estimada" in content:
        print("  O texto 'Clicou pela posicao estimada' existe no arquivo")
    if "PASSO 2: Clicando" in content:
        print("  O texto 'PASSO 2: Clicando' existe no arquivo")
