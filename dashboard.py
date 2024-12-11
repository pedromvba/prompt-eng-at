import streamlit as st
import pandas as pd
from PIL import Image
import json
import yaml
import matplotlib.pyplot as plt
import faiss
import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from llm_database import *
import time
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai


#loading api key
load_dotenv('.env')


st.set_page_config(page_title="Dados Deputados", page_icon=":chart_with_upwards_trend:")

st.title("Dados da Câmara dos Deputados")


tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Despesas", "Proposições", "Chatbot"])

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




with tab4:
        st.title("Chatbot Câmara dos Deputados")

        # Carga da base FAISS
        despesas = pd.read_parquet('./data/serie_despesas_diárias_deputados.parquet')
        despesas_texto = despesas.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in despesas.columns]),
                                        axis=1).tolist()

        deputados = pd.read_parquet('./data/deputados.parquet')
        deputados_texto = deputados.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in deputados.columns]),
                                        axis=1).tolist()

        proposicoes = pd.read_parquet('./data/proposicoes_deputados.parquet')
        proposicoes_texto = proposicoes.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in proposicoes.columns]),
                                        axis=1).tolist()

        despesas_medias = pd.read_csv('./data/despesa_média_por_tipo_de_despesa.csv')
        despesas_medias_texto = despesas_medias.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in despesas_medias.columns]),
                                        axis=1).tolist()

        despesa_total_por_deputado = pd.read_csv('./data/despesa_total_por_deputado.csv')
        despesa_total_por_deputado_texto = despesa_total_por_deputado.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in despesa_total_por_deputado.columns]),
                                        axis=1).tolist()

        dados = despesas_texto + deputados_texto + proposicoes_texto + despesas_medias_texto + despesa_total_por_deputado_texto

        # model definitions
        model_name = 'neuralmind/bert-base-portuguese-cased'
        llm_model_dir = './data/neuralMind/'
        embedding_model = SentenceTransformer(
            model_name, 
            cache_folder=llm_model_dir
        )

        # embedding texts
        embeddings_dados = embedding_model.encode(dados)
        embeddings_dados = np.array(embeddings_dados).astype("float32")

        #creating faiss index
        d = embeddings_dados.shape[1]  # embedding dimension
        index = faiss.IndexFlatL2(d)  # using l2 distance as metric
        index.add(embeddings_dados) # adding embeddings to index


        user_prompt = st.chat_input("Hi")
        if user_prompt is not None:
            # Display user message in chat message container
            st.chat_message("user").markdown(user_prompt)
            # RAG para a base de conhecimento

            query_embedding = embedding_model.encode([user_prompt]).astype("float32")
            k=100
            distances, indices = index.search(query_embedding, k) 

            
            db_text = '\n'.join([f"- {dados[indices[0][i]]}" for i in range(k)])

      

            llm_prompt = f"""

            Responda a <pergunta do usuário> considerando as informações disponíveis no banco de dados <database>
            Leia várias linhas do banco de dados para entender o contexto e fornecer uma resposta relevante.

            ##
            <pergunta do usuário>
            {user_prompt}

            ##
            <database>
            {db_text}

            """

            genai.configure(api_key=os.environ["GEMINI_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(llm_prompt)
            response = response.text

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)


