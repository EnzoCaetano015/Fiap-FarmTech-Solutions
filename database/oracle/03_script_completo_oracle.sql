BEGIN EXECUTE IMMEDIATE 'DROP TABLE FARMTECH_SENSOR_LEITURA';

EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE;

END IF;

END;

/
CREATE TABLE
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA NUMBER PRIMARY KEY,
        DATA_HORA TIMESTAMP NOT NULL,
        UMIDADE NUMBER (5, 2) NOT NULL,
        TEMPERATURA NUMBER (5, 2) NOT NULL,
        PH NUMBER (4, 2) NOT NULL,
        N NUMBER (1) NOT NULL,
        P NUMBER (1) NOT NULL,
        K NUMBER (1) NOT NULL,
        NIVEL_CHUVA NUMBER (1) NOT NULL,
        STATUS_IRRIGACAO VARCHAR2 (20) NOT NULL,
        SUGESTAO VARCHAR2 (255)
    );

ALTER TABLE FARMTECH_SENSOR_LEITURA ADD CONSTRAINT CK_FARMTECH_N CHECK (N IN (0, 1));

ALTER TABLE FARMTECH_SENSOR_LEITURA ADD CONSTRAINT CK_FARMTECH_P CHECK (P IN (0, 1));

ALTER TABLE FARMTECH_SENSOR_LEITURA ADD CONSTRAINT CK_FARMTECH_K CHECK (K IN (0, 1));

ALTER TABLE FARMTECH_SENSOR_LEITURA ADD CONSTRAINT CK_FARMTECH_NIVEL_CHUVA CHECK (NIVEL_CHUVA IN (0, 1, 2));

ALTER TABLE FARMTECH_SENSOR_LEITURA ADD CONSTRAINT CK_FARMTECH_STATUS_IRRIG CHECK (STATUS_IRRIGACAO IN ('LIGADA', 'DESLIGADA'));

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        1,
        TO_TIMESTAMP ('2026-05-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        32.5,
        24.8,
        6.4,
        1,
        1,
        1,
        0,
        'LIGADA',
        'Irrigar por 15 minutos'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        2,
        TO_TIMESTAMP ('2026-05-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        45.2,
        28.1,
        6.7,
        1,
        1,
        1,
        1,
        'DESLIGADA',
        'Sem irrigacao devido a umidade adequada'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        3,
        TO_TIMESTAMP ('2026-05-01 16:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        29.9,
        29.5,
        6.2,
        1,
        1,
        0,
        0,
        'LIGADA',
        'Irrigar e verificar nutriente K'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,    
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        4,
        TO_TIMESTAMP ('2026-05-02 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        38.0,
        23.9,
        5.4,
        1,
        0,
        1,
        0,
        'DESLIGADA',
        'Correcao de P antes de irrigar'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        5,
        TO_TIMESTAMP ('2026-05-02 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        27.3,
        27.2,
        6.9,
        1,
        1,
        1,
        2,
        'DESLIGADA',
        'Chuva forte prevista; adiar irrigacao'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        6,
        TO_TIMESTAMP ('2026-05-02 16:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        33.8,
        26.4,
        7.6,
        1,
        1,
        1,
        0,
        'DESLIGADA',
        'pH alto; ajustar antes de irrigar'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        7,
        TO_TIMESTAMP ('2026-05-03 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        41.1,
        22.7,
        6.5,
        1,
        1,
        1,
        1,
        'DESLIGADA',
        'Monitorar e manter irrigacao desligada'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        8,
        TO_TIMESTAMP ('2026-05-03 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        26.7,
        30.0,
        6.1,
        1,
        1,
        1,
        0,
        'LIGADA',
        'Irrigar por 20 minutos'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        9,
        TO_TIMESTAMP ('2026-05-03 16:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        35.4,
        27.6,
        6.8,
        0,
        1,
        1,
        0,
        'DESLIGADA',
        'Adicionar N antes de irrigar'
    );

INSERT INTO
    FARMTECH_SENSOR_LEITURA (
        ID_LEITURA,
        DATA_HORA,
        UMIDADE,
        TEMPERATURA,
        PH,
        N,
        P,
        K,
        NIVEL_CHUVA,
        STATUS_IRRIGACAO,
        SUGESTAO
    )
VALUES
    (
        10,
        TO_TIMESTAMP ('2026-05-04 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        31.2,
        24.2,
        6.3,
        1,
        1,
        1,
        1,
        'LIGADA',
        'Irrigar levemente; chuva fraca'
    );

COMMIT;

-- Consultas de validacao
SELECT
    COUNT(*) AS TOTAL_REGISTROS
FROM
    FARMTECH_SENSOR_LEITURA;

SELECT
    *
FROM
    FARMTECH_SENSOR_LEITURA
ORDER BY
    DATA_HORA;