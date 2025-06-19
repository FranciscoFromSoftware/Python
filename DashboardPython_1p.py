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
import io
import urllib.request

# Configuração para usar a largura total da página
# Isso permite que a dashboard e seus elementos ocupem toda a largura da tela do navegador,
# proporcionando mais espaço horizontal para os gráficos e outros componentes.
st.set_page_config(layout="wide")

# Título principal da nossa dashboard
# Este título aparece no topo da página da dashboard, dando uma visão geral do seu propósito.
st.title("Dashboard de População")

# Texto abaixo do título
st.write("Dados de população por município ao longo dos anos.")

# URL da sua planilha do Google Sheets (formato CSV)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRajrcbWpLzBRpPAc4ffQba8yYwnyS7HaSmq98Hid9y8WBBW7nBJpyYkmHKMMoiDu4CvHv6v7Onm07/pub?output=csv"

# Lendo os dados diretamente do URL
try:
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    st.write("DataFrame carregado com sucesso!")
    st.dataframe(df.head())

    # Preenchendo os valores ausentes na coluna 'Ano' para baixo
    df['Ano'].fillna(method='ffill', inplace=True)

    # Separando Município e UF
    df[['Município', 'UF']] = df['Município'].str.rsplit('(', n=1, expand=True)
    df['UF'] = df['UF'].str.replace(')', '', regex=False).str.strip()
    df['Município'] = df['Município'].str.strip()

    # Exibindo o DataFrame tratado (para visualização no Streamlit)
    st.subheader("DataFrame Tratado")
    st.dataframe(df.head())

    # Agora você pode adicionar seus gráficos e métricas aqui usando o DataFrame 'df'

except urllib.error.URLError as e:
    st.error(f"Erro ao acessar a planilha: {e}")
except pd.errors.EmptyDataError:
    st.error("A planilha está vazia.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")

# Adicione aqui o código para criar seus gráficos e métricas usando o DataFrame 'df'
# Por exemplo:
# col1_grafico, col2_grafico, col3_grafico = st.columns(3)
# with col1_grafico:
#     st.subheader("População por Ano")
#     fig_pop_ano = px.line(df.groupby('Ano')['Pessoas'].sum().reset_index(), x='Ano', y='Pessoas')
#     st.plotly_chart(fig_pop_ano)


# Calculando métricas (apenas para exemplo)
total_frutas = df['quantidade'].sum()
maior_quantidade = df['quantidade'].max()
fruta_mais_popular = df.loc[df['quantidade'].idxmax(), 'fruta']

# Criando as colunas para os cards de métricas
card_col1, card_col2, card_col3, card_col4, card_col5, card_col6 = st.columns(6)

with card_col1:
    st.markdown(f"""
        <div style="background-color:#e6f2ff; padding:10px; border-radius:5px; height: 150px; width: 200px;">
            <h3>🍎 Total</h3>
            <h1>{total_frutas}</h1>
        </div>
    """, unsafe_allow_html=True)

with card_col2:
    st.markdown(f"""
        <div style="background-color:#ffe6e6; padding:10px; border-radius:5px; height: 150px; width: 200px; margin-right: 10px; margin-left: 10px; border: 1px solid #ff0000; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-size: 12px; align-items: center;">
            <h3>🏆 Popular</h3>
            <h1>{fruta_mais_popular}</h1>
            <p>{maior_quantidade} unidades</p>
        </div>
    """, unsafe_allow_html=True)

with card_col3:
    st.markdown(f"""
        <div style="background-color:#e6ffe6; padding:10px; border-radius:5px; margin-right: 10px; margin-left: 10px;height: 150px; width: 200px;">
            <h3 style = "font-size: 16px; color: #00c8ff;">📊 Média</h3>
            <h1>{fruta_mais_popular}</h1>
        </div>
    """, unsafe_allow_html=True)


# Dividindo a dashboard em três colunas para organizar os gráficos lado a lado
# A função st.columns(3) retorna três objetos de coluna que podem ser usados
# como contextos (com a instrução 'with') para posicionar elementos dentro de cada coluna.
col1, col2, col3 = st.columns(3)

# Bloco para o primeiro gráfico (barras) na primeira coluna
with col1: # Iniciando o bloco de código para a primeira coluna
    # Subtítulo para o primeiro gráfico, fornecendo um contexto específico para a visualização.
    st.subheader("Quantidade de Frutas")
    # Criando a figura e os eixos para o gráfico de barras usando Matplotlib
    # 'figsize=(8, 5)' define o tamanho da figura (largura=8 polegadas, altura=5 polegadas).
    # Ajustar esses valores pode alterar o tamanho do gráfico dentro da coluna.
    fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
    # Criando o gráfico de barras usando a biblioteca Seaborn, que é construída sobre o Matplotlib
    # 'x='fruta'' especifica a coluna do DataFrame a ser usada para o eixo horizontal.
    # 'y='quantidade'' especifica a coluna a ser usada para o eixo vertical.
    # 'data=df' indica o DataFrame de onde os dados vêm.
    # 'ax=ax_bar' associa o gráfico aos eixos criados anteriormente.
    sns.barplot(x='fruta', y='quantidade', data=df, ax=ax_bar)
    # Definindo o título do gráfico de barras com um tamanho de fonte específico.
    ax_bar.set_title('Quantidade de Frutas', fontsize=14)
    # Definindo o rótulo do eixo x (horizontal) com um tamanho de fonte específico.
    ax_bar.set_xlabel('Fruta', fontsize=12)
    # Definindo o rótulo do eixo y (vertical) com um tamanho de fonte específico.
    ax_bar.set_ylabel('Quantidade', fontsize=12)
    # Ajustando o tamanho da fonte dos rótulos dos ticks nos eixos x e y.
    ax_bar.tick_params(axis='both', which='major', labelsize=12)
    # Exibindo o gráfico de barras no Streamlit usando a figura Matplotlib criada.
    st.pyplot(fig_bar)

# Bloco para o segundo gráfico (pizza) na segunda coluna
with col2:
    # Subtítulo para o segundo gráfico, fornecendo contexto.
    st.subheader("Proporção de Frutas")
    # Criando a figura e os eixos para o gráfico de pizza usando Matplotlib.
    fig_pie, ax_pie = plt.subplots(figsize=(8, 5)) # Mesmo tamanho da figura para consistência
    # Criando o gráfico de pizza usando Matplotlib
    # 'df['quantidade']' são os valores que determinam o tamanho de cada fatia.
    # 'labels=df['fruta']' são os rótulos de texto para cada fatia.
    # 'autopct='%1.1f%%'' formata a porcentagem exibida em cada fatia com uma casa decimal.
    # 'startangle=90' rotaciona o ponto inicial do primeiro pedaço para o topo.
    # 'textprops={'fontsize': 12}' define o tamanho da fonte dos rótulos das porcentagens.
    ax_pie.pie(df['quantidade'], labels=df['fruta'], autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    # Garantindo que o gráfico de pizza seja desenhado como um círculo em vez de uma elipse.
    ax_pie.axis('equal')
    # Definindo o título do gráfico de pizza com um tamanho de fonte específico.
    ax_pie.set_title('Proporção de Frutas', fontsize=14)
    # Exibindo o gráfico de pizza no Streamlit usando a figura Matplotlib criada.
    st.pyplot(fig_pie)

# Terceira coluna (espaço reservado para o terceiro gráfico)
with col3:
    # Subtítulo para indicar o espaço reservado.
    st.subheader("Espaço para o Terceiro Gráfico")
    # Um texto simples explicando o propósito desta coluna.
    st.write("Aqui ficará o nosso terceiro gráfico.")

# Adicionando um texto simples abaixo dos gráficos, fornecendo um resumo ou legenda geral.
st.write("Dashboard mostrando a quantidade e a proporção de diferentes frutas.")

# --- Dicas e Melhorias ---

# 1. Interatividade:
#    - Considere adicionar interatividade aos seus gráficos usando bibliotecas como Plotly Express
#      (import plotly.express as px). O Plotly oferece gráficos interativos com tooltips, zoom, etc.
#    - Você pode usar widgets do Streamlit (como st.selectbox, st.slider) para permitir que os usuários
#      filtrem ou modifiquem os dados exibidos nos gráficos.

# 2. Mais visualizações:
#    - Explore outros tipos de gráficos que podem ser relevantes para seus dados, como gráficos de linha,
#      gráficos de dispersão (scatter plots), histogramas, etc.
#    - Se você adicionar mais dados (por exemplo, preço por fruta), um gráfico de dispersão de quantidade vs. preço
#      poderia ser interessante.

# 3. Organização e Layout:
#    - Para dashboards mais complexas, você pode usar mais linhas de colunas ou até mesmo o st.container()
#      para agrupar elementos relacionados.
#    - A biblioteca stx (Streamlit Extras) oferece componentes de layout mais avançados.

# 4. Estilo e Temas:
#    - O Streamlit tem temas embutidos que você pode configurar (nas configurações do Streamlit).
#    - Você também pode injetar CSS personalizado (com st.markdown e <style>) para um controle mais fino
#      sobre a aparência da sua dashboard.

# 5. Tratamento de Dados:
#    - Se seus dados vierem de fontes externas, implemente um bom tratamento de erros e atualizações
#      regulares dos dados. O Streamlit pode recarregar automaticamente quando o código é alterado.
#    - Para grandes conjuntos de dados, considere usar técnicas de otimização para garantir a performance da dashboard.

# 6. Responsividade:
#    - Teste sua dashboard em diferentes tamanhos de tela para garantir que o layout se adapte bem.
#      A largura total ajuda com isso, mas em layouts mais complexos, pode ser necessário ajustes.

# 7. Anotações e Explicações:
#    - Use st.markdown() para adicionar texto formatado, explicações ou anotações diretamente na sua
#      dashboard para guiar o usuário na interpretação dos gráficos.

# 8. Testes:
#    - À medida que sua dashboard cresce, considere adicionar testes para garantir que as visualizações
#      e a lógica dos dados funcionem como esperado.