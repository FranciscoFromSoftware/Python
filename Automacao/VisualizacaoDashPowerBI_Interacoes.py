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

    # === PRIMEIRO CLIQUE ===
    # Elemento: <div aria-label='Navegação na página . Dados População Painel'> dentro de <transform data-testid='visual-container'>
    selector_first_element = "//transform[@data-testid='visual-container']//div[@aria-label='Navegação na página . Dados População Painel']"
    try:
        element_to_click_1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, selector_first_element))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element_to_click_1)
        try:
            ActionChains(driver).move_to_element(element_to_click_1).double_click().perform()
            print("Duplo clique realizado no visual-container com aria-label específico.")
        except Exception as e:
            print(f"Duplo clique ActionChains falhou: {e}. Tentando dois cliques simples via JavaScript...")
            try:
                driver.execute_script("arguments[0].click();", element_to_click_1)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", element_to_click_1)
                print("Dois cliques simples via JavaScript realizados no visual-container.")
            except Exception as e2:
                print(f"Também falhou via JavaScript: {e2}")
    except Exception as e:
        print(f"Não foi possível encontrar ou clicar no visual-container: {e}")
    time.sleep(5)

    # === SEGUNDO CLIQUE ===
    # Elemento: <g id='container03dbb183-4402-afb1-cac3-33078831b513'>
    selector_second_element = "//g[@id='container03dbb183-4402-afb1-cac3-33078831b513']"
    try:
        element_to_click_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, selector_second_element))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element_to_click_2)
        try:
            ActionChains(driver).move_to_element(element_to_click_2).double_click().perform()
            print("Duplo clique realizado no segundo elemento <g> pelo id.")
        except Exception as e:
            print(f"Duplo clique ActionChains falhou: {e}. Tentando dois cliques simples via JavaScript...")
            try:
                driver.execute_script("arguments[0].click();", element_to_click_2)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", element_to_click_2)
                print("Dois cliques simples via JavaScript realizados no segundo elemento <g>.")
            except Exception as e2:
                print(f"Também falhou via JavaScript: {e2}")
    except Exception as e:
        print(f"Não foi possível encontrar ou clicar no segundo elemento <g>: {e}")
    time.sleep(2)

    # === TERCEIRA INTERAÇÃO: CLICA NO GRUPO <g class='tile'> PAI DO PATH ===
    # Elemento: <g class='tile'> que contém o <path data-sub-selection-object-name='tile_default' data-sub-selection-display-name='Card_Background_Color'>
    selector_tile_group = "//g[@class='tile' and path[@data-sub-selection-object-name='tile_default' and @data-sub-selection-display-name='Card_Background_Color']]"
    elements_found_tile = driver.find_elements(By.XPATH, selector_tile_group)
    print(f"Encontrados {len(elements_found_tile)} elementos para o terceiro clique.")
    for idx, el in enumerate(elements_found_tile):
        print(f"Elemento {idx+1}: exibido={{el.is_displayed()}}, habilitado={{el.is_enabled()}}")
    if not elements_found_tile:
        with open('debug_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print('HTML da página salvo em debug_dashboard.html')
    else:
        try:
            element_to_click_tile = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector_tile_group))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element_to_click_tile)
            ActionChains(driver).move_to_element(element_to_click_tile).double_click().perform()
            print("Duplo clique realizado no grupo <g class='tile'> do SVG.")
        except Exception as e:
            print(f"Não foi possível dar duplo clique no grupo <g class='tile'>: {e}")
            # Tenta via JavaScript
            try:
                driver.execute_script("arguments[0].click();", element_to_click_tile)
                print("Clique via JavaScript realizado no grupo <g class='tile'>.")
            except Exception as e2:
                print(f"Também falhou via JavaScript: {e2}")
        time.sleep(2)

    # --- TERCEIRO CLIQUE (opcional, se necessário) ---
    # Adicione aqui se precisar de mais interações


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