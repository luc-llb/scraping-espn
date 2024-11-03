# Football Data Analysis

Para utilização desse material é necessário possuir instalado o Python (recomendada a versão 3.12.5 na qual o projeto foi feito) e uma ferramenta de banco de dados que suporte SQL (nesse projeto foi utilizado o MS SQL).

## Obtenção dos dados

Para obeter os dados que alimentaram o banco da dados, foi utilizado da tecnica de Web Scraping, que consiste em retirar o conteudo de interesse das paginass web, utilizando dos conteudos fornecidos em seu HTML.

Para isso, foi feito um script em python, que está no arquivo [getting_datas.py](/Scraping/getting_data.py), utilizado a biblioteca _BeautifulSoup_ com o modulo _request_ para obter as paginas.

Para a aplicação do scraping foi escolhido o site oficial da [ESPN](https://www.espn.com.br/futebol/), empresa que possui um grande nome no esporte. Além disso, outro motivo para a escolha desse site foi sua grande quantidade de informações sobre as partidas, juntamente a sua organização na distribuição dessas informações, o que facilita o processo da raspagem de dados.

Os dados contidos na pasta [Datas](./Datas/) são dos jogos que ocorreram entre a primeira rodada do Brasileirão (Série A) 2024, em 13/04/2024, até os jogos do dia 29/10/2024.
