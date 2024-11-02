-- This file contains the SQL code to create the database tables utilizing the MySQL syntax.

CREATE TABLE Partidas(
	id INT AUTO_INCREMENT,
    espn_id INT NOT NULL UNIQUE,
    local_ VARCHAR(255),
    estadio VARCHAR(255),
    campeonato VARCHAR(100),
    arbitro VARCHAR(255) DEFAULT '',
    data_ VARCHAR(12),
    horario TIME DEFAULT '00:00:00',
    audiencia INT DEFAULT 0,
    
    CONSTRAINT ct_id_partida PRIMARY KEY(id)
);

CREATE TABLE Times (
	id INT AUTO_INCREMENT,
    espn_id INT NOT NULL UNIQUE,
    nome VARCHAR(100),
    
    CONSTRAINT ct_id_time PRIMARY KEY (id)
);

CREATE TABLE EstatisticasPartida(
    id INT AUTO_INCREMENT,
    id_partida INT,
    id_time INT,
    chute_gol TINYINT DEFAULT 0,
    gol TINYINT DEFAULT 0,
    chute TINYINT DEFAULT 0,
    defesa TINYINT DEFAULT 0,
    posse TINYINT DEFAULT 0,
    
    CONSTRAINT ct_id_estPart PRIMARY KEY(id),
    CONSTRAINT ct_partida_estPart FOREIGN KEY (id_partida)
    REFERENCES Partidas (id) ON DELETE CASCADE,
    CONSTRAINT ct_time_estPart FOREIGN KEY (id_time)
    REFERENCES Times (id) ON DELETE RESTRICT
);

CREATE TABLE Jogadores(
	id INT AUTO_INCREMENT,
    espn_id INT NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    posicao VARCHAR(10) DEFAULT '--',
    idade TINYINT,
    altura REAL,
    nacionalidade VARCHAR(100),

    CONSTRAINT ct_id_jogadores PRIMARY KEY (id)
);

CREATE TABLE Passagens (
	id INT AUTO_INCREMENT,
    id_jogador INT NOT NULL,
    id_time INT NOT NULL,
    ano YEAR DEFAULT  YEAR(CURRENT_DATE()),
    gols TINYINT DEFAULT 0,
    faltas TINYINT DEFAULT 0,
    amarelos TINYINT DEFAULT 0,
    vermelhos TINYINT DEFAULT 0,
    lesoes TINYINT DEFAULT 0,
    
    CONSTRAINT ct_id_pass PRIMARY KEY (id),
    CONSTRAINT ct_jogador_pass FOREIGN KEY (id_jogador)
    REFERENCES Jogadores (id) ON DELETE CASCADE,
    CONSTRAINT ct_time_pass FOREIGN KEY (id_time)
    REFERENCES Times (id) ON DELETE CASCADE
);

CREATE TABLE Escalacoes(
	id INT AUTO_INCREMENT,
    id_partida INT NOT NULL,
    id_passagem INT NOT NULL,
    status_ VARCHAR(10),
    
    CONSTRAINT ct_id_escalacoes PRIMARY KEY (id),
    CONSTRAINT ct_part_escalacoes FOREIGN KEY (id_partida)
    REFERENCES Partidas (id) ON DELETE RESTRICT,
    CONSTRAINT ct_pass_escalacoe FOREIGN KEY (id_passagem)
    REFERENCES Passagens (id) ON DELETE RESTRICT
);

CREATE TABLE Lances (
	id INT AUTO_INCREMENT,
    id_partida INT NOT NULL,
    jogador_1 INT,
    jogador_2 INT,
    tipo VARCHAR(15),
    minuto VARCHAR(7) DEFAULT '--',
    descricao VARCHAR(255) DEFAULT '',
    time_beneficiado INT,
    
    CONSTRAINT ct_id_lances PRIMARY KEY (id),
    CONSTRAINT ct_partida_lances FOREIGN KEY (id_partida)
    REFERENCES Partidas (id) ON DELETE RESTRICT,
    CONSTRAINT ct_jogador1_lances FOREIGN KEY (jogador_1)
    REFERENCES Passagens (id) ON DELETE RESTRICT,
    CONSTRAINT ct_jogador2_lances FOREIGN KEY (jogador_2)
    REFERENCES Passagens (id) ON DELETE RESTRICT,
    CONSTRAINT ct_time_lances FOREIGN KEY (time_beneficiado)
    REFERENCES Times (id) ON DELETE RESTRICT
);
