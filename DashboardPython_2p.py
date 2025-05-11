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

# Processamento dos dados de população para 2021
df_pop_2021 = None
if df_pop_raw is not None:
    df_pop = df_pop_raw.copy()
    df_pop['Ano'] = df_pop['Ano'].ffill()
    df_pop[['Município', 'UF']] = df_pop['Município'].str.rsplit('(', n=1, expand=True)
    df_pop['UF'] = df_pop['UF'].str.replace(')', '', regex=False).str.strip()
    df_pop['Município'] = clean_text(df_pop['Município'])
    df_pop['Pessoas'] = pd.to_numeric(df_pop['Pessoas'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).astype(int)
    df_pop_2021 = df_pop[df_pop['Ano'] == 2021][['Município', 'UF', 'Pessoas']].copy()
    df_pop_2021['MergeKey'] = df_pop_2021['Município'] + ' ' + df_pop_2021['UF']

# Processamento dos dados de latitude e longitude
df_lat_lon_processed = None
if df_lat_lon is not None:
    df_lat_lon_processed = df_lat_lon[['Município', 'UF', 'Latitude', 'Longitude']].copy()
    df_lat_lon_processed['Município'] = clean_text(df_lat_lon_processed['Município'])
    df_lat_lon_processed['MergeKey'] = df_lat_lon_processed['Município'] + ' ' + df_lat_lon_processed['UF']

    # Merge dos DataFrames (mantendo todos os municípios do df_lat_lon)
    if df_pop_2021 is not None:
        df_map_data = pd.merge(df_lat_lon_processed, df_pop_2021[['MergeKey', 'Pessoas']], on='MergeKey', how='left')

        # Converter 'Latitude' e 'Longitude' para numérico ANTES de plotar
        df_map_data['Latitude'] = pd.to_numeric(df_map_data['Latitude'], errors='coerce')
        df_map_data['Longitude'] = pd.to_numeric(df_map_data['Longitude'], errors='coerce')

        # Exibição do mapa
        st.subheader("Mapa da População por Município em 2021")

        if not df_map_data.empty:
            fig_map = px.scatter_mapbox(df_map_data,
                                        lat="Latitude",
                                        lon="Longitude",
                                        size="Pessoas",
                                        color="Pessoas",
                                        hover_name="Município",
                                        hover_data={'Pessoas': ':,.2f', 'Latitude': True, 'Longitude': True},
                                        color_continuous_scale='magma',
                                        size_max=100,
                                        zoom=5,
                                        height=600)
            fig_map.update_layout(mapbox_style="carto-darkmatter",  # Estilo do mapa são open-street-map, carto-positron, carto-darkmatter 
                                  margin={"r": 0, "t": 30, "l": 0, "b": 0},
                                  mapbox_center={"lat": -15.79, "lon": -47.88})

            # Chave única para o gráfico
            chart_key = "map_chart"

            # Exibir o gráfico com captura de eventos de clique
            clicked_data = st.plotly_chart(fig_map, use_container_width=True, key=chart_key, events=["click"])

            # Exibir informações sobre o ponto clicado
            if clicked_data:
                if hasattr(clicked_data, 'plotly_event') and clicked_data.plotly_event is not None and isinstance(clicked_data.plotly_event, dict) and 'points' in clicked_data.plotly_event and len(clicked_data.plotly_event['points']) > 0:
                    try:
                        point_index = clicked_data.plotly_event['points'][0]['pointIndex']
                        clicked_municipio = df_map_data.iloc[point_index]['Município']
                        clicked_populacao = df_map_data.iloc[point_index]['Pessoas']
                        clicked_latitude = df_map_data.iloc[point_index]['Latitude']
                        clicked_longitude = df_map_data.iloc[point_index]['Longitude']

                        st.info(f"Município Clicado: {clicked_municipio}")
                        st.info(f"População: {clicked_populacao:,.0f}")
                        st.info(f"Latitude: {clicked_latitude}")
                        st.info(f"Longitude: {clicked_longitude}")

                    except (IndexError, KeyError, AttributeError):
                        st.warning("Erro ao acessar informações do clique.")
                else:
                    st.warning("Nenhum ponto clicado detectado.")

            else:
                st.warning("Nenhum clique detectado.")

        else:
            st.warning("Não há dados para exibir o mapa.")

        if not df_pop_2021.empty:
            total_populacao_2021 = df_pop_2021['Pessoas'].sum()
            st.metric("Total População em 2021", f"{total_populacao_2021:,}")

    else:
        st.error("Falha ao processar os dados de latitude e longitude.")

else:
    st.error("Falha ao carregar os dados de latitude e longitude.")

if df_pop_raw is None:
    st.error("Falha ao carregar os dados de população.")
