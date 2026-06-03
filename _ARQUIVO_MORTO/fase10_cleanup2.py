import os, shutil

base = r'C:\Users\SVOBODA\Desktop\DASHBOARD'
archive = os.path.join(base, '_ARQUIVO_MORTO')

# Scripts que DEVEM ser mantidos (operacionais atuais)
KEEP = {
    'processar_dados.py',         # Gera dashboard HTML (indicadores)
    'robo_agenda_futura.py',      # Robo de importacao da agenda
    'deploy_modular.py',          # Deploy modular do backend
    'deploy_agenda_frontend.py',  # Deploy do frontend da agenda
    'deploy_to_container.py',     # Deploy generico ao container
    'gerar_dashboard.py',         # Gerador de dashboard (se usado)
    'backup_completo.py',         # Backup completo
    'backup_vps.py',              # Backup do VPS
    'fase10_cleanup.py',          # Este script
    'importar_blacklist_inicial.py', # Import de blacklist
    'atualizar_estoque.py',       # Atualiza estoque
}

# Segunda rodada - mais padroes obsoletos
ARCHIVE_PATTERNS_2 = [
    'fix_', 'find_', 'debug_', 'injetar_', 'inject_',
    'deploy_fase2', 'deploy_unificacao', 'deploy_frontend',
    'deploy_processar', 'deploy_agenda_futura',
    'fase2', 'fase3_congelar',
    'compile_script', 'get_script', 'get_crash',
    'hex_scan', 'dom_check', 'deep_scan', 'inspecionar_',
    'gerar_dashboard_v2', 'gerar_pdf', 'gerar_prd',
    'indicadores_', 'contar_status',
    'auth_api', 'flow_api', 'apply_flow', 'apply_limits',
    'extract_flow', 'move_btncfg', 'add_mapping_modal',
    'enviar_template', 'enviar_visita', 'obter_falhas',
    'buscar_erro', 'list_backups', 'find_backup',
    'install_pg', 'install_psycopg',
    'make_inv_dynamic', 'download_compose',
    'backup_completo_fluxo', 'backup_local',
    'fazer_backup', 'find_12h', 
    'whatsapp_agenda_gen_DEPRECATED',
    'verificar_backend',
]

archived2 = []
for f in os.listdir(base):
    if not f.endswith('.py'):
        continue
    if f in KEEP:
        continue
    
    for pattern in ARCHIVE_PATTERNS_2:
        if pattern in f.lower():
            src = os.path.join(base, f)
            dst = os.path.join(archive, f)
            if os.path.exists(src):
                shutil.move(src, dst)
                archived2.append(f)
            break

# Listar o que sobrou
remaining = [f for f in os.listdir(base) if f.endswith('.py')]

print(f"ARQUIVADOS (2a rodada): {len(archived2)} scripts")
print(f"RESTANTES: {len(remaining)} scripts")
print()
print("=== RESTANTES ===")
for f in sorted(remaining):
    print(f"  {f}")
