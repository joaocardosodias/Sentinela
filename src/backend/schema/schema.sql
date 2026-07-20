CREATE TABLE users (
    id    UUID PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role  VARCHAR(50)  NOT NULL,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE veiculos (
    id          UUID PRIMARY KEY,
    placa       VARCHAR(10)  UNIQUE NOT NULL,
    modelo      VARCHAR(100) NOT NULL,
    cor         VARCHAR(50)  NOT NULL,
    roubado     BOOLEAN      NOT NULL,
    data_roubo  TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE operacoes (
    id         UUID PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    status     VARCHAR(50)  NOT NULL,
    created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    localizacao VARCHAR(255) NOT NULL
);

CREATE TABLE drones (
    id             UUID PRIMARY KEY,
    operacao_id    UUID         NOT NULL,
    nome           VARCHAR(100) NOT NULL,
    bateria        INTEGER,
    conectividade  VARCHAR(50),
    status_voo     VARCHAR(50)  NOT NULL,
    latitude       DECIMAL(10, 8),
    longitude      DECIMAL(11, 8),

    CONSTRAINT drones_operacao_id_fkey
        FOREIGN KEY (operacao_id) REFERENCES operacoes(id) ON DELETE CASCADE
);

CREATE TABLE scans (
    id                UUID PRIMARY KEY,
    id_drone          UUID          NOT NULL,
    placa             VARCHAR(10)   NOT NULL,
    match             BOOLEAN       NOT NULL,
    imagem_url        VARCHAR(500),
    latitude          DECIMAL(10, 8),
    longitude         DECIMAL(11, 8),
    horario_scan      TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status_validacao  VARCHAR(20)   DEFAULT 'pendente',
    validado_por      UUID          REFERENCES users(id),
    validado_em       TIMESTAMP(0) WITHOUT TIME ZONE,

    CONSTRAINT scans_id_drone_fkey
        FOREIGN KEY (id_drone) REFERENCES drones(id) ON DELETE CASCADE
);

CREATE TABLE veiculos_scans (
    id          UUID PRIMARY KEY,
    id_scan     UUID NOT NULL,
    id_veiculos UUID NOT NULL,

    CONSTRAINT veiculos_scans_id_scan_fkey
        FOREIGN KEY (id_scan)     REFERENCES scans(id)    ON DELETE CASCADE,
    CONSTRAINT veiculos_scans_id_veiculos_fkey
        FOREIGN KEY (id_veiculos) REFERENCES veiculos(id) ON DELETE CASCADE
);

CREATE TABLE usuarios_scans (
    id               UUID PRIMARY KEY,
    usuario_id       UUID        NOT NULL,
    scan_id          UUID        NOT NULL,
    acao_realizada   VARCHAR(50),

    CONSTRAINT usuarios_scans_usuario_fkey
        FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT usuarios_scans_scan_fkey
        FOREIGN KEY (scan_id)    REFERENCES scans(id) ON DELETE CASCADE
);
