import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib.request
import plotly.express as px  # Importando Plotly Express para gráficos interativos

# Configuração para usar a largura total da página
st.set_page_config(layout="wide")

# Título principal da nossa dashboard
st.title("Dashboard de População")

# Texto abaixo do título
st.write("Visão geral das métricas e visualizações da população por município ao longo dos anos.")

# URL da sua planilha do Google Sheets (formato CSV)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRajrcbWpLzBRpPAc4ffQba8yYwnyS7HaSmq98Hid9y8WBBW7nBJpyYkmHKMMoiDu4CvHv6v7Onm07/pub?output=csv"

# Lendo os dados diretamente do URL
try:
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    df = pd.read_csv(io.StringIO(data))

    # Preenchendo os valores ausentes na coluna 'Ano' para baixo
    df['Ano'] = df['Ano'].ffill()

    # Separando Município e UF
    df[['Município', 'UF']] = df['Município'].str.rsplit('(', n=1, expand=True)
    df['UF'] = df['UF'].str.replace(')', '', regex=False).str.strip()
    df['Município'] = df['Município'].str.strip()

    # Calculando métricas de população
    total_populacao = df['Pessoas'].sum()
    maior_populacao = df['Pessoas'].max()
    municipio_mais_populoso = df.loc[df['Pessoas'].idxmax(), 'Município']
    media_populacao = df['Pessoas'].mean()
    ano_mais_recente = df['Ano'].max()
    municipio_mais_antigo = df.loc[df['Ano'].idxmin(), 'Município']
    total_municipios = df['Município'].nunique()

    # Criando as colunas para os cards de métricas
    card_col1, card_col2, card_col3, card_col4, card_col5, card_col6 = st.columns(6)

    with card_col1:
        st.metric("Total População", f"{total_populacao:,}")

    with card_col2:
        st.metric("Maior População", municipio_mais_populoso, f"{maior_populacao:,} pessoas")

    with card_col3:
        st.metric("Média População", f"{media_populacao:,.2f}")

    with card_col4:
        st.metric("Ano Mais Recente", ano_mais_recente)

    with card_col5:
        st.metric("Município Mais Antigo (Primeiro Registro)", municipio_mais_antigo)

    with card_col6:
        st.metric("Total Municípios", total_municipios)

    # Dividindo a dashboard em três colunas para organizar os gráficos lado a lado
    col1, col2, col3 = st.columns(3)

    # Bloco para o primeiro gráfico (barras) na primeira coluna
    with col1:
        st.subheader(f"Top 10 Municípios Mais Populosos em {ano_mais_recente}")
        df_ano_recente = df[df['Ano'] == ano_mais_recente].sort_values(by='Pessoas', ascending=False).head(10)
        fig_bar = px.bar(df_ano_recente, x='Município', y='Pessoas',
                         title=f'Top 10 em {ano_mais_recente}',
                         labels={'Pessoas': 'População'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # Bloco para o segundo gráfico (linha) na segunda coluna
    with col2:
        st.subheader("Evolução da População Total ao Longo dos Anos")
        df_pop_ano = df.groupby('Ano')['Pessoas'].sum().reset_index()
        fig_line = px.line(df_pop_ano, x='Ano', y='Pessoas',
                          title='Evolução Total',
                          labels={'Pessoas': 'População Total', 'Ano': 'Ano'})
        st.plotly_chart(fig_line, use_container_width=True)

    # Terceira coluna (gráfico de barras para população por UF no ano mais recente)
    with col3:
        st.subheader(f"População por UF em {ano_mais_recente}")
        df_pop_uf = df[df['Ano'] == ano_mais_recente].groupby('UF')['Pessoas'].sum().reset_index().sort_values(by='Pessoas', ascending=False)
        fig_bar_uf = px.bar(df_pop_uf, x='UF', y='Pessoas',
                             title=f'Por UF em {ano_mais_recente}',
                             labels={'Pessoas': 'População Total', 'UF': 'Unidade Federativa'})
        st.plotly_chart(fig_bar_uf, use_container_width=True)

    # Adicionando um texto simples abaixo dos gráficos
    st.write("Fonte dos dados: Elaborado a partir da planilha fornecida.")

except urllib.error.URLError as e:
    st.error(f"Erro ao acessar a planilha: {e}")
except pd.errors.EmptyDataError:
    st.error("A planilha está vazia.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")