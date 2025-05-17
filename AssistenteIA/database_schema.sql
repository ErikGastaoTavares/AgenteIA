-- Estrutura do Banco SQLite (validacao_triagem.db)

-- Tabela de Triagens
CREATE TABLE validacao_triagem (
    id TEXT PRIMARY KEY,           -- UUID único da triagem
    sintomas TEXT,                 -- Descrição dos sintomas
    resposta TEXT,                 -- Resposta/classificação do sistema
    data_hora DATETIME,           -- Data/hora da triagem
    validado INTEGER DEFAULT 0,   -- Status de validação (0=pendente, 1=validado)
    feedback TEXT,                -- Feedback do especialista
    validado_por TEXT,            -- Usuário que validou
    data_validacao DATETIME       -- Data/hora da validação
);

-- Tabela de Usuários
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,         -- Nome de usuário
    password TEXT,               -- Senha (hash)
    perfil TEXT,                -- Perfil (admin/médico/enfermeiro)
    status INTEGER DEFAULT 1    -- Status do usuário (ativo/inativo)
);

-- Tabela de Validações (histórico)
CREATE TABLE validacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    triagem_id TEXT,             -- Referência à triagem
    usuario_id INTEGER,          -- Usuário que validou
    data_validacao DATETIME,     -- Data/hora da validação
    feedback TEXT,               -- Feedback/observações
    FOREIGN KEY (triagem_id) REFERENCES validacao_triagem(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de Casos Iniciais
CREATE TABLE IF NOT EXISTS casos_iniciais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sintomas TEXT NOT NULL,           -- Descrição dos sintomas
    classificacao TEXT NOT NULL,      -- Classificação de Manchester
    encaminhamento TEXT NOT NULL,     -- Conduta sugerida
    ativo INTEGER DEFAULT 1          -- Status do caso (1=ativo, 0=inativo)
);

-- Inserir casos base iniciais
INSERT INTO casos_iniciais (sintomas, classificacao, encaminhamento) VALUES 
    ('Paciente do sexo masculino, 58 anos, com dor torácica intensa há 20 minutos, irradiação para o braço esquerdo, sudorese, PA 180/100 mmHg', 'Vermelha', 'Atendimento imediato na sala de emergência'),
    ('Paciente jovem, 24 anos, com febre de 38,5ºC, tosse seca, dor de garganta e cefaleia há 3 dias. Saturação de oxigênio: 97%', 'Verde', 'Consultório clínico para avaliação ambulatorial'),
    ('Paciente idoso, 79 anos, com confusão mental súbita, pressão arterial 90/60 mmHg, glicemia capilar 60 mg/dL. Sem sinais de trauma', 'Amarela', 'Avaliação médica prioritária e monitoramento'),
    ('Paciente com crise convulsiva ativa no momento da triagem, sem histórico conhecido', 'Vermelha', 'Sala de emergência para contenção e avaliação neurológica'),
    ('Paciente com falta de ar aos mínimos esforços, tosse produtiva, chiado no peito. Saturação: 89%. Histórico de DPOC', 'Laranja', 'Atendimento médico com suporte de oxigênio');