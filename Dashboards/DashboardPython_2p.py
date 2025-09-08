import streamlit as st
import pandas as pd
import plotly.express as px
import io
import urllib.request

# Configuração para usar a largura total da página
st.set_page_config(layout="wide")

# URLs das planilhas
url_populacao = "https://docs.google.com/spreadsheets/d/1yH6Rvo5V5WYEDMiB7ViSLTZWWOlmYMer/export?format=csv"
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

# Adicione o header com título e filtros lado a lado
cols_header = st.columns([0.4, 0.3, 0.3])
with cols_header[0]:
    st.markdown("<h2 style='font-size: 28px; font-weight: bold; color: #2E3B4E; text-align: left;'>Dashboard de População do Brasil</h2>", unsafe_allow_html=True)
with cols_header[1]:
    ano_selecionado = st.selectbox("Selecione o Ano", anos_disponiveis, index=len(anos_disponiveis) - 1)
with cols_header[2]:
    ufs_disponiveis = sorted(df_pop_completo['UF'].unique()) if df_pop_completo is not None else []
    uf_selecionada = st.selectbox("Selecione a UF", ["Todas"] + ufs_disponiveis)

# Adicionado para garantir que os dataframes foram carregados
if df_pop_completo is None or df_lat_lon_processed is None:
    st.warning("Não foi possível carregar os dados. O aplicativo não pode continuar.")
    st.stop()

# Adicionado para garantir que um ano foi selecionado
if ano_selecionado is None:
    st.warning("Nenhum ano disponível para seleção. O aplicativo não pode continuar.")
    st.stop()

# Container para o filtro e mapa
map_container = st.container()

with map_container:
    # Novo: aplicar filtro de UF nas medidas
    df_pop_completo_filtered = df_pop_completo if uf_selecionada == "Todas" else df_pop_completo[df_pop_completo['UF'] == uf_selecionada]
    
    # Filtrando os dados para o ano selecionado usando o dataset filtrado por UF
    df_pop_filtrado_ano = df_pop_completo_filtered[df_pop_completo_filtered['Ano'] == int(ano_selecionado)]
    
    # Cálculo das métricas filtradas pelo ano (usando o dataset filtrado por UF)
    total_populacao_ano = df_pop_filtrado_ano['Pessoas'].sum() if not df_pop_filtrado_ano.empty else 0

    crescimento_medio_anual_pct_ano = 0
    anos_para_media = sorted([ano for ano in anos_disponiveis if ano <= int(ano_selecionado)])
    if len(anos_para_media) > 1:
        df_pop_filtrado_ate_ano = df_pop_completo_filtered[df_pop_completo_filtered['Ano'].isin(anos_para_media)]
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
                df_crescimento_pct_ano_selecionado_df = df_pop_completo_filtered[df_pop_completo_filtered['Ano'].isin([ano_anterior_selecionado, int(ano_selecionado)])].pivot_table(
                    index=['Município', 'UF'], columns='Ano', values='Pessoas'
                ).reset_index()
                df_crescimento_pct_ano_selecionado_df = df_crescimento_pct_ano_selecionado_df[df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado] != 0].copy()
                if not df_crescimento_pct_ano_selecionado_df.empty:
                    df_crescimento_pct_ano_selecionado_df['Crescimento_Pct'] = ((df_crescimento_pct_ano_selecionado_df[int(ano_selecionado)] - df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado]) / df_crescimento_pct_ano_selecionado_df[ano_anterior_selecionado]) * 100
                    maior_crescimento_pct_row = df_crescimento_pct_ano_selecionado_df.nlargest(1, 'Crescimento_Pct')[['Município', 'Crescimento_Pct']].iloc[0]
                    maior_crescimento_pct_ano_selecionado = f"{maior_crescimento_pct_row['Município']} ({maior_crescimento_pct_row['Crescimento_Pct']:.2f}%)"
        except ValueError:
            pass

    maior_crescimento_medio_pct_ate_ano = "Sem dados"
    if len(anos_para_media) > 1:
        df_pop_filtrado_ate_ano_pivot = df_pop_completo_filtered[df_pop_completo_filtered['Ano'].isin(anos_para_media)].pivot_table(
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
            maior_crescimento_medio_ate_ano_row = df_pop_filtrado_ate_ano_pivot.nlargest(1, 'Crescimento_Medio_Pct')[['Município', 'Crescimento_Medio_Pct']].iloc[0]
            if maior_crescimento_medio_ate_ano_row is not None:
                maior_crescimento_medio_pct_ate_ano = f"{maior_crescimento_medio_ate_ano_row['Município']} ({maior_crescimento_medio_ate_ano_row['Crescimento_Medio_Pct']:.2f}%)"

    # Exibição dos cards estilizados
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(to right, #024053, #499c70);
                        color: white; height: 100px; 
                        padding: 15px; border-radius: 5px;
                        display: flex; flex-direction: column; justify-content: left;
                        align-items: left; text-align: left;'>
                <h3 style='font-size: 0.7em; margin-bottom: 0px;'>População Total ({ano_selecionado})</h3>
                <p style='font-size: 1.1em; margin-top: -1;'>{total_populacao_ano:,.0f}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(to right,  #024053, #499c70);
                        color: white; height: 100px;
                        padding: 15px; border-radius: 5px;
                        display: flex; flex-direction: column; justify-content: left;
                        align-items: left; text-align: left;'>
                <h3 style='font-size: 0.7em; margin-bottom: 0px;'>Cresc. Médio Anual (até {ano_selecionado})</h3>
                <p style='font-size: 1.1rem; margin-top: -1;'>{crescimento_medio_anual_pct_ano:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(to right,  #024053, #499c70);
                        color: white; height: 100px; 
                        padding: 15px; border-radius: 5px;
                        display: flex; flex-direction: column; justify-content: left;
                        align-items: left; text-align: left;'>
                <h3 style='font-size: 0.7em; margin-bottom: 0px;'>Maior Cresc. (%) ({ano_selecionado} vs {ano_anterior_selecionado if ano_anterior_selecionado else 'anterior'})</h3>
                <p style='font-size: 80%; margin-top: -1;'>{maior_crescimento_pct_ano_selecionado}</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(to right,  #024053, #499c70);
                        color: white; height: 100px; 
                        padding: 15px; border-radius: 5px;
                        display: flex; flex-direction: column; justify-content: left;
                        align-items: left; text-align: left;'>
                <h3 style='font-size: 0.7em; margin-bottom: 0px;'>Maior Cresc. Médio (%) (até {ano_selecionado})</h3>
                <p style='font-size: 80%; margin-top: 0;'>{maior_crescimento_medio_pct_ate_ano}</p>
            </div>
        """, unsafe_allow_html=True)

    # Processamento dos dados de população para o ano selecionado para o mapa
    df_pop_filtrado_mapa = df_pop_completo[df_pop_completo['Ano'] == int(ano_selecionado)][['Município', 'UF', 'Pessoas']].copy()
    df_pop_filtrado_mapa['MergeKey'] = df_pop_filtrado_mapa['Município'] + ' ' + df_pop_filtrado_mapa['UF']

    # Merge dos DataFrames para o mapa
    df_map_data = None
    if df_pop_filtrado_mapa is not None and df_lat_lon_processed is not None:
        df_map_data = pd.merge(df_lat_lon_processed, df_pop_filtrado_mapa[['MergeKey', 'Pessoas']], on='MergeKey', how='left')

        # Novo: Filtrar por UF, se selecionado
        if uf_selecionada != "Todas":
            df_map_data = df_map_data[df_map_data['UF'] == uf_selecionada]

        # Converter 'Latitude' e 'Longitude' para numérico ANTES de plotar
        if df_map_data is not None:
            df_map_data.dropna(subset=['Pessoas'], inplace=True) # Remove linhas sem dados de população
            df_map_data['Latitude'] = pd.to_numeric(df_map_data['Latitude'], errors='coerce')
            df_map_data['Longitude'] = pd.to_numeric(df_map_data['Longitude'], errors='coerce')

            if not df_map_data.empty:
                st.markdown(f"""
                    <div style="background: linear-gradient(to right,  #fcbb45, #1c6144); color: #2E3B4E; font-size: 16px; padding: 5px; border-radius: 5px; text-align: left; width: 35%; margin-top: 20px; margin-bottom: 10px;">
                        Mapa Atualizado da População - Ano {ano_selecionado}
                    </div>
                """, unsafe_allow_html=True)
                fig_map = px.scatter_mapbox(
                    df_map_data,
                    lat="Latitude",
                    lon="Longitude",
                    size="Pessoas",
                    color="Pessoas",
                    hover_name="Município",
                    hover_data={'Pessoas': ':,.0f', 'Latitude': True, 'Longitude': True},
                    color_continuous_scale='Viridis',
                    range_color=[0, 2000000],  # Escala ajustada para cidades com até 2 milhões
                    size_max=50,
                    zoom=3.5,
                    height=600
                )
                fig_map.update_layout(
                    mapbox={
                        "style": "carto-darkmatter",
                        "center": {"lat": -15.79, "lon": -47.88},
                        "zoom": 3.5,
                        "pitch": 45,
                        "bearing": 0
                    },
                    margin={"r": 0, "t": 0, "l": 0, "b": 0}
                )
                st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})

