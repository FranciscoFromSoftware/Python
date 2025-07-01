# -*- coding: utf-8 -*-
"""
Controle de visualização automatizada de dashboards do Power BI usando Selenium e Microsoft Edge.

Criado em 28/06/2025 

Francisco H. Lomas
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import threading
import msvcrt # Importa a biblioteca msvcrt (apenas para Windows)

# Variável global para controlar o loop principal
fechar_navegador = False

def monitorar_tecla_enter_msvcrt():
    """
    Função que monitora o pressionar da tecla 'Enter' usando msvcrt.
    Define a variável global 'fechar_navegador' como True quando 'Enter' é pressionado.
    """
    print("\nMonitorando a tecla 'Enter'... Pressione ENTER para fechar o navegador.")
    
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r': # '\r' é o byte para a tecla Enter no Windows
                global fechar_navegador
                fechar_navegador = True
                print("Tecla 'Enter' detectada. Preparando para fechar o navegador.")
                break
        time.sleep(0.1)

def realizar_interacoes_dashboard(driver, url_atual):
    """
    Função para adicionar interações de clique específicas em uma dashboard.
    Você customizará esta função para cada dashboard/página se precisar de cliques diferentes.

    Args:
        driver (webdriver.Edge): A instância do WebDriver Edge.
        url_atual (str): A URL da dashboard que está sendo exibida.
    """
    print(f"Tentando realizar interacoes na dashboard: {url_atual}")

    # **SELETOR PARA O SPINNER DO POWER BI**
    # Este seletor pode precisar ser ajustado. Inspecione o HTML quando a página estiver carregando.
    # Procure por divs ou outros elementos que indiquem "carregando".
    SPINNER_SELECTOR = (By.CSS_SELECTOR, "div.powerbi-spinner[data-testid='spinner']")
    
    if "reportId=4f3676e5-ac8c-4d39-82e8-90bddfecc24f" in url_atual: 
        print("Interagindo com a dashboard (reportId=4f3676e5-ac8c-4d39-82e8-90bddfecc24f)...")
        try:
            # --- PRIMEIRO CLIQUE ---
            print("Tentando clicar no tile do container9e609888-f796-bd52-6232-d7ed0bbfd3fa...")
            selector_first_tile = "//*[name()='g' and @id='container9e609888-f796-bd52-6232-d7ed0bbfd3fa']/*[name()='g' and @class='tile' and @cursor='pointer']"
            try:
                element_to_click_1 = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector_first_tile))
                )
                element_to_click_1.click()
                print("Clique realizado no primeiro tile.")
            except Exception as e:
                print(f"Não foi possível clicar no primeiro tile: {e}")
            time.sleep(5)

            # --- SEGUNDO CLIQUE ---
            print("Tentando clicar no tile do containera0f15145-f3de-0b6e-5688-53b57360677e...")
            selector_second_tile = "//*[name()='g' and @id='containera0f15145-f3de-0b6e-5688-53b57360677e']/*[name()='g' and @class='tile' and @cursor='pointer']"
            try:
                element_to_click_2 = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector_second_tile))
                )
                element_to_click_2.click()
                print("Clique realizado no segundo tile.")
            except Exception as e:
                print(f"Não foi possível clicar no segundo tile: {e}")
            time.sleep(5)

            # --- TERCEIRO CLIQUE (opcional, se necessário) ---
            # Adicione aqui se precisar de mais interações

        except Exception as e:
            print(f"Erro geral durante as interações na dashboard: {e}")

    else:
        print("Nenhuma interação específica configurada para esta dashboard.")


def visualizar_dashboards_com_enter(urls, intervalo_segundos=60, driver_path='msedgedriver.exe', zoom_level=100):
    """Função para visualizar dashboards do Power BI em um loop contínuo.
    Args:
        urls (list): Lista de URLs das dashboards do Power BI.
        intervalo_segundos (int): Intervalo em segundos entre as visualizações das dashboards (padrão: 30).
        driver_path (str): Caminho para o driver do navegador (padrão: 'msedgedriver.exe').
        zoom_level (int): Nível de zoom inicial (padrão: 100).
    """
    if not urls:
        print("Nenhuma URL fornecida. Adicione as URLs das suas dashboards à lista.")
        return

    monitor_thread = threading.Thread(target=monitorar_tecla_enter_msvcrt)
    monitor_thread.daemon = True
    monitor_thread.start()

    service = Service(executable_path=driver_path)
    options = Options()
    
    # Adiciona o argumento para iniciar maximizado
    options.add_argument("--start-maximized") 
    
    driver = None
    try:
        driver = webdriver.Edge(service=service, options=options)
        print("Navegador Microsoft Edge iniciado (maximizado).") # Mensagem de log atualizada

        # Não precisamos mais destas linhas, pois --start-maximized já deve fazer o trabalho
        # driver.maximize_window() 
        # driver.fullscreen_window() 
        # time.sleep(1) # Pode manter um pequeno sleep inicial se quiser, mas pode não ser necessário


        print("Iniciando a visualização automatizada das dashboards (páginas de relatório)...")
        print(f"Cada dashboard/página será exibida por {intervalo_segundos} segundos.")

        driver.get(urls[0])

        main_window_handle = driver.current_window_handle
        print(f"Aba principal identificada: {main_window_handle}")

        # Se o zoom for diferente de 100, ainda é preciso aplicar
        if zoom_level != 100:
            print(f"Aplicando zoom de {zoom_level}%...")
            driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")
            time.sleep(1)

        global fechar_navegador
        while not fechar_navegador:
            for i, url in enumerate(urls):
                if fechar_navegador:
                    break

                print(f"\nNavegando para dashboard/página {i+1}: {url}")
                try:
                    driver.switch_to.window(main_window_handle)
                    driver.get(url)
                    
                    # --- TEMPO DE ESPERA PRINCIPAL APÓS CARREGAMENTO DA URL ---
                    print("Aguardando 10 segundos para a dashboard carregar completamente e elementos ficarem prontos...")
                    time.sleep(10)
                    # --------------------------------------------------------

                    # Removi as reaplicações de maximização e tela cheia aqui também
                    # driver.maximize_window()
                    # driver.fullscreen_window()
                    # time.sleep(1)

                    if zoom_level != 100:
                        time.sleep(2)
                        driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")

                    print("Tentando ocultar elementos de interface para embed (se aplicável)...")
                    js_hide_embed_ui = """
                    var header = document.querySelector('.report-header');
                    if (header) { header.style.display = 'none'; console.log('Cabeçalho embed oculto.'); }
                    var footer = document.querySelector('.embed-footer');
                    if (footer) { footer.style.display = 'none'; console.log('Rodapé embed oculto.'); }
                    """
                    driver.execute_script(js_hide_embed_ui)
                    time.sleep(1)

                    # Chama a função de interacoes para a URL atual
                    realizar_interacoes_dashboard(driver, url)

                    print(f"Aguardando {intervalo_segundos} segundos...")
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
powerbi_dashboard_urls = [
    "https://app.powerbi.com/view?r=eyJrIjoiMGZhMDVhMzAtNTZkNy00OWMwLWJiNTgtNWY5ZWE2YjE4YjgxIiwidCI6IjY0YjI0ZDg4LTU4ODQtNDg0NC04YmZhLWMwNzFjOThjNjUyMSJ9&filterPaneEnabled=false&navContentPaneEnabled=false"
]
    # Adicione mais links de páginas do seu relatório aqui, seguindo o mesmo padrão!


# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    visualizar_dashboards_com_enter(powerbi_dashboard_urls, intervalo_segundos=60, driver_path='msedgedriver.exe', zoom_level=100)