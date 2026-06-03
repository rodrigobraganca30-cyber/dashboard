import paramiko, os, json

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Criar tabela de configurações
print("1. Criando tabela 'configuracoes'...")
sql_create = """
CREATE TABLE IF NOT EXISTS configuracoes (
    chave VARCHAR(100) PRIMARY KEY,
    valor JSONB NOT NULL,
    descricao TEXT,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""
i, o, e = c.exec_command(f'docker exec agenda-db psql -U agenda_user -d agenda -c "{sql_create}"')
print(o.read().decode().strip())
print(e.read().decode().strip())

# 2. Inserir BTN_STATUS_MAP
print("\n2. Inserindo BTN_STATUS_MAP...")
btn_map = {
    "sim, confirmo": "confirmado",
    "preciso reagendar": "reagendado",
    "cancelar": "nao-atendido",
    "agendar": "agendado",
    "ja devolvi": "resolvido",
    "sim, tudo certo": "confirmado",
    "nao, tenho problema": "problema-aberto",
    "quero falar com alguem": "problema-aberto",
    "sim, pode vir": "agendado",
    "não, preciso reagendar": "reagendado",
    "nao, preciso reagendar": "reagendado"
}
btn_json = json.dumps(btn_map).replace("'", "''")
sql_btn = f"INSERT INTO configuracoes (chave, valor, descricao) VALUES ('btn_status_map', '{btn_json}'::jsonb, 'Mapeamento de texto de botão para status automático') ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = CURRENT_TIMESTAMP;"
i, o, e = c.exec_command(f"docker exec agenda-db psql -U agenda_user -d agenda -c \"{sql_btn}\"")
print(o.read().decode().strip())

# 3. Inserir KEYWORDS
print("\n3. Inserindo KEYWORDS...")
keywords = {
    "nao-atendido": ["não posso", "nao posso", "impossível", "impossivel", "ocupado", "não vou", "nao vou", "cancelar", "cancela", "desmarcar", "não", "nao"],
    "reagendado": ["remarcar", "reagendar", "outro dia", "outra data", "mudar data", "mudar horário", "mudar horario", "pode ser amanhã", "pode ser amanha", "outra hora", "diferente", "semana que vem"],
    "confirmado": ["sim", "confirmo", "confirmado", "ok", "pode vir", "pode sim", "pode confirmar", "certo", "perfeito", "tá bom", "ta bom", "tudo bem", "estarei", "estarei lá", "estarei la", "combinado", "show", "vou estar", "ótimo", "otimo", "beleza", "claro", "com certeza", "positivo"]
}
kw_json = json.dumps(keywords).replace("'", "''")
sql_kw = f"INSERT INTO configuracoes (chave, valor, descricao) VALUES ('keywords_status', '{kw_json}'::jsonb, 'Palavras-chave para detecção automática de status nas mensagens') ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = CURRENT_TIMESTAMP;"
i, o, e = c.exec_command(f"docker exec agenda-db psql -U agenda_user -d agenda -c \"{sql_kw}\"")
print(o.read().decode().strip())

# 4. Inserir config de flow
print("\n4. Inserindo flow_config...")
flow_cfg = {"ativo": False, "delay_segundos": 10}
flow_json = json.dumps(flow_cfg).replace("'", "''")
sql_flow = f"INSERT INTO configuracoes (chave, valor, descricao) VALUES ('flow_config', '{flow_json}'::jsonb, 'Configuração do fluxo automático de mensagens') ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = CURRENT_TIMESTAMP;"
i, o, e = c.exec_command(f"docker exec agenda-db psql -U agenda_user -d agenda -c \"{sql_flow}\"")
print(o.read().decode().strip())

# 5. Verificar
print("\n5. Verificando configurações inseridas...")
i, o, e = c.exec_command('docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT chave, descricao, atualizado_em FROM configuracoes;"')
print(o.read().decode().strip())

c.close()
print("\nFase 5 - Tabela de configurações criada com sucesso!")
