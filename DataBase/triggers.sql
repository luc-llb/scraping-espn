-- This file contains the SQL code to create the triggers for the database tables utilizing the MySQL syntax.

DELIMITER //

CREATE TRIGGER insert_Lance 
AFTER INSERT ON Lances
FOR EACH ROW 
BEGIN
    IF NEW.tipo = 'GOL' THEN
        UPDATE Passagens
        SET gols = gols + 1
        WHERE id = NEW.jogador_1;
    ELSEIF NEW.tipo = 'FALTA-FEITA' THEN
        UPDATE Passagens
        SET faltas = faltas + 1
        WHERE id = NEW.jogador_1;
    ELSEIF NEW.tipo = 'CARTAO-AMARELO' THEN
        UPDATE Passagens
        SET amarelos = amarelos + 1
        WHERE id = NEW.jogador_1;
    ELSEIF NEW.tipo = 'CARTAO-VERMELHO' THEN
        UPDATE Passagens
        SET vermelhos = vermelhos + 1
        WHERE id = NEW.jogador_1;
    ELSEIF NEW.tipo = 'LESAO' THEN
        UPDATE Passagens
        SET lesoes = lesoes + 1
        WHERE id = NEW.jogador_1;
    END IF;
END //

DELIMITER ;