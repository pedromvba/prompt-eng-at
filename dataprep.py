import requests
import pandas as pd


def deputados():

    root = 'https://dadosabertos.camara.leg.br/api/v2'
    response = requests.get(root+'/deputados', params={'dataInicio': '2024-08-01', 'dataFim': '2024-08-30'})
    deputados = pd.DataFrame().from_dict(response.json()['dados'])
    deputados.set_index('id', inplace=True)
    deputados.to_parquet('./data/deputados.parquet', index=True)

    print('Deputados Atualizados')

if __name__ == "__main__":
    deputados()
