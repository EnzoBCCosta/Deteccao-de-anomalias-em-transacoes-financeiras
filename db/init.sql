-- =====================================================================
-- Script de criação do banco (executado automaticamente pelo container
-- do PostgreSQL na primeira inicialização - ver docker-compose.yml).
-- 5 tabelas: categoria, conta, transacao, perfil_conta, alerta_anomalia
-- As regras de negócio ficam na API (camada services); aqui ficam apenas
-- a estrutura e as restrições de integridade (chaves, CHECK, UNIQUE).
-- =====================================================================

CREATE TABLE categoria (
    id   SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE conta (
    id        SERIAL PRIMARY KEY,
    titular   VARCHAR(120) NOT NULL,
    criada_em TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE transacao (
    id           BIGSERIAL PRIMARY KEY,
    conta_id     INT NOT NULL REFERENCES conta(id),
    categoria_id INT NOT NULL REFERENCES categoria(id),
    valor        NUMERIC(14,2) NOT NULL CHECK (valor > 0),          -- regra 1 (proteção extra)
    data_hora    TIMESTAMP NOT NULL DEFAULT NOW(),
    descricao    TEXT,
    status       VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (status IN ('normal', 'anomala'))
);

-- Perfil de gastos da conta (1:1 com conta). Atualizado a cada nova transação.
CREATE TABLE perfil_conta (
    conta_id        INT PRIMARY KEY REFERENCES conta(id) ON DELETE CASCADE,
    qtd_transacoes  INT NOT NULL DEFAULT 0 CHECK (qtd_transacoes >= 0),
    media           NUMERIC(18,4) NOT NULL DEFAULT 0,
    m2              NUMERIC(24,4) NOT NULL DEFAULT 0,
    desvio_padrao   NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (desvio_padrao >= 0),
    atualizado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE alerta_anomalia (
    id           BIGSERIAL PRIMARY KEY,
    transacao_id BIGINT NOT NULL REFERENCES transacao(id) ON DELETE RESTRICT,   -- regra 6 (proteção extra)
    conta_id     INT NOT NULL REFERENCES conta(id),
    tipo         VARCHAR(30) NOT NULL CHECK (tipo IN ('valor_elevado', 'horario_atipico', 'rajada_transacoes')),
    severidade   VARCHAR(10) NOT NULL CHECK (severidade IN ('baixa', 'media', 'alta')),
    descricao    TEXT NOT NULL,
    metrica      NUMERIC(18,4),
    criado_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transacao_conta_data     ON transacao (conta_id, data_hora);
CREATE INDEX idx_transacao_categoria_data ON transacao (categoria_id, data_hora);
CREATE INDEX idx_alerta_transacao         ON alerta_anomalia (transacao_id);
CREATE INDEX idx_alerta_conta             ON alerta_anomalia (conta_id);

-- Dados iniciais (para a demonstração; o histórico de transações é criado
-- pela API com scripts/popular_demo.py, assim as regras de detecção rodam).
INSERT INTO categoria (nome) VALUES ('Alimentação'), ('Transporte'), ('Lazer');
INSERT INTO conta (titular) VALUES ('João Silva'), ('Maria Souza');
