-- This script is resbonsible to inserting the datas getting by scraping in the database.

-- Saving the datas to tables without foreigns keys 

-- Times
LOAD DATA INFILE 'Datas/times.csv'
INTO TABLE Times
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(nome, espn_id);

-- Jogadores
LOAD DATA INFILE 'Datas/jogadores.csv'
INTO TABLE Jogadores
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(nome, espn_id, posicao, idade, altura, nacionalidade);

-- Partida
LOAD DATA INFILE 'Datas/partidas.csv'
INTO TABLE Partidas
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(espn_id, local_, estadio, campeonato, arbitro, data_, horario, audiencia);

-- Saving data to tables that have relationships with other tables

-- EstatisticasPartida
CREATE TEMPORARY TABLE t_stats (
    id_partida INT,
    id_time VARCHAR(100),
    chute_gol TINYINT DEFAULT 0,
    gol TINYINT DEFAULT 0,
    chute TINYINT DEFAULT 0,
    defesa TINYINT DEFAULT 0,
    posse TINYINT DEFAULT 0
);

LOAD DATA INFILE 'Datas/estatisticas.csv'
INTO TABLE t_stats
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id_partida, id_time, chute_gol, gol, chute, defesa, posse);

INSERT INTO EstatisticasPartida (id_partida, id_time, chute_gol, gol, chute, defesa, posse)
SELECT
    p.id,
    t.id,
    s.chute_gol,
    s.gol,
    s.chute,
    s.defesa,
    s.posse
FROM t_stats s
INNER JOIN Partidas p ON p.espn_id = s.id_partida
INNER JOIN Times t ON t.nome = s.id_time;

DROP TEMPORARY TABLE t_stats;

-- Passagens
CREATE TEMPORARY TABLE t_passagens (
    id_jogador INT NOT NULL,
    id_time INT NOT NULL,
    ano YEAR DEFAULT YEAR(CURRENT_DATE())
);

LOAD DATA INFILE 'Datas/passagens.csv'
INTO TABLE t_passagens
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id_jogador, id_time, ano);

INSERT INTO Passagens (id_jogador, id_time, ano)
SELECT j.id, t.id, pass.ano FROM t_passagens pass
INNER JOIN Jogadores j ON j.espn_id = pass.id_jogador
INNER JOIN Times t ON t.espn_id = pass.id_time;

DROP TEMPORARY TABLE t_passagens;

-- Escalacoes
CREATE TEMPORARY TABLE t_escalacoes (
    nome_time VARCHAR(100) NOT NULL,
    id_partida INT NOT NULL,
    id_jogador INT NOT NULL,
    status_ VARCHAR(20)
);

LOAD DATA INFILE 'Datas/escalacoes.csv'
INTO TABLE t_escalacoes
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(nome_time, id_partida, id_jogador, status_);

INSERT INTO Escalacoes (id_partida, id_passagem, status_)
SELECT
    p.id,
    q.passagens,
    temp.status_
FROM t_escalacoes temp
INNER JOIN Partidas p ON p.espn_id = temp.id_partida
INNER JOIN (
    SELECT 
        pass.id AS passagens,
    	t.nome AS nome_time,
    	j.espn_id
    FROM Passagens pass
    INNER JOIN Jogadores j ON j.id = pass.id_jogador
    INNER JOIN Times t ON t.id = pass.id_time 
) q ON q.nome_time = temp.nome_time AND q.espn_id = temp.id_jogador;

-- Players can switch to other teams
CREATE TEMPORARY TABLE t_new_passagens (
    id_partida INT NOT NULL,
    espn_id_jogador INT,
    nome_time VARCHAR(100),
    status_ VARCHAR(20)
);

INSERT INTO t_new_passagens (id_partida, espn_id_jogador, nome_time, status_)
SELECT
    temp.id_partida,
    temp.id_jogador,
    temp.nome_time,
    temp.status_
FROM t_escalacoes temp
LEFT JOIN Partidas p ON p.espn_id = temp.id_partida
LEFT JOIN (
    SELECT 
        pass.id AS passagens,
    	t.nome AS nome_time,
    	j.espn_id
    FROM Passagens pass
    INNER JOIN Jogadores j ON j.id = pass.id_jogador
    INNER JOIN Times t ON t.id = pass.id_time 
) q ON q.nome_time = temp.nome_time AND q.espn_id = temp.id_jogador
WHERE q.espn_id IS NULL OR q.nome_time IS NULL OR q.passagens IS NULL;

DROP TEMPORARY TABLE t_escalacoes;

-- Bug: Players who changed teams internationally are not included in the Passage table	
INSERT INTO Passagens (id_jogador, id_time)
SELECT j.id, t.id FROM t_new_passagens pass
JOIN Jogadores j ON j.espn_id = pass.espn_id_jogador
JOIN Times t ON t.nome = pass.nome_time;

INSERT INTO Escalacoes (id_partida, id_passagem, status_)
SELECT
    p.id,
    q.passagem,
    temp.status_
FROM t_new_passagens temp
INNER JOIN Partidas p ON p.espn_id = temp.id_partida
INNER JOIN (
    SELECT 
        pass.id AS passagens,
    	t.nome AS nome_time,
    	j.espn_id
    FROM Passagens pass
    INNER JOIN Jogadores j ON j.id = pass.id_jogador
    INNER JOIN Times t ON t.id = pass.id_time 
) q ON q.nome_time = temp.nome_time AND q.espn_id = temp.espn_id_jogador;

DROP TEMPORARY TABLE t_new_passagens;

-- Lances

CREATE TEMPORARY TABLE t_lances(
    id_partida INT NOT NULL,
    jogador_1 VARCHAR(255),
    jogador_2 VARCHAR(255),
    tipo VARCHAR(25),
    minuto VARCHAR(7),
    descricao VARCHAR(255),
    time_beneficiado VARCHAR(100)  
);

LOAD DATA INFILE 'Datas/lances.csv'
INTO TABLE t_lances
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id_partida, jogador_1, jogador_2, tipo, minuto, descricao, @time_beneficiado)
-- Removes the last element of the string to fix compatibility errors
SET time_beneficiado = SUBSTRING(@time_beneficiado, 1, LENGTH(@time_beneficiado) - 1);

UPDATE t_lances SET jogador_1 = NULL WHERE jogador_1 = '';
UPDATE t_lances SET jogador_2 = NULL WHERE jogador_2 = '';
UPDATE t_lances SET time_beneficiado = NULL WHERE time_beneficiado = '';
UPDATE t_lances SET descricao = NULL WHERE descricao = '';

CREATE TEMPORARY TABLE v_pass AS
    SELECT 
        pass.id AS id_passagem,
        t.id AS id_time,
        t.nome AS nome_time,
        j.nome AS nome_jogador
    FROM Passagens pass
    INNER JOIN Jogadores j ON j.id = pass.id_jogador
    INNER JOIN Times t ON t.id = pass.id_time;

INSERT INTO Lances (id_partida, jogador_1, jogador_2, tipo, minuto, descricao, time_beneficiado)
SELECT
    p.id id_partida,
    j1.id_passagem id_jogador_1,
    j2.id_passagem id_jogador_2,
    temp.tipo,
    temp.minuto,
    temp.descricao,
    t.id time_beneficiado
FROM t_lances temp
INNER JOIN Partidas p ON p.espn_id = temp.id_partida
LEFT JOIN v_pass j1 ON j1.nome_jogador = temp.jogador_1
LEFT JOIN v_pass j2 ON j2.nome_jogador = temp.jogador_2
LEFT JOIN Times t ON t.nome = temp.time_beneficiado
;

DROP TEMPORARY TABLE t_lances;
DROP TEMPORARY TABLE v_pass;