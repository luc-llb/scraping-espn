'''
This file contains the code for scraping the data from the website from ESPN.

By @luc-llb
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
import logging

def get_soup(url: str) -> BeautifulSoup | None:
    '''Return de BeautifulSoup object from a url'''

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    if(type(url) != str):
        logging.warning('URL must be a string')
        return None

    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        logging.warning(f'Error {page.status_code}')
        return None
    return BeautifulSoup(page.content, 'html.parser')

def verify_page(url: str) -> BeautifulSoup | None:
    '''Verify if the page is empty'''
    page = get_soup(url)

    if page is None:
        logging.warning('Page not found')
        return None
    elif not page.find('h1', class_='Error404__Title') is None:
        logging.warning('Data not found')
        return None
    return page

def get_games(url: str) -> list | None:
    '''Get the IDs of all games from a specific URL'''
    
    page = verify_page(url)
    
    if page is None:
        return None
    elif not page.find('h4', class_='n5 tc pv6 clr-gray-05') is None:
        logging.warning('No data found')
        return None
    
    links = page.find_all('a', class_='AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100 mr2')
    ids = [l['href'].replace('/futebol/partida-estatisticas/_/jogoId/','') for l in links if 'partida-estatisticas' in l['href']]
    if not ids:
        logging.warning('No links found')
        return None
    return ids

def get_all_games(from_date: int, to_date: int = 0) -> dict | None:
    '''
    Gets all links to games within a specific date range.
    If no end date is given, it is considered the current date.
    Use from_date < to_date .
    '''
    today = int(datetime.date.today().strftime('%Y%m%d'))
    if to_date == 0:
        to_date = today
    elif from_date > today or to_date > today:
        print('Date is greater than today. This function returns only past games for security reasons.')
        return None

    if from_date > to_date:
        print('Initial date is greater than end date')
        return None
    
    init = datetime.datetime.strptime(str(from_date), '%Y%m%d')
    end = datetime.datetime.strptime(str(to_date), '%Y%m%d')
    data_range = pd.date_range(start=init, end=end)
    data_range = [date.strftime('%Y%m%d') for date in data_range]

    pages = {}
    for date in data_range:
        url = f'https://www.espn.com.br/futebol/resultados/_/data/{date}/liga/bra.1'
        logging.info(f'Getting IDs from {url}:')
        links = get_games(url)
        if not links is None:
            pages[date] = links
    return pages

def get_datas_from_estatisticas(id: str) -> dict | None:
    '''Get the stats from a game by the page Estatisticas'''

    if type(id) != str:
        logging.warning('ID must be a string')
        return None

    url = f'https://www.espn.com.br/futebol/partida-estatisticas/_/jogoId/{id}'
    page = verify_page(url)

    if page is None:
        return None
    elif page.find_all('div', class_='Gamestrip__Score relative tc w-100 fw-heavy-900 h2 clr-gray-01') == []:
        # This is a way to check if the game was canceled, when there is no score
        logging.warning('Game canceled')
        return None
    
    team1 = {}
    team2 = {}

    # Finding team names
    aux = page.find_all('h2', class_='ScoreCell__TeamName ScoreCell__TeamName--displayName db')
    aux = [name.text for name in aux]
    
    team1['time'], team2['time'] = aux[0], aux[1]

    # Finding gols
    aux = page.find_all('div', class_='Gamestrip__Score relative tc w-100 fw-heavy-900 h2 clr-gray-01')
    aux = [gol.text for gol in aux]
    for i in range(len(aux)):
        index = aux[i].find('V') # Removing extra information
        if index != -1:
            aux[i] = aux[i][:index]
    team1['gols'], team2['gols'] = aux[0], aux[1]

    # Finding team stats
    labels = ['chute a gol', 'chute', 'faltas', 'amarelos', 'vermelhos', 'escanteios', 'defesas']
    aux = page.find_all('span', class_='bLeWt ZfQkn JoGSb hsDdd ICQCm')
    aux = [stat.text for stat in aux]
    
    count = 0
    for i in range(0, len(labels)*2, 2):
        if labels[count] in ['chute a gol', 'chute', 'defesas']: # Other information can be extracted from the game's plays
            team1[labels[count]], team2[labels[count]] = aux[i], aux[i+1]
        count += 1
    
    # Finding possession
    aux = page.find('span', class_='bLeWt ZfQkn JoGSb VZTD pgHdv uHRs')
    team1['posse'] = aux.text.replace('%','')

    aux = page.find('span', class_='bLeWt ZfQkn JoGSb VZTD nljvg')
    team2['posse'] = aux.text.replace('%','')

    # Finding general information about the game
    general_inf = {
        'partida': id
    } 

    aux = page.find('div', class_='ScoreCell__GameNote di')
    general_inf['campeonato'] = aux.text if aux is not None else None

    aux = page.find('div', class_='n6 clr-gray-03 GameInfo__Location__Name--noImg')
    general_inf['estadio'] = aux.text if aux is not None else None

    aux = page.find('div', class_='n8 GameInfo__Meta')
    aux = aux.find('span').text.split(',') if aux is not None else None
    general_inf['horario'] = aux[0] if aux is not None else None
    general_inf['data'] = aux[1] if aux is not None else None

    aux = page.find('span', class_='Location__Text')
    general_inf['local'] = aux.text if aux is not None else None

    aux = page.find('div', class_='Attendance__Numbers')
    general_inf['audiencia'] = aux.text.replace('Attendance:','').replace(',','') if aux is not None else None

    aux = page.find('li', class_='GameInfo__List__Item')
    general_inf['arbitro'] = aux.text if aux is not None else None

    general_inf['mandante'] = team1
    general_inf['visitante'] = team2

    return general_inf

def get_data_from_comment(index: int, text: str, minute: str) -> None:
    key = index
    datas = {key:{'jogador-1':None, 'jogador-2':None, 'time':None, 'tipo':None, 'descricao':None, 'minuto':''}}

    datas[key]['minuto'] = minute
    if "Falta cometida" in text:
        point = text.find('(') # Dot where is the team name
        datas[key]['jogador-1'] = text[19:point-1]
        datas[key]['time'] = text[point+1:len(text)-2] # removing the parentheses
        datas[key]['tipo'] = 'FALTA-FEITA'

    elif "sofre uma falta" in text:
        point = text.find('(')
        datas[key]['jogador-2'] = text[:point-1]
        datas[key]['time'] = text[point+1:text.find(')')]
        datas[key]['tipo'] = 'FALTA-SOFRIDA'

    elif "Oportunidade perdida" in text:
        point = text.find('(')
        datas[key]['jogador-1'] = text[21:point-1]
        datas[key]['time'] = text[point+1:text.find(')')]
        datas[key]['tipo'] = 'GOL-PERDIDO'
        description = text[text.find(','):text.find('.')]
        if 'cabeça' in description: # Checking the type of shot
            datas[key]['descricao'] = 'CABECEIO'
        elif 'pé direito' in description: 
            datas[key]['descricao'] = 'CHUTE (pé direito)'
        else:
            datas[key]['descricao'] = 'CHUTE (pé esquerdo)'

    elif "Escanteio" in text:
        point = text.find('.')
        datas[key]['time'] = text[11:point]
        datas[key]['jogador-2'] = text[point+13:-1]
        datas[key]['tipo'] = 'ESCANTEIO'

    elif "Impedimento" in text:
        point = text.find('.')
        datas[key]['jogador-1'] = text[point+2:text.find('tentou')-1]
        datas[key]['jogador-2'] = text[text.find('encontrou')+10:text.find(' em posição')]
        datas[key]['time'] = text[13:point]
        datas[key]['tipo'] = 'IMPEDIMENTO'

    elif "cartão" in text:
        point = text.find('(')
        datas[key]["jogador-1"] = text[:point-1]
        datas[key]['time'] = text[point+1:text.find(')')]
        if 'por' in text:
            datas[key]['descricao'] = text[text.find('por', point):-1]
        if 'amarelo' in text:
            datas[key]['tipo'] = 'CARTAO-AMARELO'
        elif 'vermelho' in text:
            datas[key]['tipo'] = 'CARTAO-VERMELHO'

    elif "Gol" in text:
        point = text.find(' (')
        datas[key]["jogador-1"] = text[text.find('.')+2: point]
        if 'Assistência' in text:
            datas[key]['jogador-2'] = text[text.find('Assistência ')+15:-1]
        datas[key]['time'] = text[point+2:text.find(')')]
        descroption = text[text.find(')')+2:text.find('gol.')+3]
        if 'direito' in descroption:
            datas[key]['descricao'] = "pé direito"
        elif 'esquerdo' in descroption:
            datas[key]['descricao'] = "pé esquerdo"
        elif 'cabeça' in descroption:
            datas[key]['descricao'] = "cabeça"
        else:
            datas[key]['descricao'] = text[text.find(')')+2:text.find('gol.')+3]
        datas[key]['tipo'] = 'GOL'

    elif "Substituição" in text:
        point = text.find('substituindo')
        datas[key]['jogador-1'] = text[text.find('campo')+6:point-1]
        datas[key]['jogador-2'] = text[point+13:text.find('.', point)]
        datas[key]['time'] = text[13:text.find(',')]
        datas[key]['tipo'] = 'SUBSTITUICAO'

    elif "lesão" in text:
        point = text.find('(')
        datas[key]['jogador-1'] = text[text.find('lesão de')+9:point-1]
        datas[key]['time'] = text[point+1:text.find(')', point)]
        datas[key]['tipo'] = 'LESAO'

    elif "Fim do primeiro" in text:
        datas[key]['tipo'] = 'ENCERRAMENTO-1'

    elif "Fim do segundo" in text:
        datas[key]['tipo'] = 'ENCERRAMENTO-2'
    
    else:
        logging.warning(f'Non-standard comment')
        return
    
    return datas

def get_datas_from_comentarios(id: str) -> dict | None:
    '''Get the stats from a game by the page Comentarios'''

    if type(id) != str:
        logging.warning('ID must be a string')
        return None

    url = f'https://www.espn.com.br/futebol/comentario/_/jogoId/{id}'
    page = verify_page(url)

    if page is None:
        return None
    elif page.find_all('div', class_='Gamestrip__Score relative tc w-100 fw-heavy-900 h2 clr-gray-01') == []:
        # This is a way to check if the game was canceled, when there is no score
        logging.warning('Game canceled')
        return None

    # Getting comments
    minutes = page.find_all('div', class_='MatchCommentary__Comment__Timestamp')
    comments = page.find_all('div', class_='MatchCommentary__Comment__GameDetails')
    if len(minutes) != len(comments):
        logging.warning('Data inconsistency')
        return None
    
    bids = {
        'partida': id,
    } # Dictionary to store the data from comments

    for comment, minute in zip(comments, minutes):
        index = len(bids)
        data = get_data_from_comment(index, comment.text, minute.text)
        if data is not None:
            data['partida'] = id
            bids.update(data)
        # else:
        #     print(comment.text)
        
    return bids

def get_lineup(id: str) -> dict | None:
    '''Get the lineup from a game by the page Escalacoes'''

    if type(id) != str:
        logging.warning('ID must be a string')
        return None

    url = f'https://www.espn.com.br/futebol/escalacoes/_/jogoId/{id}'
    page = verify_page(url)
    
    if page is None:
        return None
    elif page.find_all('div', class_='Gamestrip__Score relative tc w-100 fw-heavy-900 h2 clr-gray-01') == []:
        # This is a way to check if the game was canceled, when there is no score
        logging.warning('Game canceled')
        return None
    
    logging.info(f'Getting lineup from {url}:')

    substitute = 'SoccerLineUpPlayer__Header SoccerLineUpPlayer__Header--subbedIn' # div
    starting_player = 'SoccerLineUpPlayer__Header' # div
    class_names = 'AnchorLink SoccerLineUpPlayer__Header__Name' # a

    # Getting the table with the components of the page
    aux = list(page.find_all('div', class_='ResponsiveTable LineUps__PlayersTable'))
    team1_component = aux[0]
    team2_component = aux[1]

    # Getting the names of the sunstitute players
    team1_substitute, team2_substitute = [], []
    substitutes1 = team1_component.find_all('div', class_=substitute)
    substitutes2 = team2_component.find_all('div', class_=substitute)
    for name1, name2 in zip(substitutes1, substitutes2):
        player1 = name1.find('a', class_=class_names)
        player2 = name2.find('a', class_=class_names)
        team1_substitute.append(player1['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0])
        team2_substitute.append(player2['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0])
    
    # Getting the names of the starting players
    team1_starting, team2_starting = [], []
    startings1 = team1_component.find_all('div', class_=starting_player)
    startings2 = team2_component.find_all('div', class_=starting_player)
    for name1, name2 in zip(startings1, startings2):
        player1 = name1.find('a', class_=class_names)['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0]
        player2 = name2.find('a', class_=class_names)['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0]
        if player1 not in team1_substitute:
            team1_starting.append(player1)
        if player2 not in team2_substitute:
            team2_starting.append(player2)
    
    # Getting the names of the reserve players
    team1_reserve, team2_reserve = [], []
    aux = page.find_all('div', class_='ResponsiveTable LineUps__SubstitutesTable')
    team1_component = aux[0]
    team2_component = aux[1]

    aux = team1_component.find_all('a', class_=class_names)
    team1_reserve = [player['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0] for player in aux]
    aux = team2_component.find_all('a', class_=class_names)
    team2_reserve = [player['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/', '').split('/')[0] for player in aux]

    # Finding team names
    aux = page.find_all('h2', class_='ScoreCell__TeamName ScoreCell__TeamName--displayName db')
    aux = [name.text for name in aux]
    
    team1, team2 = aux[0], aux[1]

    datas = {
        'partida': id,
        team1: {
            'titulares': team1_starting,
            'substitutos': team1_substitute,
            'reservas': team1_reserve
        },
        team2: {
            'titulares': team2_starting,
            'substitutos': team2_substitute,
            'reservas': team2_reserve
        }
    }
    return datas

def get_teams_id(temporada: int = 2024) -> list | None:
    '''Get the IDs of the teams from the table'''

    url = f'https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1/temporada/{temporada}'
    page = verify_page(url)
    if page is None:
        return None

    logging.info(f'Getting teams IDs from {url}:')

    aux = page.find_all('span', class_='hide-mobile')
    id = []
    for element in aux:
        id.append({
            element.text: element.find('a')['href'].replace('/futebol/time/_/id/','')
            })

    return id

def get_cast(id: str, season: int = 2024) -> dict | None:
    '''Get the cast of the team'''

    url = f'https://www.espn.com.br/futebol/time/elenco/_/id/{id}/liga/BRA.1/temporada/{season}'
    page = verify_page(url)

    if page is None:
        return None
    elif not page.find('h1', class_='Error404__Title') is None:
        logging.warning('Team not found')
        return None
    
    line_class = 'Table__TR Table__TR--sm Table__even' # tr
    column_class = 'Table__TD' # td
    class_names = 'AnchorLink' # a

    tags = {'A': 'ATACANTE', 'G': 'GOLEIRO', 'D': 'DEFENSOR', 'M':'MEIO-CAMPO'}
    
    players = []
    table = page.find_all('tr', class_=line_class)
    for line in table:
        player = line.find('a', class_=class_names).text
        espn_id = line.find('a', class_=class_names)['href'].replace('https://www.espn.com.br/futebol/jogador/_/id/','').split('/')[0]
        columns = line.find_all('td', class_=column_class)
        players.append({
            'nome': player,
            'espn_id': espn_id,
            'posicao': tags[columns[1].text] if columns[1].text in tags else None,
            'idade': columns[2].text if columns[2].text != '--' else None,
            'altura': columns[3].text if columns[3].text != '--' else None,
            'nacionalidade': columns[5].text if columns[5].text != '--' else None,
        })
    cast = {
        'time': id,
        'temporada': season,
        'jogadores': players
    }
    return cast