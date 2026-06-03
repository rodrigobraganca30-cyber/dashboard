import os, shutil

base = r'C:\Users\SVOBODA\Desktop\DASHBOARD'
archive = os.path.join(base, '_ARQUIVO_MORTO')
os.makedirs(archive, exist_ok=True)

# Scripts que DEVEM ser mantidos (operacionais atuais)
KEEP = {
    'processar_dados.py',        # Gera o dashboard principal (indicadores)
    'robo_agenda_futura.py',     # Robô de importação da agenda futura
    'deploy_modular.py',         # Deploy modular do backend (novo)
    'deploy_agenda_frontend.py', # Deploy do frontend da agenda
    'migrate.js',                # Migration script Redis -> PG (referência)
}

# Categorias de lixo
ARCHIVE_PATTERNS = [
    'patch_', 'restore_', 'inject_', '_patch', '_inject',
    'post_inject', 'update_post_inject', 'add_templates_to_post_inject',
    'sync_definitivo', 'sync_scripts', 'rodar_gerador',
    'teste_', 'scratch_', 'test_', 'verify_', 'check_',
    'deep_check', 'analise_', 'diagnose_',
    'upload_and_execute', 'upload_and_restart', 'upload_compose',
    'upload_frontend', 'upload_jsons',
    'split_frontend', 'download_frontend',
    'fase5_', 'run_migration',
    'check_redis_api', 'check_network', 'check_serve', 'check_crash',
    'test_e2e', 'test_routes', 'test_nginx', 'test_ip_direct', 'test_config',
    'restaurar_backup', 'rollback', 'revert_oracle',
    'relatorio_sem_retorno', 'ver_logs',
    'fix_post_inject', 'prep_flow',
    'setup_usuarios', '_add_sctbl', '_comp_patch', '_debug',
    '_ifi_patch', '_irr_patch', '_js_patch', '_rm_giga',
    '_read_oracle', '_check_', '_migrate_redis',
    'whatsapp_agenda_gen_DEPRECATED',
]

archived = []
kept = []
for f in os.listdir(base):
    if not f.endswith('.py'):
        continue
    if f in KEEP:
        kept.append(f)
        continue
    
    should_archive = False
    for pattern in ARCHIVE_PATTERNS:
        if pattern in f.lower():
            should_archive = True
            break
    
    if should_archive:
        src = os.path.join(base, f)
        dst = os.path.join(archive, f)
        shutil.move(src, dst)
        archived.append(f)
    else:
        kept.append(f)

print(f"ARQUIVADOS: {len(archived)} scripts movidos para _ARQUIVO_MORTO/")
print(f"MANTIDOS:   {len(kept)} scripts operacionais")
print()
print("=== MANTIDOS ===")
for f in sorted(kept):
    print(f"  + {f}")
print()
print(f"=== ARQUIVADOS ({len(archived)}) ===")
for f in sorted(archived)[:20]:
    print(f"  - {f}")
if len(archived) > 20:
    print(f"  ... e mais {len(archived)-20}")
