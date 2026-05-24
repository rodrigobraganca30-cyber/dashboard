import re

with open("/opt/painel_robo/src/robo_oracle.py", "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ===== FIX 1: Antes do PASSO 1, esperar a pagina carregar de verdade =====
old_passo1_marker = '''        # =============================================
        # PASSO 1: Clicar no botao hamburguer (3 risquinhos)
        # =============================================
        print("PASSO 1: Clicando no botao hamburguer (3 risquinhos)...")'''

new_passo1_marker = '''        # =============================================
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

if old_passo1_marker in content:
    content = content.replace(old_passo1_marker, new_passo1_marker)
    changes += 1
    print("FIX 1 OK - Adicionado wait antes do PASSO 1")
else:
    print("FIX 1 SKIP - Marcador do PASSO 1 nao encontrado")

# ===== FIX 2: No PASSO 1, esperar mais apos o clique do hamburguer =====
old_sleep_after_hamburger = '''        time.sleep(2)
        screenshot(page, "02_apos_hamburguer")

        # =============================================
        # PASSO 2: Clicar em "Console de Alocacao"'''

new_sleep_after_hamburger = '''        # Aguarda a sidebar/navegacao aparecer apos o clique do hamburguer
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
        screenshot(page, "02_apos_hamburguer")

        # =============================================
        # PASSO 2: Clicar em "Console de Alocacao"'''

if old_sleep_after_hamburger in content:
    content = content.replace(old_sleep_after_hamburger, new_sleep_after_hamburger)
    changes += 1
    print("FIX 2 OK - Melhorado wait apos hamburguer")
else:
    print("FIX 2 SKIP - Marcador pos-hamburguer nao encontrado")

# ===== FIX 3: Remover o screenshot duplicado do 01_pagina_inicial (o antigo) =====
# O screenshot antigo fica entre o goto e o PASSO 1, mas agora o novo wait ja tira
old_screenshot = '''        screenshot(page, "01_pagina_inicial")

        # =============================================
        # ESPERA: Aguardar a pagina Oracle carregar completamente'''

new_screenshot = '''        # (screenshot movido para apos o wait de carregamento)

        # =============================================
        # ESPERA: Aguardar a pagina Oracle carregar completamente'''

if old_screenshot in content:
    content = content.replace(old_screenshot, new_screenshot)
    changes += 1
    print("FIX 3 OK - Removido screenshot duplicado")
else:
    print("FIX 3 SKIP - Screenshot antigo nao encontrado ou ja removido")

# Salva
if changes > 0:
    with open("/opt/painel_robo/src/robo_oracle.py", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nTOTAL: {changes} fixes aplicados!")
else:
    print("\nNENHUM fix aplicado - verificar conteudo do arquivo")
