CREATE TABLE IF NOT EXISTS gold (
    review_id   BIGINT PRIMARY KEY,
    review_text TEXT NOT NULL,
    text_len    INT  NOT NULL,
    sentimento  TEXT NOT NULL CHECK (sentimento IN ('positivo','neutro','negativo')),
    tema        TEXT NOT NULL CHECK (tema IN ('entrega','qualidade_produto','preco','atendimento','anuncio_divergente','outro')),
    split       TEXT NOT NULL CHECK (split IN ('dev','test')),
    stars       SMALLINT                       -- nota original; só usada na análise, nunca no rótulo
);
CREATE TABLE IF NOT EXISTS runs (
    run_id         BIGSERIAL PRIMARY KEY,
    prompt_version TEXT NOT NULL,
    model          TEXT NOT NULL,
    split          TEXT NOT NULL,
    run_idx        INT  NOT NULL,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS predictions (
    run_id     BIGINT REFERENCES runs(run_id),
    review_id  BIGINT REFERENCES gold(review_id),
    sentimento TEXT,            -- NULL quando a resposta nunca ficou válida
    tema       TEXT,
    valid      BOOLEAN NOT NULL,
    attempts   INT NOT NULL,
    error      TEXT,
    raw        TEXT,
    latency_ms INT,
    PRIMARY KEY (run_id, review_id)
);
