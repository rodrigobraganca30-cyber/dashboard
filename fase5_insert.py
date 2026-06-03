import paramiko, os, json

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Criar script SQL inline no servidor e executar
configs = [
    {
        "chave": "btn_status_map",
        "descricao": "Mapeamento de texto de botao para status automatico",
        "valor": {
            "sim, confirmo": "confirmado",
            "preciso reagendar": "reagendado",
            "cancelar": "nao-atendido",
            "agendar": "agendado",
            "ja devolvi": "resolvido",
            "sim, tudo certo": "confirmado",
            "nao, tenho problema": "problema-aberto",
            "quero falar com alguem": "problema-aberto",
            "sim, pode vir": "agendado",
            "nao, preciso reagendar": "reagendado"
        }
    },
    {
        "chave": "keywords_status",
        "descricao": "Palavras-chave para deteccao automatica de status",
        "valor": {
            "nao-atendido": ["nao posso", "impossivel", "ocupado", "nao vou", "cancelar", "cancela", "desmarcar", "nao"],
            "reagendado": ["remarcar", "reagendar", "outro dia", "outra data", "mudar data", "mudar horario", "pode ser amanha", "outra hora", "diferente", "semana que vem"],
            "confirmado": ["sim", "confirmo", "confirmado", "ok", "pode vir", "pode sim", "pode confirmar", "certo", "perfeito", "ta bom", "tudo bem", "estarei", "combinado", "show", "vou estar", "otimo", "beleza", "claro", "com certeza", "positivo"]
        }
    },
    {
        "chave": "flow_config",
        "descricao": "Configuracao do fluxo automatico de mensagens",
        "valor": {"ativo": False, "delay_segundos": 10}
    }
]

# Gerar o SQL
sql_lines = []
for cfg in configs:
    valor_json = json.dumps(cfg["valor"], ensure_ascii=False)
    # Escape single quotes for SQL
    valor_escaped = valor_json.replace("'", "''")
    sql_lines.append(
        f"INSERT INTO configuracoes (chave, valor, descricao) "
        f"VALUES ('{cfg['chave']}', '{valor_escaped}'::jsonb, '{cfg['descricao']}') "
        f"ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = CURRENT_TIMESTAMP;"
    )

full_sql = "\n".join(sql_lines)

# Upload SQL como arquivo
sftp = c.open_sftp()
with sftp.open('/tmp/insert_configs.sql', 'w') as f:
    f.write(full_sql)
sftp.close()

print("Executando SQL...")
i, o, e = c.exec_command('docker exec -i agenda-db psql -U agenda_user -d agenda < /tmp/insert_configs.sql')
print("OUT:", o.read().decode().strip())
print("ERR:", e.read().decode().strip())

# Verificar
print("\nVerificando...")
i, o, e = c.exec_command('docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT chave, descricao, length(valor::text) as tamanho_json FROM configuracoes;"')
print(o.read().decode().strip())

c.close()
