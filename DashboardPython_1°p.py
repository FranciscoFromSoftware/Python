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

# Criando um gráfico de barras com Matplotlib e Seaborn
fig, ax = plt.subplots()
sns.barplot(x='fruta', y='quantidade', data=df, ax=ax)
ax.set_title('Quantidade de Frutas')
ax.set_xlabel('Fruta')
ax.set_ylabel('Quantidade')

# Exibindo o gráfico no Streamlit
st.pyplot(fig)

# Adicionando um texto simples
st.write("Esta é uma dashboard muito simples, mas é o começo!")