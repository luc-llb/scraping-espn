'''
This script is responsible for getting the data from the games and saving them in csv files.
'''

import scraping as sc
import logging
import data_format as df

# Configurando o log
logging.basicConfig(filename='getting_data.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

# obtendo os links dos jogos desde a primeira rodada 2024-04-13
jogos = sc.get_all_games(20240413) 

# Obterndo os dados de cada jogo
dados = {
    'estatisticas': [],
    'lances': [],
    'escalacoes': [],
}

for jogo in jogos.values():
    if jogo is None:
        continue
    for id in jogo:
        logging.info(f'Getting data from game {id}')
        dados['estatisticas'].append(sc.get_datas_from_estatisticas(str(id)))
        dados['lances'].append(sc.get_datas_from_comentarios(str(id)))
        dados['escalacoes'].append(sc.get_lineup(str(id)))

# Formatando os dados para utiliza-los no banco de dados
estatisticas, escalacoes, lances, partidas = [], [], [], []

for i in range(len(dados['estatisticas'])):
    if not dados['estatisticas'][i] is None:
        aux = df.format_estatisticas_partida(dados['estatisticas'][i])
        for e in aux:
            estatisticas.append(e) 
        partidas.append(df.format_partidas(dados['estatisticas'][i]))
    
    if not dados['lances'][i] is None:
        aux = df.format_lances(dados['lances'][i])
        for e in aux:
            lances.append(e)
    
    if not dados['escalacoes'][i] is None:
        aux = df.format_escalacoes(dados['escalacoes'][i])
        for team in aux:
            for e in team:
                escalacoes.append(e)

# Obtendo os dados dos times e jogadores
times_id = sc.get_teams_id()
elencos = []
for time in times_id:
    if time is None:
        continue
    for nome, id in time.items():
        elencos.append(sc.get_cast(id))

jogadores, passagens = [], []
for time in elencos:
    if time is None:
        continue
    for jogador in time['jogadores']:
        jogadores.append(df.format_jogadores(jogador))
    aux = df.format_passagens(time)
    for e in aux:
        passagens.append(e)

times = []
for time in times_id:
    if time is None:
        continue
    times.append(df.format_times(time))

# Salvando os dados em arquivos csv (cada csv é uma tabela do banco de dados)
df.save_toCSV(estatisticas, 'Datas/estatisticas.csv', ['id_partida', 'time', 'chute_gol', 'chute', 'gol', 'defesa', 'posse'])
df.save_toCSV(escalacoes, 'Datas/escalacoes.csv', ['time', 'partida', 'jogador', 'status'])
df.save_toCSV(lances, 'Datas/lances.csv', ['partida', 'jogador-1', 'jogador-2', 'tipo', 'minuto', 'descricao', 'time'])
df.save_toCSV(partidas, 'Datas/partidas.csv', ['partida', 'local', 'estadio', 'campeonato', 'arbitro', 'data', 'horario', 'audiencia', 'mandante', 'visitante'])
df.save_toCSV(jogadores, 'Datas/jogadores.csv', ['nome', 'posicao', 'idade', 'altura', 'nacionalidade'])
df.save_toCSV(passagens, 'Datas/passagens.csv', ['jogador', 'time', 'ano'])
df.save_toCSV(times, 'Datas/times.csv', ['id', 'nome'])
