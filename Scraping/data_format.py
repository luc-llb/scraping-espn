'''
This module is responsible for formatting the data to be saved in the database.
*Obs.: The databe in question is represented in the image in REDME.md.
'''
import os
import csv

def stats_formatting(data: dict, id: str) -> list:
        '''Atomic function to format the data from the stats of a game'''

        return {
            'id_partida': id,
            'id_time': data['time'],
            'chute_gol': int(data['chute a gol']),
            'gol': int(data['gols']),
            'chute': int(data['chute']),
            'defesa': int(data['defesas']),
            'posse': float(data['posse'])
        }
    
def lineUp_formatting(data: dict, team: str, game: str) -> list:
    '''Atomic function to format the data from the line-up of a game'''
    
    datas = []
    for key, value in data.items():
       if value is None:
            continue
       for name in value:
            player = {
                'time': team,
                'partida': int(game),
                'jogador': int(name)
            }
            if key == 'titulares':
                player['status_'] = 'TITULAR'
            elif key == 'substitutos':
                player['status_'] = 'SUBSTITUTO'
            else:
                player['status_'] = 'RESERVA'
            datas.append(player)
    return datas

def format_jogadores(data: dict) -> dict:
    '''Format the data from the table Jogadores'''

    return {
        'nome': data['nome'],
        'espn_id': int(data['espn_id']),
        'posicao': data['posicao'],
        'idade': int(data['idade']),
        'altura': float(data['altura'].replace(' m', '')) if data['altura'] != None else None,
        'nacionalidade': data['nacionalidade']
    }

def format_lances(data: dict) -> list:
    '''Format the data from the table Lances'''

    datas = []
    data_aux = data.copy()
    game = data_aux.pop('partida')
    for key, value in data_aux.items():
        datas.append({
            'id_partida': game,
            'jogador_1': value['jogador-1'],
            'jogador_2': value['jogador-2'],
            'tipo': value['tipo'],
            'minuto': value['minuto'],
            'descricao': value['descricao'],
            'time': value['time']
        })
    return datas

def format_partidas(data: dict) -> dict:
    '''Format the data from the table Partidas'''

    return {
        'espn_id': int(data['partida']),
        'local_': data['local'],
        'estadio': data['estadio'],
        'campeonato': data['campeonato'],
        'arbitro': data['arbitro'],
        'data_': data['data'],
        'horario': data['horario'],
        'audiencia': int(data['audiencia']) if data['audiencia'] != None else None,
        # 'mandante': data['mandante']['time'],
        # 'visitante': data['visitante']['time'],
    }

def format_estatisticas_partida(data: dict) -> list:
    '''Format the data from the table EstatisticasPartida'''
    datas = [stats_formatting(data['mandante'], data['partida'])]
    datas.append(stats_formatting(data['visitante'], data['partida']))
    return datas

def format_escalacoes(data: dict) -> list:
    '''Format the data from the table Escalacoes'''

    teams = list(data.keys())  # Get team names
    datas = [lineUp_formatting(data[teams[1]], teams[1], data['partida'])]
    datas.append(lineUp_formatting(data[teams[2]], teams[2], data['partida']))
    return datas

def format_times(data: dict) -> dict:
    '''Format the data from the table Times'''

    team = list(data.keys())[0]
    return {
        'nome': team,
        'espn_id': int(data[team].split('/')[0])
    }

def format_passagens(data: dict) -> list:
    '''Format the data from the table Passagens'''

    datas = []
    time = data['time'].split('/')[0]
    for player in data['jogadores']:
        datas.append({
            'id_jogador': int(player['espn_id']),
            'id_time': int(time),
            'ano': int(data['temporada'])
        })
    return datas

def save_toCSV(datas: list, filename: str, columns: list[str]) -> None:

    # Verify the file path and create the directory if needed
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()
        for data in datas:
            writer.writerow(data)
        file.close()

def data_formatting(data: dict, table: str) -> list | dict:
    '''Formating the data to a save in the database'''

    if not isinstance(data, dict):
        print('data should be a dictionary')
        return []
    elif not isinstance(table, str):
        print('table should be a string')
        return []

    title = table.upper()
    if title == "JOGADORES":
        return format_jogadores(data)
    elif title == "LANCES":
        return format_lances(data)
    elif title == "PARTIDAS":
        return format_partidas(data)
    elif title == "ESTATISTICAS-PARTIDA":
        return format_estatisticas_partida(data)
    elif title == "ESCALACOES":
        return format_escalacoes(data)
    elif title == "TIMES":
        return format_times(data)
    elif title == "PASSAGENS":
        return format_passagens(data)
    else:
        print('specify a valid table')
        return []