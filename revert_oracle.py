with open("/opt/painel_robo/src/robo_oracle.py", "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# === REVERT 1: Remover o bloco de ESPERA antes do PASSO 1 ===
old_wait = '''        # =============================================
        # ESPERA: Aguardar a pagina Oracle carregar completamente
        # =============================================
        print("AGUARDANDO pagina Oracle carregar...")
        try:
            # Espera ate o header/logo ou a barra de pesquisa aparecer (sinal de que o app carregou)
            page.wait_for_selector(
                'input[placeholder*="Pesquisa"], input[placeholder*="Search"], '
                '.head-burger-icon, [class*="burger"], '
                'a.global-navigation-item, [class*="global-navigation"]',
                state="visible", timeout=30000
            )
            print("  Pagina carregou!")
        except:
            print("  Timeout esperando pagina, tentando continuar...")
            time.sleep(5)  # fallback: espera mais 5s
        
        screenshot(page, "01_pagina_inicial")

        # =============================================
        # PASSO 1: Clicar no botao hamburguer (3 risquinhos)
        # =============================================
        print("PASSO 1: Clicando no botao hamburguer (3 risquinhos)...")'''

new_wait = '''        # =============================================
        # PASSO 1: Clicar no botao hamburguer (3 risquinhos)
        # =============================================
        print("PASSO 1: Clicando no botao hamburguer (3 risquinhos)...")'''

if old_wait in content:
    content = content.replace(old_wait, new_wait)
    changes += 1
    print("REVERT 1 OK - Removido bloco ESPERA")
else:
    print("REVERT 1 SKIP - Bloco ESPERA nao encontrado")

# === REVERT 2: Restaurar sleep apos hamburguer (remover retry) ===
old_after_hamb = '''        # Aguarda a sidebar/navegacao aparecer apos o clique do hamburguer
        time.sleep(3)
        try:
            page.wait_for_selector(
                'a.global-navigation-item, [class*="navigation-item"], '
                'text="Console de Alocação", text="Mapas"',
                state="visible", timeout=10000
            )
            print("  Menu de navegacao apareceu!")
        except:
            print("  Menu nao apareceu, tentando clicar hamburguer de novo...")
            # Tenta clicar o hamburguer uma segunda vez
            try:
                page.mouse.click(25, 25)
                time.sleep(3)
            except:
                pass
        screenshot(page, "02_apos_hamburguer")'''

new_after_hamb = '''        time.sleep(2)
        screenshot(page, "02_apos_hamburguer")'''

if old_after_hamb in content:
    content = content.replace(old_after_hamb, new_after_hamb)
    changes += 1
    print("REVERT 2 OK - Restaurado sleep simples apos hamburguer")
else:
    print("REVERT 2 SKIP - Bloco pos-hamburguer nao encontrado")

# === REVERT 3: Restaurar PASSO 2 original ===
# Primeiro, encontrar o bloco atual do PASSO 2
old_passo2 = '''        print("PASSO 2: Clicando em 'Console de Alocacao'...")
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
                        # Tenta clique normal
                        try:
                            nav_links.nth(i).click(timeout=3000)
                            print(f"  Clicou no item [{i}] (normal)!")
                            _clicou_console = True
                        except:
                            # Tenta force click (ignora overlays)
                            try:
                                nav_links.nth(i).click(force=True, timeout=3000)
                                print(f"  Clicou no item [{i}] (force)!")
                                _clicou_console = True
                            except:
                                pass
                        break
                except:
                    continue

        # Ultimo recurso: clique via JavaScript direto no DOM
        if not _clicou_console:
            print("  Tentando clique via JavaScript...")
            try:
                result = page.evaluate("""() => {
                    // Tenta pelo seletor CSS
                    let el = document.querySelector('a.global-navigation-item--activities');
                    if (!el) {
                        // Tenta por title
                        el = document.querySelector('a[title="Console de Alocação"]');
                    }
                    if (!el) {
                        // Busca por texto
                        const links = document.querySelectorAll('a.global-navigation-item');
                        for (const a of links) {
                            if (a.textContent.includes('Console') || a.title.includes('Console')) {
                                el = a;
                                break;
                            }
                        }
                    }
                    if (el) {
                        el.click();
                        return 'OK: ' + el.title;
                    }
                    return 'ERRO: elemento nao encontrado';
                }""")
                print(f"  JavaScript click: {result}")
                if result.startswith("OK"):
                    _clicou_console = True
            except Exception as ex:
                print(f"  JavaScript click falhou: {ex}")

        if not _clicou_console:
            print("  [ERRO] Nao conseguiu clicar em Console de Alocacao!")
            screenshot(page, "erro_console_alocacao")'''

new_passo2 = '''        print("PASSO 2: Clicando em 'Console de Alocacao'...")
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

if old_passo2 in content:
    content = content.replace(old_passo2, new_passo2)
    changes += 1
    print("REVERT 3 OK - Restaurado PASSO 2 original")
else:
    print("REVERT 3 SKIP - PASSO 2 modificado nao encontrado")

# === Restaurar screenshot antigo antes do PASSO 1 ===
old_comment = '''        # (screenshot movido para apos o wait de carregamento)

        # =============================================
        # PASSO 1:'''

new_comment = '''        screenshot(page, "01_pagina_inicial")

        # =============================================
        # PASSO 1:'''

if old_comment in content:
    content = content.replace(old_comment, new_comment)
    changes += 1
    print("REVERT 4 OK - Restaurado screenshot antes do PASSO 1")
else:
    print("REVERT 4 SKIP")

# Salva
with open("/opt/painel_robo/src/robo_oracle.py", "w", encoding="utf-8") as f:
    f.write(content)
print(f"\nTOTAL: {changes} reverts aplicados")
