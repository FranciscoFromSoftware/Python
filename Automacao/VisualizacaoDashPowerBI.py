# -*- coding: utf-8 -*-
"""
Controle de visualização automatizada de dashboards do Power BI usando Selenium e Microsoft Edge.

Criado em 28/06/2025 

Francisco H. Lomas
"""

from selenium import webdriver # Importa o webdriver do Selenium para controle do navegador
from selenium.webdriver.edge.service import Service # Importa o serviço do Edge para inicializar o driver
from selenium.webdriver.edge.options import Options # Importa as opções do Edge para configuração do navegador
import time # Importa a biblioteca time para manipulação de tempo
import threading # Importa a biblioteca threading para permitir a execução de threads
import msvcrt # Importa a biblioteca msvcrt (apenas para Windows)

# Variável global para controlar o loop principal
fechar_navegador = False

def monitorar_tecla_enter_msvcrt(): # Função para monitorar a tecla 'Enter'
# Obs parênteses vazios () em monitorar_tecla_enter_msvcrt() significam que você a chama sem fornecer nenhum valor específico.
# monitor_thread = threading.Thread(target=monitorar_tecla_enter_msvcrt)
# monitor_thread.start()
    """
    Função que monitora o pressionar da tecla 'Enter' usando msvcrt.
    Define a variável global 'fechar_navegador' como True quando 'Enter' é pressionado.
    """
    print("\nMonitorando a tecla 'Enter'... Pressione ENTER para fechar o navegador.")
    while True: # Loop contínuo para monitorar a tecla
        if msvcrt.kbhit(): # Verifica se uma tecla foi pressionada a função msvcrt.kbhit()
            # msvcrt.kbhit() retorna True se uma tecla foi pressionada, permitindo a leitura do caractere
            key = msvcrt.getch() # Obtém o caractere da tecla pressionada a função msvcrt.getch()
            # msvcrt.getch() retorna o byte correspondente à tecla pressionada
            if key == b'\r': # '\r' é o byte para a tecla Enter no Windows a key == b'\r' verifica se a tecla pressionada é 'Enter'
                # Se a tecla pressionada for 'Enter', define a variável global fechar_naveg
                global fechar_navegador # função global para permitir a modificação da variável fora do escopo local
                fechar_navegador = True # Define a variável global fechar_navegador como True
                print("Tecla 'Enter' detectada. Preparando para fechar o navegador.")
                break # Sai do loop se 'Enter' for pressionado
        time.sleep(0.1) # Pequena pausa para evitar alto uso da CPU

# Função principal para visualizar dashboards do Power BI
def visualizar_dashboards_com_enter(urls, intervalo_segundos=180, driver_path='msedgedriver.exe', zoom_level=100): 
# Argumentos: urls para visualizar, intervalo_segundos para pausas, driver_path para o caminho do driver, zoom_level para o nível de zoom

    """Função para visualizar dashboards do Power BI em um loop contínuo.
    Args:
        urls (list): Lista de URLs das dashboards do Power BI.
        intervalo_segundos (int): Intervalo em segundos entre as visualizações das dashboards (padrão: 30).
        driver_path (str): Caminho para o driver do navegador (padrão: 'msedgedriver.exe').
        zoom_level (int): Nível de zoom inicial (padrão: 100).
    """
    if not urls: # Verifica se a lista de URLs está vazia
        print("Nenhuma URL fornecida. Adicione as URLs das suas dashboards à lista.")
        return

    # Inicia o monitoramento da tecla 'Enter' em uma thread separada para evitar o bloqueio do loop principal monitorando a tecla 'Enter' dentro da def visualizar_dashboards_com_enter
    monitor_thread = threading.Thread(target=monitorar_tecla_enter_msvcrt) # threadinding.Thread() cria uma nova thread para monitorar a tecla 'Enter'
    monitor_thread.daemon = True # Define a thread como daemon para que ela seja encerrada quando o programa principal terminar
    monitor_thread.start() # Inicia a thread

    service = Service(executable_path=driver_path) # Cria uma instância do serviço do Edge com o caminho do driver fornecido
    options = Options() # Cria uma instância das opções do Edge para configuração do navegador
    options.add_argument("--start-maximized") # Adiciona o argumento para iniciar o navegador maximizado --start-maximized
    
    driver = None # Inicializa a variável driver como None para uso posterior
    try: # Tenta inicializar o navegador com função try que permite capturar erros durante a inicialização
        driver = webdriver.Edge(service=service, options=options) # Cria uma instância do navegador Edge com o serviço e as opções configuradas
        print("Navegador Microsoft Edge iniciado (maximizado).") # Imprime uma mensagem indicando que o navegador foi iniciado
        print("Iniciando a visualização automatizada das dashboards (páginas de relatório)...") # Imprime uma mensagem indicando o início da visualização automatizada
        print(f"Cada dashboard/página será exibida por {intervalo_segundos} segundos.") # Imprime o intervalo de tempo entre as visualizações das dashboards

        # Abre a primeira URL para estabelecer a janela principal
        driver.get(urls[0]) # Abre a primeira URL da lista de dashboards .get(urls[0]) abre a primeira URL da lista de dashboards
        # função driver.get() carrega a página da URL especificada no navegador

        main_window_handle = driver.current_window_handle # Obtém o identificador da janela principal do navegador .current_window_handle retorna o identificador da janela atual do navegador
        # Isso é importante para garantir que o script sempre retorne à janela principal após cada nave
        print(f"Aba principal identificada: {main_window_handle}") # Imprime o identificador da janela principal

        # Ativa o modo de tela cheia (equivalente ao F11)
        print("Ativando o modo de tela cheia (F11)...") 
        driver.fullscreen_window() # A função driver.fullscreen_window() ativa o modo de tela cheia no navegador
        time.sleep(1) # Pausa para garantir que a tela cheia seja aplicada corretamente

        # Aplica o nível de zoom inicial
        if zoom_level != 100: # Verifica se o nível de zoom é diferente de 100% para aplicar o zoom
            print(f"Aplicando zoom de {zoom_level}%...")
            driver.execute_script(f"document.body.style.zoom='{zoom_level}%'") # A função driver.execute_script() executa um script JavaScript para aplicar o nível de zoom especificado
            time.sleep(1)# Pausa para garantir que o zoom seja aplicado corretamente

        # Loop principal para manter o ciclo contínuo
        global fechar_navegador
        while not fechar_navegador:
            for i, url in enumerate(urls):
                if fechar_navegador:
                    break

                print(f"\nNavegando para dashboard/página {i+1}: {url}")
                try:
                    driver.switch_to.window(main_window_handle)
                    driver.get(url)
                    
                    print("Reaplicando maximização e tela cheia após carregamento...")
                    driver.maximize_window()
                    driver.fullscreen_window()
                    time.sleep(1)

                    if zoom_level != 100:
                        time.sleep(2) 
                        driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")

                    print(f"Aguardando {intervalo_segundos} segundos...")
                    # Verifica 'fechar_navegador' dentro do time.sleep para resposta rápida
                    for _ in range(intervalo_segundos):
                        if fechar_navegador:
                            break
                        time.sleep(1)

                except Exception as e:
                    print(f"Erro ao navegar para a URL {url}: {e}")
                    print("Continuando para a próxima dashboard...")
            
            if fechar_navegador:
                break

    except Exception as e:
        print(f"Erro ao inicializar o navegador ou durante a execução: {e}")
    finally:
        if driver:
            print("\nEncerrando o navegador.")
            driver.quit()


# --- SUAS DASHBOARDS (PÁGINAS DE RELATÓRIO) AQUI ---
# IMPORTANTES: Certifique-se de que cada URL inclui os parâmetros para otimização visual.
# Ex: ?experience=power-bi&chromeless=1&filterPaneEnabled=false&navContentPaneEnabled=false
powerbi_dashboard_urls = [
    "https://app.powerbi.com/reportEmbed?reportId=b912fa6e-07ac-41b1-90a2-b81e8180fa63&autoAuth=true&ctid=64b24d88-5884-4844-8bfa-c071c98c6521&filterPaneEnabled=false&navContentPaneEnabled=false"
]
    # Adicione mais links de páginas do seu relatório aqui, seguindo o mesmo padrão!
    # "https://app.powerbi.com/groups/me/reports/SEU_REPORT_ID/SUA_PAGE_ID_AQUI?experience=power-bi&chromeless=1&filterPaneEnabled=false&navContentPaneEnabled=false",


# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    # Teste com diferentes 'zoom_level' se o problema de "minimização" persistir.
    # Por exemplo, 110, 125, 150. Comece com 100 e vá aumentando.
    visualizar_dashboards_com_enter(powerbi_dashboard_urls, intervalo_segundos= 60, driver_path='msedgedriver.exe', zoom_level=100)
