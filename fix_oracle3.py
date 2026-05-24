with open("/opt/painel_robo/src/robo_oracle.py", "r", encoding="utf-8") as f:
    content = f.read()

# O bloco que tenta clicar nos nav_links e falha
old_block = '''        if not _clicou_console:
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

new_block = '''        if not _clicou_console:
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

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("/opt/painel_robo/src/robo_oracle.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("OK - Adicionado force click + JavaScript click como fallback")
else:
    print("ERRO - Bloco nao encontrado")
    if "Seletores falharam" in content:
        print("  'Seletores falharam' existe no arquivo")
    if "ERRO] Nao conseguiu" in content:
        print("  'ERRO] Nao conseguiu' existe no arquivo")
