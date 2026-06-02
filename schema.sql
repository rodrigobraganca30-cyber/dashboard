-- Tabela de Clientes e Status (Substitui os arquivos JSON e o KEY_STATUS do Redis)
CREATE TABLE IF NOT EXISTS clientes (
    id VARCHAR(50) PRIMARY KEY,
    nome VARCHAR(255),
    telefone VARCHAR(20),
    data DATE,
    cidade VARCHAR(100),
    horario VARCHAR(50),
    endereco TEXT,
    tipo VARCHAR(50),
    fase VARCHAR(20),
    status_ofs VARCHAR(50),
    
    -- Status do fluxo da agenda
    status_atual VARCHAR(50) DEFAULT 'pendente',
    obs_status TEXT,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Mensagens (Substitui KEY_MSGS do Redis)
CREATE TABLE IF NOT EXISTS mensagens (
    id SERIAL PRIMARY KEY,
    telefone VARCHAR(20) NOT NULL,
    remetente VARCHAR(10) NOT NULL, -- 'me' ou 'client'
    texto TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    instancia VARCHAR(50),
    is_auto BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mensagens_telefone ON mensagens(telefone);
CREATE INDEX idx_mensagens_timestamp ON mensagens(timestamp);

-- Tabela de Blacklist (Substitui o Set do Redis)
CREATE TABLE IF NOT EXISTS blacklist (
    telefone VARCHAR(20) PRIMARY KEY,
    motivo TEXT,
    adicionado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Logs (Opcional, para histórico)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    nivel VARCHAR(20),
    mensagem TEXT,
    dados JSONB,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
