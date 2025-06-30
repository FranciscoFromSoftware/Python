import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import io
import urllib.request

# Inicializando o geocoder
geolocator = Nominatim(user_agent="geocoding_script")

# Função para obter latitude e longitude com tratamento de erros
def geocode_municipio(municipio, uf):
    try:
        municipio_completo = f"{municipio}, {uf}, Brasil"
        location = geolocator.geocode(municipio_completo, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Erro de geocodificação para {municipio}: {e}")
        return None, None
    except Exception as e:
        print(f"Erro inesperado ao geocodificar {municipio}: {e}")
        return None, None
    time.sleep(0.1)  # Pequena pausa para respeitar os limites da API

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

    # Criando um DataFrame com municípios únicos e suas UFs
    municipios_unicos_df = df[['Município', 'UF']].drop_duplicates().reset_index(drop=True)

    # Criando colunas para latitude e longitude
    municipios_unicos_df['Latitude'] = None
    municipios_unicos_df['Longitude'] = None

    # Geocodificando os municípios únicos
    for index, row in municipios_unicos_df.iterrows():
        municipio = row['Município']
        uf = row['UF']
        lat, lon = geocode_municipio(municipio, uf)
        municipios_unicos_df.loc[index, 'Latitude'] = lat
        municipios_unicos_df.loc[index, 'Longitude'] = lon
        print(f"Geocodificado: {municipio} ({uf}) - Latitude: {lat}, Longitude: {lon}")

    # Exportando o DataFrame com latitude e longitude dos municípios únicos para um arquivo CSV
    output_csv_file = 'municipios_unicos_com_lat_lon.csv'
    municipios_unicos_df.to_csv(output_csv_file, index=False, encoding='utf-8')

    print(f"\nDataFrame com latitude e longitude dos municípios únicos exportado para: {output_csv_file}")
    print("\nAgora você pode inserir este arquivo na sua planilha do Google Sheets.")

except urllib.error.URLError as e:
    print(f"Erro ao acessar a planilha: {e}")
except pd.errors.EmptyDataError:
    print("A planilha está vazia.")
except Exception as e:
    print(f"Erro inesperado: {e}")