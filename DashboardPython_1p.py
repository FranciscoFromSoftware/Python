## Dashboard Python com Streamlit
# Este é um exemplo básico de como criar uma dashboard.
# Vamos usar o Streamlit, uma biblioteca Python que facilita a criação de aplicações web interativas.
# Cadastro no site: https://streamlit.io/ e instalação do Streamlit: pip install streamlit
# Para executar o código, salve-o em um arquivo .py e envie para o gitHub
# Depois crie um app no Streamlit Cloud e faça o upload do arquivo .py do gitHub.
# O Streamlit Cloud irá gerar um link para você acessar a dashboard online.
# Você também pode executar o código localmente, mas precisará instalar o Streamlit e suas dependências.
# Recomendo usar um ambiente virtual para evitar conflitos de dependências.
# Para criar um ambiente virtual, use o comando: python -m venv nome_do_ambiente
# Para executar o código localmente, use o comando: python -m streamlit run nome_do_arquivo.py


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Título da nossa dashboard
st.title("Minha Primeira Dashboard Streamlit")

# Criando um DataFrame de exemplo
data = {'fruta': ['Maçã', 'Banana', 'Laranja', 'Uva'],
        'quantidade': [10, 15, 7, 12]}
df = pd.DataFrame(data)

# Dividindo a dashboard em duas colunas para organizar os gráficos lado a lado
col1, col2 = st.columns(2)

# Bloco para o primeiro gráfico (barras) na primeira coluna
with col1:
    # Subtítulo para o primeiro gráfico
    st.subheader("Quantidade de Frutas")
    # Criando a figura e os eixos para o gráfico Matplotlib/Seaborn
    fig_bar, ax_bar = plt.subplots()
    # Criando o gráfico de barras usando Seaborn
    # 'x' representa a coluna 'fruta' no eixo horizontal
    # 'y' representa a coluna 'quantidade' no eixo vertical
    # 'data=df' especifica o DataFrame a ser usado
    # 'ax=ax_bar' associa o gráfico aos eixos criados
    sns.barplot(x='fruta', y='quantidade', data=df, ax=ax_bar)
    # Definindo o título do gráfico
    ax_bar.set_title('Quantidade de Frutas')
    # Definindo o rótulo do eixo x
    ax_bar.set_xlabel('Fruta')
    # Definindo o rótulo do eixo y
    ax_bar.set_ylabel('Quantidade')
    # Exibindo o gráfico no Streamlit usando a figura criada com Matplotlib
    st.pyplot(fig_bar)

# Bloco para o segundo gráfico (pizza) na segunda coluna
with col2:
    # Subtítulo para o segundo gráfico
    st.subheader("Proporção de Frutas")
    # Criando a figura e os eixos para o gráfico Matplotlib
    fig_pie, ax_pie = plt.subplots()
    # Criando o gráfico de pizza usando Matplotlib
    # 'df['quantidade']' são os valores das fatias
    # 'labels=df['fruta']' são os rótulos de cada fatia
    # 'autopct='%1.1f%%'' formata a exibição das porcentagens nas fatias
    # 'startangle=90' rotaciona o início do primeiro pedaço em 90 graus (vertical)
    ax_pie.pie(df['quantidade'], labels=df['fruta'], autopct='%1.1f%%', startangle=90)
    # Garantindo que o gráfico de pizza seja um círculo e não uma elipse
    ax_pie.axis('equal')
    # Exibindo o gráfico de pizza no Streamlit usando a figura criada com Matplotlib
    st.pyplot(fig_pie)

# Adicionando um texto simples abaixo dos gráficos
st.write("Esta dashboard agora exibe os gráficos lado a lado com explicações no código!")