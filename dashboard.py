import streamlit as st
import pandas as pd
from PIL import Image
import json
import yaml
import matplotlib.pyplot as plt


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


with tab2:
    st.title("Análise de Dados de Deputados")

    
    st.subheader("Insights Gerais:")
    try:
        with open("./data/insights_despesas_deputados.json", "r") as f:
            insights_despesas = json.load(f)
            for key, value in insights_despesas.items():
                st.write(f"{key}: {value}")
    except FileNotFoundError:
        st.error("Arquivo insights_despesas_deputados.json não encontrado.")


    st.subheader("Série Temporal de Despesas:")
    try:
        df_despesas = pd.read_parquet("./data/serie_despesas_diárias_deputados.parquet")
        deputados = df_despesas['nome'].unique()
        selected_deputado = st.selectbox("Selecione o Deputado:", deputados)

        df_deputado = df_despesas[df_despesas['nome'] == selected_deputado]
        df_deputado['data_documento'] = pd.to_datetime(df_deputado['data_documento'])
        df_deputado = df_deputado.sort_values('data_documento')

        fig, ax = plt.subplots(figsize=(10,6))
        ax.bar(df_deputado['data_documento'], df_deputado['valor_documento'])
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor")
        ax.set_title(f"Despesas do Deputado {selected_deputado}")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    except FileNotFoundError:
        st.error("Arquivo serie_despesas_diárias_deputados.parquet não encontrado.")
    except Exception as e:
        st.exception(e)


with tab3:
# Aba Proposições

    st.subheader("Dados das Proposições:")
    try:
        df_proposicoes = pd.read_parquet("./data/proposicoes_deputados.parquet")
        st.dataframe(df_proposicoes)
    except FileNotFoundError:
        st.error("Arquivo proposicoes_deputados.parquet não encontrado.")


    st.subheader("Sumarização das Proposições:")
    try:
        with open("./data/sumarizacao_proposicoes.json", "r") as f:
            sumarizacao_proposicoes = json.load(f)
            for key, value in sumarizacao_proposicoes.items():
                st.write(f"{key}: {value}")
    except FileNotFoundError:
        st.error("Arquivo sumarizacao_proposicoes.json não encontrado.")


    st.subheader("Assistente Virtual da Câmara dos Deputados")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Faça uma pergunta sobre a Câmara dos Deputados"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Create assistant response
        with st.chat_message("assistant"):
            response = """
            Como assistente especializado na Câmara dos Deputados, posso ajudar com:
            - Informações sobre proposições legislativas
            - Detalhes sobre deputados e partidos
            - Explicações sobre o processo legislativo
            - Análise de dados parlamentares

            Com base nos dados disponíveis, posso fornecer insights sobre:
            - {df_proposicoes.shape[0]} proposições registradas
            - Tendências legislativas
            - Atividade parlamentar
            """
            st.markdown(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

