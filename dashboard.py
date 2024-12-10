import streamlit as st
import pandas as pd
from PIL import Image
import json
import yaml


st.set_page_config(page_title="Dados Deputados", page_icon=":chart_with_upwards_trend:")

st.title("Dados da Câmara dos Deputados")


tab1, tab2, tab3 = st.tabs(["Overview", "Despesas", "Proposições"])

with tab1:
    st.title("Análise de Dados de Deputados da Câmara dos Deputados")

    st.markdown(
        """
        Esta aplicação Streamlit visa facilitar a análise de dados de deputados da Câmara dos Deputados.  
        Através de uma interface intuitiva, você poderá explorar informações relevantes sobre os parlamentares, 
        permitindo uma compreensão mais aprofundada do cenário político brasileiro.

        **Objetivo:**

        O principal objetivo desta aplicação é disponibilizar dados públicos de forma acessível e organizada, 
        facilitando a análise e a compreensão do trabalho dos deputados.  Isso contribui para a transparência e 
        o engajamento cívico, permitindo a população um melhor acompanhamento das atividades parlamentares.


        **Contexto:**

        Os dados utilizados nesta aplicação são provenientes de fontes públicas e oficiais da Câmara dos Deputados.  
        """)


    def load_overview_summary(filepath):
        """Carrega o resumo do arquivo YAML."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config.get('overview_summary', "Resumo não encontrado.")  # Retorna mensagem padrão se a chave não existir
        except FileNotFoundError:
            return "Arquivo de configuração não encontrado."
        except yaml.YAMLError as e:
            return f"Erro ao ler o arquivo YAML: {e}"

    overview_summary = load_overview_summary('./data/config.yaml')
    
    st.markdown("**Resumo da Câmara dos Deputados:**")
    st.markdown(overview_summary)

    st.markdown("**Distribuição de Deputados por Partido**")

    image = Image.open("./docs/distribuicao_deputados.png")
    st.image(image, caption="Distribuição de Deputados por Partido", use_column_width=True)



    def update_overview_tab(filepath="./data/insights_despesas_deputados.json"):
        """
        Lê o arquivo JSON, extrai os insights e atualiza a aba Overview.
        """
        with open(filepath, 'r', encoding='utf-8') as f:  # Encoding especificado para lidar com caracteres especiais
            data = json.load(f)
            insights = list(data.values())
        return insights  # Obtém todos os valores (insights) do dicionário
    
    insights = update_overview_tab()
    st.markdown("**Insights:**")
    st.write(insights)


# with tab2:
#     st.header("Despesas")
#     if not despesas_data.empty:
#         st.dataframe(despesas_data)
#     else:
#         st.write("Dados de despesas indisponíveis.")


# with tab3:
#     st.header("Proposições")
#     if not proposicoes_data.empty:
#         st.dataframe(proposicoes_data)
#     else:
#         st.write("Dados de proposições indisponíveis.")

