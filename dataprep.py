import requests
import pandas as pd


def deputados():

    root = 'https://dadosabertos.camara.leg.br/api/v2'
    response = requests.get(root+'/deputados', params={'dataInicio': '2024-08-01', 'dataFim': '2024-08-30'})
    deputados = pd.DataFrame().from_dict(response.json()['dados'])
    deputados.set_index('id', inplace=True)
    deputados.to_parquet('./data/deputados.parquet', index=True)

    print('Deputados Atualizados')
    return deputados

def despesas_deputados():

    root = 'https://dadosabertos.camara.leg.br/api/v2'
    response = requests.get(root+'/deputados', params={'dataInicio': '2024-08-01', 'dataFim': '2024-08-30'})
    deputados = pd.DataFrame().from_dict(response.json()['dados'])

    lista_despesas = []

    for _, deputado in deputados.iterrows():
        id = deputado['id']
        nome = deputado['nome']
        despesas = requests.get(f'{root}/deputados/{id}/despesas').json()['dados']

        for despesa in despesas:

            tipo_despesa = despesa.get("tipoDespesa", "Não informado")
            valor_documento = despesa.get("valorDocumento", 0.0)
            data_documento = despesa.get("dataDocumento", "Não informado")

            lista_despesas.append({
                "id": id,
                "nome": nome,
                "tipo_despesa": tipo_despesa,
                "valor_documento": valor_documento,
                "data_documento": data_documento
            })

    df_despesas = pd.DataFrame(lista_despesas)
    df_despesas.to_parquet('./data/serie_despesas_diárias_deputados.parquet', index=False)
    print('Despesas Atualizadas')
    return df_despesas

def proposicoes():

    proposicoes = pd.DataFrame()

    for cod in [40, 46, 62]:

        root = 'https://dadosabertos.camara.leg.br/api/v2'
        response = requests.get(root+'/proposicoes', 
                                params={'dataInicio': '2024-08-01', 
                                        'dataFim': '2024-08-30',
                                        'codTema': cod,
                                        'itens': 10,})
        prop = pd.DataFrame().from_dict(response.json()['dados'])
        prop['tema'] = "Economia" if cod == 40 else "Educação" if cod == 46 else "Ciência, Tecnologia e Inovação"
        proposicoes = pd.concat([proposicoes, prop])
    
        proposicoes.to_parquet('./data/proposicoes_deputados.parquet', index=False)
    
    print('Proposicoes Atualizadas')    

    return proposicoes


if __name__ == "__main__":
    proposicoes()
