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
            # --- PRIMEIRO CLIQUE (Navegação na página . Dados População Painel) ---
            print("Tentando clicar no primeiro elemento (card de navegação para População Painel)...")
            selector_first_element_div = "//div[@aria-label='Navegação na página . Dados População Painel']"
            selector_first_element_path = "//div[@aria-label='Navegação na página . Dados População Painel']//path[@data-sub-selection-object-name='tile_default']"
            
            try:
                # Tenta o DIV pai
                element_to_click_1 = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, selector_first_element_div))
                )
                element_to_click_1.click()
                print(f"Clicou no primeiro elemento (DIV pai) com seletor: {selector_first_element_div}")
                
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e_div:
                print(f"Não conseguiu clicar no DIV pai do primeiro elemento diretamente ou foi interceptado: {e_div}")
                print("Tentando clicar no PATH do primeiro elemento...")
                try:
                    # Tenta o PATH
                    element_to_click_1 = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, selector_first_element_path))
                    )
                    element_to_click_1.click()
                    print(f"Clicou no primeiro elemento (PATH) com seletor: {selector_first_element_path}")
                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e_path:
                    print(f"Não conseguiu clicar no PATH do primeiro elemento: {e_path}")
                    print("Tentando clicar no primeiro elemento via JavaScript (último recurso)...")
                    try:
                        # Tenta via JavaScript no DIV
                        js_selector_first = "return document.evaluate(\"//div[@aria-label='Navegação na página . Dados População Painel']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                        element_js = driver.execute_script(js_selector_first)
                        if element_js:
                            driver.execute_script("arguments[0].click();", element_js)
                            print(f"Clicou no primeiro elemento (JavaScript) com seletor: {selector_first_element_div}")
                        else:
                            raise NoSuchElementException("Elemento JavaScript não encontrado para o primeiro clique.")
                    except Exception as e_js:
                        print(f"Erro fatal: Não conseguiu clicar no primeiro elemento mesmo via JavaScript: {e_js}")
                        raise # Re-lança a exceção para que a captura de tela seja feita

            # --- ESPERA POR CARREGAMENTO APÓS O PRIMEIRO CLIQUE ---
            print("\nPrimeiro clique realizado. Aguardando a página carregar (esperando spinner desaparecer)...")
            try:
                # Espera que o spinner esteja visível e depois espera que ele desapareça
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner detectado. Esperando que ele se torne invisível...")
                WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner invisível. Página carregada.")
            except TimeoutException:
                print("Spinner não detectado ou não desapareceu a tempo (pode não haver um ou o seletor está errado). Prosseguindo com espera fixa.")
                time.sleep(10) # Fallback para uma espera fixa se o spinner não for encontrado/desaparecer

            # --- SEGUNDO CLIQUE (Indicador . Clique aqui para seguir link) ---
            print("\nTentando clicar no segundo elemento (botão Indicador)...")
            selector_second_element_div = "//div[@aria-label='Indicador . Clique aqui para seguir link']"
            selector_second_element_path = "//div[@aria-label='Indicador . Clique aqui para seguir link']//path[@data-sub-selection-object-name='tile_default']"

            # Nova estratégia: Tentar ActionChains primeiro para simular um clique mais "real"
            try:
                print("Tentando clicar no segundo elemento via ActionChains (simulação de clique real)...")
                # Primeiro, esperamos que o DIV pai esteja presente no DOM (não necessariamente clicável)
                element_for_action = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector_second_element_div))
                )
                ActionChains(driver).move_to_element(element_for_action).click().perform()
                print(f"Clicou no segundo elemento (ActionChains) usando seletor: {selector_second_element_div}")
                # NÃO HÁ PAUSA FIXA AQUI, ESPERAMOS O PRÓXIMO CARREGAMENTO
            
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e_action_chains:
                print(f"Não conseguiu clicar no segundo elemento via ActionChains: {e_action_chains}")
                
                # Se ActionChains falhar, volta para a estratégia anterior (JavaScript > PATH > DIV)
                print("Voltando para tentativas JavaScript/Selenium para o segundo elemento...")
                try:
                    # TENTA VIA JAVASCRIPT
                    print("Tentando clicar no segundo elemento via JavaScript (fallback 1)...")
                    js_selector_second = "return document.evaluate(\"//div[@aria-label='Indicador . Clique aqui para seguir link']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                    element_js_2 = WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script(js_selector_second) # Espera até que o elemento esteja presente no DOM via JS
                    )
                    if element_js_2:
                        driver.execute_script("arguments[0].click();", element_js_2)
                        print(f"Clicou no segundo elemento (JavaScript) com seletor: {selector_second_element_div}")
                    else:
                        raise NoSuchElementException("Elemento JavaScript não encontrado para o segundo clique (fallback 1).")

                except (TimeoutException, NoSuchElementException) as e_js_2_fallback:
                    print(f"Não conseguiu clicar no segundo elemento via JavaScript (fallback 1): {e_js_2_fallback}")
                    print("Tentando clicar no PATH do segundo elemento como último recurso (Selenium)...")
                    try:
                        # Tenta o PATH
                        element_to_click_2 = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector_second_element_path))
                        )
                        element_to_click_2.click()
                        print(f"Clicou no segundo elemento (PATH) com seletor: {selector_second_element_path}")
                    except Exception as e_path_2_final:
                        print(f"Erro fatal: Não conseguiu clicar no segundo elemento mesmo via PATH (Selenium): {e_path_2_final}")
                        raise # Re-lança a exceção para que a captura de tela seja feita

            # --- ESPERA POR CARREGAMENTO APÓS O SEGUNDO CLIQUE (se aplicável) ---
            print("\nSegundo clique realizado. Aguardando a página carregar (esperando spinner desaparecer, se houver)...")
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner detectado. Esperando que ele se torne invisível...")
                WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner invisível. Página carregada após o segundo clique.")
            except TimeoutException:
                print("Spinner não detectado ou não desapareceu a tempo após o segundo clique. Prosseguindo.")
                time.sleep(5) # Pequena pausa de fallback

            # --- TERCEIRO CLIQUE (Elemento visual-container específico) ---
            print("\nTentando clicar no terceiro elemento (visual-container específico)...")
            
            # Aguarda um pouco mais para garantir que o elemento apareça após os cliques anteriores
            print("Aguardando 3 segundos para o elemento aparecer...")
            time.sleep(3)
            
            # Debug: Verificar quais elementos estão disponíveis na página
            print("Verificando elementos disponíveis na página...")
            try:
                # Verifica elementos visual-container
                visual_containers = driver.find_elements(By.XPATH, "//visual-container")
                print(f"Encontrados {len(visual_containers)} elementos visual-container")
                
                # Verifica elementos com data-testid
                testid_elements = driver.find_elements(By.XPATH, "//*[@data-testid='visual-container']")
                print(f"Encontrados {len(testid_elements)} elementos com data-testid='visual-container'")
                
                # Verifica elementos com role='group'
                group_elements = driver.find_elements(By.XPATH, "//*[@role='group']")
                print(f"Encontrados {len(group_elements)} elementos com role='group'")
                
                # Lista os primeiros elementos encontrados para debug
                for i, elem in enumerate(visual_containers[:3]):
                    try:
                        aria_label = elem.get_attribute("aria-label") or "N/A"
                        class_attr = elem.get_attribute("class") or "N/A"
                        print(f"  Visual-container {i+1}: aria-label='{aria_label}', class='{class_attr[:50]}...'")
                    except:
                        pass
                        
            except Exception as e:
                print(f"Erro ao verificar elementos: {e}")
            
            # Múltiplos seletores para tentar encontrar o elemento (evitando confusão com o segundo)
            selectors_to_try = [
                "//visual-container//div[@data-testid='visual-container']",
                "//div[@data-testid='visual-container']",
                "//visual-container//div[@role='group' and @tabindex='0']",
                "//div[@role='group' and @tabindex='0']",
                "//visual-container//div[@class='visualContainer unselectable readMode hideBorder paddingDisabled noVisualTitle visualHeaderAbove droppableElement ui-droppable']",
                "//div[@class='visualContainer unselectable readMode hideBorder paddingDisabled noVisualTitle visualHeaderAbove droppableElement ui-droppable']",
                "//visual-container//div[contains(@class, 'visualContainer')]",
                "//div[contains(@class, 'visualContainer')]",
                "//visual-container//div[@data-sub-selection-object-name='visual-area']",
                "//div[@data-sub-selection-object-name='visual-area']",
                "//visual-container//div[@data-sub-selection-display-name='Visual_Area']",
                "//div[@data-sub-selection-display-name='Visual_Area']",
                # Seletores mais genéricos como último recurso
                "//visual-container//div[contains(@class, 'visualContainer') and not(@aria-label='Indicador . Clique aqui para seguir link')]",
                "//div[contains(@class, 'visualContainer') and not(@aria-label='Indicador . Clique aqui para seguir link')]",
                "//visual-container//div[@role='group' and not(@aria-label='Indicador . Clique aqui para seguir link')]",
                "//div[@role='group' and not(@aria-label='Indicador . Clique aqui para seguir link')]"
            ]
            
            third_click_success = False
            for i, selector in enumerate(selectors_to_try):
                if third_click_success:
                    break
                    
                print(f"Tentativa {i+1}: Usando seletor: {selector}")
                try:
                    # Espera que o elemento esteja presente
                    element_to_click_3 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    
                    # Tenta clicar via ActionChains primeiro
                    try:
                        ActionChains(driver).move_to_element(element_to_click_3).click().perform()
                        print(f"Clicou no terceiro elemento (ActionChains) com seletor: {selector}")
                        third_click_success = True
                        break
                    except Exception as e_action:
                        print(f"ActionChains falhou: {e_action}")
                        
                        # Tenta clicar normal
                        try:
                            element_to_click_3.click()
                            print(f"Clicou no terceiro elemento (Selenium) com seletor: {selector}")
                            third_click_success = True
                            break
                        except Exception as e_click:
                            print(f"Clique normal falhou: {e_click}")
                            
                            # Tenta via JavaScript
                            try:
                                driver.execute_script("arguments[0].click();", element_to_click_3)
                                print(f"Clicou no terceiro elemento (JavaScript) com seletor: {selector}")
                                third_click_success = True
                                break
                            except Exception as e_js:
                                print(f"JavaScript falhou: {e_js}")
                                continue
                                
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Elemento não encontrado com seletor {selector}: {e}")
                    continue
            
            if not third_click_success:
                print("Erro fatal: Não conseguiu clicar no terceiro elemento com nenhuma estratégia.")
                raise NoSuchElementException("Terceiro elemento não encontrado ou não clicável.")

            # --- ESPERA POR CARREGAMENTO APÓS O TERCEIRO CLIQUE (se aplicável) ---
            print("\nTerceiro clique realizado. Aguardando a página carregar (esperando spinner desaparecer, se houver)...")
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner detectado. Esperando que ele se torne invisível...")
                WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(SPINNER_SELECTOR))
                print("Spinner invisível. Página carregada após o terceiro clique.")
            except TimeoutException:
                print("Spinner não detectado ou não desapareceu a tempo após o terceiro clique. Prosseguindo.")
                time.sleep(5) # Pequena pausa de fallback

        except Exception as e:
            # Captura exceções gerais ou re-lançadas das tentativas de clique
            print(f"Erro geral durante as interacoes na dashboard: {e}")
            print("Verifique se os seletores estão corretos e se os elementos estão visíveis e clicáveis no momento do script.")
            
            # --- Adicionado para depuração ---
            try:
                screenshot_filename = f"erro_clique_{time.strftime('%Y%m%d-%H%M%S')}.png"
                driver.save_screenshot(screenshot_filename)
                print(f"Captura de tela salva em: {screenshot_filename}")
            except Exception as ss_e:
                print(f"Erro ao salvar captura de tela: {ss_e}")
            # --- Fim da adição para depuração ---

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