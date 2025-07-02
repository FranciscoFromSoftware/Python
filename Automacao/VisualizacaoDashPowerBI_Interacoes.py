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
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyautogui
import signal
import sys

# Variável global para controlar o loop principala
fechar_navegador = False

def clicar_posicao_absoluta(driver, element, offset_y=0):
    """Move o mouse suavemente para a posição do elemento usando porcentagens da tela. Permite ajuste vertical (offset_y)."""
    screen_width, screen_height = pyautogui.size()
    location = element.location_once_scrolled_into_view
    size = element.size
    x_element = location['x'] + size['width'] // 2
    y_element = location['y'] + size['height'] // 2 + offset_y
    rect = driver.get_window_rect()
    x_window = rect['x']
    y_window = rect['y']
    window_width = rect['width']
    window_height = rect['height']
    x_abs = x_window + x_element
    y_abs = y_window + y_element
    x_percent = (x_abs / screen_width) * 100
    y_percent = (y_abs / screen_height) * 100
    print(f"Movendo mouse suavemente para: ({x_abs}, {y_abs}) - Porcentagens: ({x_percent:.1f}%, {y_percent:.1f}%)")
    pyautogui.moveTo(x_abs, y_abs, duration=0.5)
    pyautogui.click()

def realizar_interacoes_dashboard(driver, url_atual):
    print(f"Tentando realizar interacoes na dashboard: {url_atual}")

    # 1º clique: Selenium no elemento real
    try:
        selector = "//transform[@data-testid='visual-container']//div[@aria-label='Navegação na página . Dados População Painel']"
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            ActionChains(driver).move_to_element(element).click().perform()
            print(f"Clique 1 realizado com ActionChains.")
        except Exception as e:
            print(f"ActionChains falhou no clique 1: {e}. Tentando via JavaScript...")
            try:
                driver.execute_script("arguments[0].click();", element)
                print(f"Clique 1 realizado via JavaScript.")
            except Exception as e2:
                print(f"Também falhou via JavaScript no clique 1: {e2}")
    except Exception as e:
        print(f"Não foi possível encontrar ou clicar no elemento do clique 1: {e}")
    time.sleep(2)

    # 2º clique: posição do mouse baseada em elemento de referência
    try:
        selector2 = "//div[contains(@class, 'vcBody') and @data-sub-selection-object-name='visual-area' and @data-sub-selection-display-name='Visual_Area']"
        element2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, selector2))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element2)
        location = element2.location_once_scrolled_into_view
        size = element2.size
        x = location['x'] + size['width'] // 2
        y = location['y'] + size['height'] // 2
        ActionChains(driver).move_by_offset(x, y).click().perform()
        print(f"Clique 2 realizado pelas coordenadas absolutas do mouse ({x}, {y}).")
        ActionChains(driver).move_by_offset(-x, -y).perform()  # volta o mouse
    except Exception as e:
        print(f"Não foi possível encontrar ou clicar no elemento do clique 2: {e}")
    time.sleep(2)

    # 3º clique: 80% x, 30.5% y da tela
    screen_width, screen_height = pyautogui.size()
    x_abs = int(screen_width * 0.84)
    y_abs = int(screen_height * 0.31)
    print(f"Movendo mouse para 83% x, 30% y: ({x_abs}, {y_abs})")
    pyautogui.moveTo(x_abs, y_abs, duration=0.5)
    pyautogui.doubleClick()
    time.sleep(2)
    pyautogui.click()
    print(f"Clique 3 realizado (duplo clique) em 80% x, 30.5% y da tela.")
    time.sleep(2)

    # 4º clique: 68% x, 20% y da tela
    x_abs = int(screen_width * 0.54)
    y_abs = int(screen_height * 0.56)
    print(f"Movendo mouse para 68% x, 20% y: ({x_abs}, {y_abs})")
    pyautogui.moveTo(x_abs, y_abs, duration=0.5)
    pyautogui.click()
    print(f"Clique 4 realizado em 68% x, 20% y da tela.")
    time.sleep(2)

def encerrar_programa(signum, frame):
    """Função para encerrar o programa de forma limpa."""
    global fechar_navegador
    print("\nRecebido sinal de encerramento. Finalizando programa...")
    fechar_navegador = True
    sys.exit(0)

def verificar_janela_fechada(driver):
    """Verifica se a janela do navegador foi fechada manualmente."""
    try:
        # Tenta acessar uma propriedade da janela
        driver.current_url
        return False
    except:
        print("\nJanela do navegador foi fechada. Encerrando programa...")
        return True

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
                
                # Verifica se a janela foi fechada
                if verificar_janela_fechada(driver):
                    fechar_navegador = True
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
    # Configura o handler para Ctrl+C
    signal.signal(signal.SIGINT, encerrar_programa)
    print("Pressione Ctrl+C para encerrar o programa a qualquer momento.")
    visualizar_dashboards_com_enter(powerbi_dashboard_urls, intervalo_segundos=60, driver_path='msedgedriver.exe', zoom_level=100)