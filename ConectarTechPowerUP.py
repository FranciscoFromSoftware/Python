import requests
from bs4 import BeautifulSoup

def extrair_dados_cpu(url):
    """
    Extrai os dados da primeira CPU listada na tabela do URL fornecido.

    Args:
        url (str): O URL da página da CPU Database no TechPowerUp.

    Returns:
        dict: Um dicionário contendo os dados da CPU (Nome, Codinome, etc.)
              ou None se não for possível extrair os dados.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        soup = BeautifulSoup(response.content, 'html.parser')

        # Tenta encontrar a tabela de CPUs de forma mais geral
        tabela_cpu = soup.find('table', class_='items-desktop-table')

        if tabela_cpu:
            print("Tabela com classe 'items-desktop-table' encontrada.")
            # Tenta encontrar o tbody
            tbody = tabela_cpu.find('tbody')
            if tbody:
                print("Elemento tbody encontrado.")
                # Encontra a primeira linha de dados
                primeira_linha = tbody.find('tr')
                if primeira_linha:
                    print("Primeira linha <tr> dentro do tbody encontrada.")
                    celulas = primeira_linha.find_all('td')
                    if len(celulas) >= 9:
                        dados_cpu = {
                            'Name': celulas[0].text.strip(),
                            'Codename': celulas[1].text.strip(),
                            'Cores': celulas[2].text.strip(),
                            'Clock': celulas[3].text.strip(),
                            'Socket': celulas[4].text.strip(),
                            'Process': celulas[5].text.strip(),
                            'L3 Cache': celulas[6].text.strip(),
                            'TDP': celulas[7].text.strip(),
                            'Released': celulas[8].text.strip()
                        }
                        return dados_cpu
                    else:
                        print("A primeira linha da tabela não possui o número esperado de colunas.")
                        return None
                else:
                    print("Nenhuma linha de dados <tr> encontrada dentro do tbody.")
                    return None
            else:
                print("Elemento tbody NÃO encontrado dentro da tabela.")
                return None
        else:
            print("Tabela com classe 'items-desktop-table' NÃO encontrada.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# URL da página da CPU Database
url_cpu_database = 'https://www.techpowerup.com/cpu-specs/'

# Extrair os dados da primeira CPU
dados = extrair_dados_cpu(url_cpu_database)

# Imprimir os dados extraídos
if dados:
    print("Dados da primeira CPU encontrada:")
    for chave, valor in dados.items():
        print(f"{chave}: {valor}")