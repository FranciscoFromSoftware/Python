import streamlit as st
import pandas as pd
import plotly.express as px
import io
import urllib.request

# Configuração para usar a largura total da página
st.set_page_config(layout="wide")

# Título principal da nossa dashboard
st.title("Dashboard de População com Localização")

# Texto abaixo do título
st.write("Visão geral das métricas e visualizações da população por município com informações de localização.")

# URLs das planilhas
url_populacao = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRajrcbWpLzBRpPAc4ffQba8yYwnyS7HaSmq98Hid9y8WBBW7nBJpyYkmHKMMoiDu4CvHv6v7Onm07/pub?output=csv"
url_lat_lon = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRns5zrdUDwA4__xZCSoEquLiktvp-1DgDlbl9WxW9eKtuBk7ef6fQcPzVmhw305wST8iGJxksAi6U0/pub?gid=1077836227&single=true&output=csv"

# Função para carregar dados com caching
@st.cache_data
def load_data(url):
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(data))
        return df
    except urllib.error.URLError as e:
        st.error(f"Erro ao acessar a planilha: {e}")
        return None
    except pd.errors.EmptyDataError:
        st.error("A planilha está vazia.")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None

def clean_text(text):
    text = text.str.lower().str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8').str.strip()
    return text

# Carregando os dados
df_pop_raw = load_data(url_populacao)
df_lat_lon = load_data(url_lat_lon)

# Processamento dos dados de população
anos_disponiveis = []
df_pop_completo = None
if df_pop_raw is not None:
    df_pop_completo = df_pop_raw.copy()
    df_pop_completo['Ano'] = df_pop_completo['Ano'].ffill().astype(int)
    df_pop_completo[['Município', 'UF']] = df_pop_completo['Município'].str.rsplit('(', n=1, expand=True)
    df_pop_completo['UF'] = df_pop_completo['UF'].str.replace(')', '', regex=False).str.strip()
    df_pop_completo['Município'] = clean_text(df_pop_completo['Município'])
    df_pop_completo['Pessoas'] = pd.to_numeric(df_pop_completo['Pessoas'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).astype(int)
    anos_disponiveis = sorted(df_pop_completo['Ano'].unique())

# Processamento dos dados de latitude e longitude
df_lat_lon_processed = None
if df_lat_lon is not None:
    df_lat_lon_processed = df_lat_lon[['Município', 'UF', 'Latitude', 'Longitude']].copy()
    df_lat_lon_processed['Município'] = clean_text(df_lat_lon_processed['Município'])
    df_lat_lon_processed['MergeKey'] = df_lat_lon_processed['Município'] + ' ' + df_lat_lon_processed['UF']

# Container para o filtro e mapa
map_container = st.container()

with map_container:
    st.subheader("Mapa da População por Município")

    # Define o tamanho do selectbox com base no número de anos
    num_anos = len(anos_disponiveis)
    largura_relativa = min(num_anos * 0.05, 0.8)  # Ajuste o fator 0.05 conforme necessário
    col_filtro = st.columns([largura_relativa, 1 - largura_relativa])[0]

    with col_filtro:
        ano_selecionado = st.selectbox("Selecione o Ano", anos_disponiveis, index=len(anos_disponiveis) - 1)

    # Filtrando os dados para o ano selecionado
    df_pop_filtrado_ano = df_pop_completo[df_pop_completo['Ano'] == int(ano_selecionado)]

    # Cálculo das métricas filtradas pelo ano
    total_populacao_ano = df_pop_filtrado_ano['Pessoas'].sum() if not df_pop_filtrado_ano.empty else 0

    crescimento_medio_anual_pct_ano = 0
    anos_para_media = sorted([ano for ano in anos_disponiveis if ano <= int(ano_selecionado)])
    if len(anos_para_media) > 1:
        df_pop_filtrado_ate_ano = df_pop_completo[df_pop_completo['Ano'].isin(anos_para_media)]
        df_pop_pivot_ano = df_pop_filtrado_ate_ano.pivot_table(index=['Município', 'UF'], columns='Ano', values='Pessoas').reset_index()
        df_pop_pivot_ano['Crescimento_Pct'] = 0.0
        for i in range(len(anos_para_media) - 1):
            ano_atual = anos_para_media[i+1]
            ano_anterior = anos_para_media[i]
            df_pop_pivot_ano = df_pop_pivot_ano[df_pop_pivot_ano[ano_anterior] != 0].copy()
            if not df_pop_pivot_ano.empty:
                df_pop_pivot_ano['Cresc_Ano_Pct'] = ((df_pop_pivot_ano[ano_atual] - df_pop_pivot_ano[ano_anterior]) / df_pop_pivot_ano[ano_anterior]) * 100
                df_pop_pivot_ano['Crescimento_Pct'] += df_pop_pivot_ano['Cresc_Ano_Pct']
        crescimento_medio_anual_pct_ano = (df_pop_pivot_ano['Crescimento_Pct'].mean() / (len(anos_para_media) - 1)) if (len(anos_para_media) - 1) > 0 and not df_pop_pivot_ano['Crescimento_Pct'].empty else 0

    maior_crescimento_pct_ano_selecionado = "Sem dados"
    if len(anos_disponiveis) > 1:
        ano_anterior_selecionado = None
        anos_ordenados = sorted(anos_disponiveis)
        try:
            index_ano_selecionado = anos_ordenados.index(int(ano_selecionado))
            if index_ano_selecionado > 0:
                ano_anterior_selecionado = anos_ordenados[index_ano_selecionado - 1]
                df_crescimento_pct_ano_selecionado_df = df_pop_completo[df_pop_completo['Ano'].isin([ano_anterior_selecionado, int(ano_selecionado)])].pivot_table(
                    index=['Município', 'UF'], columns='Ano', values='Pessoas'
                ).reset_index()
                df_crescimento_pct_ano_selecionado_df = df_crescimento_pct_ano_selecionado_df[df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado] != 0].copy()
                if not df_crescimento_pct_ano_selecionado_df.empty:
                    df_crescimento_pct_ano_selecionado_df['Crescimento_Pct'] = ((df_crescimento_pct_ano_selecionado_df[int(ano_selecionado)] - df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado]) / df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado]) * 100
                    maior_crescimento_pct_row = df_crescimento_pct_ano_selecionado_df.nlargest(1, 'Crescimento_Pct')[['Município', 'Crescimento_Pct']].iloc[0]
                    maior_crescimento_pct_ano_selecionado = f"{maior_crescimento_pct_row['Município']} ({maior_crescimento_pct_row['Crescimento_Pct']:.2f}%)"
        except ValueError:
            pass

    # Cálculo do maior crescimento médio percentual ATÉ o ano selecionado
    maior_crescimento_medio_pct_ate_ano = "Sem dados"
    if len(anos_para_media) > 1:
        df_pop_filtrado_ate_ano_pivot = df_pop_completo[df_pop_completo['Ano'].isin(anos_para_media)].pivot_table(
            index=['Município', 'UF'], columns='Ano', values='Pessoas'
        ).reset_index()
        df_pop_filtrado_ate_ano_pivot['Crescimento_Acumulado_Pct'] = 0.0
        for i in range(len(anos_para_media) - 1):
            ano_atual = anos_para_media[i+1]
            ano_anterior = anos_para_media[i]
            df_pop_filtrado_ate_ano_pivot = df_pop_filtrado_ate_ano_pivot[df_pop_filtrado_ate_ano_pivot[ano_anterior] != 0].copy()
            if not df_pop_filtrado_ate_ano_pivot.empty:
                df_pop_filtrado_ate_ano_pivot['Cresc_Ano_Pct'] = ((df_pop_filtrado_ate_ano_pivot[ano_atual] - df_pop_filtrado_ate_ano_pivot[ano_anterior]) / df_pop_filtrado_ate_ano_pivot[ano_anterior]) * 100
                df_pop_filtrado_ate_ano_pivot['Crescimento_Acumulado_Pct'] += df_pop_filtrado_ate_ano_pivot['Cresc_Ano_Pct']

        df_pop_filtrado_ate_ano_pivot['Crescimento_Medio_Pct'] = df_pop_filtrado_ate_ano_pivot['Crescimento_Acumulado_Pct'] / (len(anos_para_media) - 1) if (len(anos_para_media) - 1) > 0 else 0
        if not df_pop_filtrado_ate_ano_pivot.empty and not df_pop_filtrado_ate_ano_pivot['Crescimento_Medio_Pct'].empty:
            maior_crescimento_medio_ate_ano_row = df_pop_filtrado_ate_ano_pivot.nlargest(1, 'Crescimento_Medio_Pct')[['Município', 'Crescimento_Medio_Pct']].iloc[0] if not df_pop_filtrado_ate_ano_pivot.empty else None
            if maior_crescimento_medio_ate_ano_row is not None:
                maior_crescimento_medio_pct_ate_ano = f"{maior_crescimento_medio_ate_ano_row['Município']} ({maior_crescimento_medio_ate_ano_row['Crescimento_Medio_Pct']:.2f}%)"

    # Exibição dos cards estilizados
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(to right, #1e3a8a, #047a60); color: white; padding: 15px; border-radius: 5px;'>
                <h3 style='font-size: 1em; margin-bottom: 5px;'>População Total ({ano_selecionado})</h3>
                <p style='font-size: 1.2em; margin-top: 0;'>{total_populacao_ano:,.0f}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(to right, #1e3a8a, #047a60); color: white; padding: 15px; border-radius: 5px;'>
                <h3 style='font-size: 1em; margin-bottom: 5px;'>Cresc. Médio Anual (até {ano_selecionado})</h3>
                <p style='font-size: 1.2em; margin-top: 0;'>{crescimento_medio_anual_pct_ano:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(to right, #1e3a8a, #047a60); color: white; padding: 15px; border-radius: 5px;'>
                <h3 style='font-size: 0.9em; margin-bottom: 5px;'>Maior Cresc. (%) ({ano_selecionado} vs {ano_anterior_selecionado if ano_anterior_selecionado else 'anterior'})</h3>
                <p style='font-size: 1.1em; margin-top: 0;'>{maior_crescimento_pct_ano_selecionado}</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(to right, #1e3a8a, #047a60); color: white; padding: 15px; border-radius: 5px;'>
                <h3 style='font-size: 0.9em; margin-bottom: 5px;'>Maior Cresc. Médio (%) (até {ano_selecionado})</h3>
                <p style='font-size: 1.1em; margin-top: 0;'>{maior_crescimento_medio_pct_ate_ano}</p>
            </div>
        """, unsafe_allow_html=True)

    # Processamento dos dados de população para o ano selecionado para o mapa
    df_pop_filtrado_mapa = df_pop_completo[df_pop_completo['Ano'] == int(ano_selecionado)][['Município', 'UF', 'Pessoas']].copy()
    df_pop_filtrado_mapa['MergeKey'] = df_pop_filtrado_mapa['Município'] + ' ' + df_pop_filtrado_mapa['UF']

    # Merge dos DataFrames para o mapa
    df_map_data = None
    if df_pop_filtrado_mapa is not None and df_lat_lon_processed is not None:
        df_map_data = pd.merge(df_lat_lon_processed, df_pop_filtrado_mapa[['MergeKey', 'Pessoas']], on='MergeKey', how='left')

        # Converter 'Latitude' e 'Longitude' para numérico ANTES de plotar
        if df_map_data is not None:
            df_map_data['Latitude'] = pd.to_numeric(df_map_data['Latitude'], errors='coerce')
            df_map_data['Longitude'] = pd.to_numeric(df_map_data['Longitude'], errors='coerce')

            if not df_map_data.empty:
                st.subheader(f"Mapa da População por Município em {ano_selecionado}")
                fig_map = px.scatter_mapbox(df_map_data,
                                            lat="Latitude",
                                            lon="Longitude",
                                            size="Pessoas",
                                            color="Pessoas",
                                            hover_name="Município",
                                            hover_data={'Pessoas': ':,.0f', 'Latitude': True, 'Longitude': True},
                                            color_continuous_scale='magma',
                                            size_max=22,
                                            zoom=3.5,
                                            height=600)
                fig_map.update_layout(mapbox_style="carto-darkmatter",
                                      margin={"r": 0, "t": 30, "l": 0, "b": 0})
                st.plotly_chart(fig_map, use_container_width=True)
            
