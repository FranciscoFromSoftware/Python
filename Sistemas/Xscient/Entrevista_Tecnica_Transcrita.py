# -*- coding: utf-8 -*-
"""
Sistema Completo de Gravação e Transcrição de Entrevistas Técnicas
==================================================================

Este sistema permite gravar áudio, capturar screenshots da tela e transcrever
o áudio automaticamente, sendo ideal para entrevistas técnicas, reuniões
ou qualquer situação que necessite de documentação audiovisual.

Funcionalidades:
- Gravação de áudio em tempo real
- Captura automática de screenshots em intervalos configuráveis
- Transcrição de áudio para texto usando Google Speech Recognition
- Salvamento organizado de todos os arquivos gerados

Dependências necessárias:
- pyaudio: Para gravação de áudio
- pyautogui: Para captura de tela
- Pillow: Para processamento de imagens
- SpeechRecognition: Para transcrição de áudio

Requisitos do sistema:
- Microfone funcionando
- Conexão com internet (para transcrição)
- Permissões de acesso ao microfone e tela

Criado em: 28/06/2025
Autor: Francisco H. Lomas
Versão: 1.0
"""

import pyaudio
import wave
import pyautogui
import time
import os
from datetime import datetime
import threading
import speech_recognition as sr

# =============================================================================
# CONFIGURAÇÕES DO SISTEMA
# =============================================================================

# Intervalo entre capturas de tela (em segundos)
# Valores menores = mais screenshots, mas mais uso de CPU
# Valores maiores = menos screenshots, mas pode perder momentos importantes
DURACAO_CAPTURA_TELA = 2

# Nome da pasta onde os screenshots serão salvos
# A pasta será criada automaticamente se não existir
PASTA_SCREENSHOTS = "screenshots"

# =============================================================================
# VARIÁVEIS GLOBAIS
# =============================================================================

# Controla se o sistema está executando (usado para parar threads)
executando = True

# Lista para armazenar os frames de áudio capturados
frames = []

# Contador para numerar os screenshots sequencialmente
contador_screenshots = 0

# =============================================================================
# CRIAÇÃO DE DIRETÓRIOS NECESSÁRIOS
# =============================================================================

# Criar pasta para screenshots se não existir
# Isso evita erros quando o sistema tentar salvar as imagens
if not os.path.exists(PASTA_SCREENSHOTS):
    os.makedirs(PASTA_SCREENSHOTS)
    print(f"Pasta '{PASTA_SCREENSHOTS}' criada automaticamente.")

# =============================================================================
# FUNÇÕES DE TRANSCRIÇÃO DE ÁUDIO
# =============================================================================

def transcrever_audio(arquivo_audio="audio.wav"):
    """
    Transcreve um arquivo de áudio para texto usando Google Speech Recognition.
    
    Esta função utiliza a API gratuita do Google para converter áudio em texto.
    O processo pode demorar dependendo do tamanho do arquivo e qualidade da
    conexão com a internet.
    
    Args:
        arquivo_audio (str): Caminho para o arquivo de áudio (.wav)
                           Padrão: "audio.wav"
    
    Returns:
        str: Texto transcrito do áudio ou mensagem de erro
        
    Observações importantes:
    - Requer conexão com internet
    - Funciona melhor com áudio claro e sem ruído
    - Configurado para português brasileiro (pt-BR)
    - Limite de 10MB por arquivo (Google Speech Recognition)
    - Pode demorar alguns minutos para arquivos grandes
    
    Exemplo de uso:
        texto = transcrever_audio("minha_entrevista.wav")
        if not texto.startswith("Erro"):
            print("Transcrição:", texto)
    """
    print("\nIniciando transcrição do áudio...")
    
    # Inicializar reconhecedor de voz
    # O SpeechRecognition suporta múltiplos serviços (Google, Sphinx, etc.)
    recognizer = sr.Recognizer()
    
    try:
        # Carregar arquivo de áudio
        # O arquivo deve estar no formato WAV para compatibilidade
        with sr.AudioFile(arquivo_audio) as source:
            print("Carregando arquivo de áudio...")
            
            # Gravar o áudio completo do arquivo
            # Isso pode demorar para arquivos grandes
            audio = recognizer.record(source)
            
            print("Processando transcrição (pode demorar alguns minutos)...")
            print("Dica: Quanto maior o arquivo, mais tempo levará.")
            
            # Tentar reconhecimento com Google Speech Recognition
            # Configurado para português brasileiro para melhor precisão
            try:
                texto = recognizer.recognize_google(audio, language='pt-BR')
                print("Transcrição concluída com sucesso!")
                return texto
                
            except sr.UnknownValueError:
                # Erro quando o áudio não pode ser entendido
                print("Erro: Não foi possível entender o áudio.")
                print("Possíveis causas:")
                print("- Áudio muito baixo ou com muito ruído")
                print("- Falas muito rápidas ou incompreensíveis")
                print("- Problemas com o microfone durante a gravação")
                return "Erro: Áudio não reconhecido"
                
            except sr.RequestError as e:
                # Erro na requisição ao serviço do Google
                print(f"Erro na requisição ao serviço de reconhecimento: {e}")
                print("Possíveis causas:")
                print("- Sem conexão com internet")
                print("- Serviço do Google temporariamente indisponível")
                print("- Limite de requisições excedido")
                return f"Erro na requisição: {e}"
                
    except FileNotFoundError:
        # Erro quando o arquivo de áudio não é encontrado
        print(f"Erro: Arquivo de áudio '{arquivo_audio}' não encontrado.")
        print("Verifique se o arquivo existe no diretório correto.")
        return "Erro: Arquivo de áudio não encontrado"
        
    except Exception as e:
        # Erro genérico durante o processo
        print(f"Erro durante a transcrição: {e}")
        return f"Erro: {e}"

def salvar_transcricao(texto, nome_arquivo="transcricao.txt"):
    """
    Salva a transcrição em um arquivo de texto formatado.
    
    Cria um arquivo de texto com cabeçalho informativo e formatação
    adequada para facilitar a leitura e organização das transcrições.
    
    Args:
        texto (str): Texto transcrito a ser salvo
        nome_arquivo (str): Nome do arquivo onde salvar a transcrição
                          Padrão: "transcricao.txt"
    
    Returns:
        bool: True se salvou com sucesso, False caso contrário
        
    Observações:
    - Arquivo é salvo em UTF-8 para suportar caracteres especiais
    - Inclui timestamp de quando a transcrição foi salva
    - Formatação organizada para fácil leitura
    
    Exemplo de uso:
        sucesso = salvar_transcricao("Texto da entrevista...", "entrevista_01.txt")
        if sucesso:
            print("Transcrição salva com sucesso!")
    """
    try:
        # Abrir arquivo em modo de escrita com encoding UTF-8
        # UTF-8 garante que caracteres especiais sejam salvos corretamente
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            # Escrever cabeçalho informativo
            arquivo.write("TRANSCRIÇÃO DA ENTREVISTA TÉCNICA\n")
            arquivo.write("=" * 50 + "\n")
            arquivo.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            arquivo.write("=" * 50 + "\n\n")
            
            # Escrever o texto transcrito
            arquivo.write(texto)
        
        print(f"Transcrição salva em: {nome_arquivo}")
        return True
        
    except Exception as e:
        # Erro ao salvar o arquivo
        print(f"Erro ao salvar transcrição: {e}")
        print("Possíveis causas:")
        print("- Sem permissão de escrita no diretório")
        print("- Disco cheio")
        print("- Arquivo aberto por outro programa")
        return False

# =============================================================================
# FUNÇÕES DE CAPTURA DE TELA
# =============================================================================

def capturar_tela():
    """
    Captura screenshots da tela em intervalos regulares.
    
    Esta função roda em uma thread separada e captura a tela a cada
    DURACAO_CAPTURA_TELA segundos. Os screenshots são salvos com
    timestamp e numeração sequencial para facilitar a organização.
    
    Observações importantes:
    - Roda em thread separada para não interferir na gravação de áudio
    - Captura toda a tela principal (não funciona com múltiplos monitores)
    - Arquivos são salvos em formato PNG (boa qualidade, tamanho moderado)
    - Nome dos arquivos: screenshot_YYYYMMDD_HHMMSS_XXXX.png
    
    Dependências:
    - pyautogui: Para captura de tela
    - Pillow: Para processamento e salvamento das imagens
    
    Exemplo de arquivos gerados:
    - screenshot_20250628_143015_0001.png
    - screenshot_20250628_143017_0002.png
    - screenshot_20250628_143019_0003.png
    """
    global contador_screenshots, executando
    
    print(f"Iniciando captura de tela a cada {DURACAO_CAPTURA_TELA} segundos...")
    
    while executando:
        try:
            # Capturar screenshot da tela inteira
            # pyautogui.screenshot() captura a tela principal
            screenshot = pyautogui.screenshot()
            
            # Gerar nome do arquivo com timestamp e contador
            # Formato: YYYYMMDD_HHMMSS para facilitar ordenação
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Contador com 4 dígitos (0001, 0002, etc.)
            nome_arquivo = f"{PASTA_SCREENSHOTS}/screenshot_{timestamp}_{contador_screenshots:04d}.png"
            
            # Salvar screenshot em formato PNG
            # PNG mantém boa qualidade sem compressão excessiva
            screenshot.save(nome_arquivo)
            print(f"Screenshot salvo: {nome_arquivo}")
            
            # Incrementar contador para próximo arquivo
            contador_screenshots += 1
            
            # Aguardar próximo intervalo de captura
            # time.sleep() não bloqueia a thread principal
            time.sleep(DURACAO_CAPTURA_TELA)
            
        except Exception as e:
            # Erro durante a captura de tela
            print(f"Erro ao capturar tela: {e}")
            print("Possíveis causas:")
            print("- Sem permissão de acesso à tela")
            print("- Problemas com drivers de vídeo")
            print("- Tela bloqueada ou em modo de segurança")
            time.sleep(1)  # Aguardar antes de tentar novamente

# =============================================================================
# FUNÇÕES DE GRAVAÇÃO DE ÁUDIO
# =============================================================================

def gravar_audio():
    """
    Grava áudio do microfone em tempo real.
    
    Esta função configura o sistema de áudio, inicia a gravação e
    salva o áudio em arquivo WAV. A gravação continua até que o
    usuário pressione Ctrl+C ou ocorra algum erro.
    
    Configurações de áudio:
    - Formato: 16-bit PCM (paInt16)
    - Canais: 1 (mono)
    - Taxa de amostragem: 44100 Hz (qualidade CD)
    - Buffer: 1024 frames
    
    Observações importantes:
    - Requer microfone funcionando e acessível
    - Qualidade do áudio afeta diretamente a precisão da transcrição
    - Arquivo é salvo em formato WAV (compatível com SpeechRecognition)
    - Gravação continua até interrupção manual (Ctrl+C)
    
    Dependências:
    - pyaudio: Para acesso ao hardware de áudio
    - wave: Para salvamento em formato WAV
    
    Exemplo de uso:
        gravar_audio()  # Inicia gravação até Ctrl+C
    """
    global frames, executando
    
    # Inicializar PyAudio
    # PyAudio é a interface principal para acesso ao áudio
    audio = pyaudio.PyAudio()
    
    # Configurar stream de áudio para entrada (microfone)
    # Parâmetros otimizados para reconhecimento de voz
    stream = audio.open(
        input=True,                    # Modo de entrada (gravação)
        format=pyaudio.paInt16,        # Formato 16-bit (boa qualidade)
        channels=1,                    # Mono (suficiente para voz)
        rate=44100,                    # 44.1 kHz (qualidade CD)
        frames_per_buffer=1024,        # Buffer de 1024 frames
    )
    
    print("Iniciando gravação de áudio e captura de tela...")
    print("Pressione Ctrl+C para parar a gravação.")
    print("-" * 50)
    print("Dicas para melhor qualidade:")
    print("- Fale claramente e em volume adequado")
    print("- Evite ruídos de fundo")
    print("- Mantenha distância consistente do microfone")
    print("-" * 50)
    
    try:
        # Loop principal de gravação
        # Lê dados do microfone continuamente
        while executando:
            # Ler 1024 frames de áudio do microfone
            # Retorna bytes que são adicionados à lista frames
            data = stream.read(1024)
            frames.append(data)
            
    except KeyboardInterrupt:
        # Interrupção manual pelo usuário (Ctrl+C)
        print("\nInterrupção detectada. Finalizando gravação...")
        pass
    
    # Limpeza e finalização do stream de áudio
    # Importante para liberar recursos do sistema
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Salvar arquivo de áudio em formato WAV
    # WAV é o formato mais compatível com SpeechRecognition
    arquivo = wave.open("audio.wav", "wb")
    arquivo.setnchannels(1)                    # 1 canal (mono)
    arquivo.setsampwidth(audio.get_sample_size(pyaudio.paInt16))  # 2 bytes por amostra
    arquivo.setframerate(44100)                # 44.1 kHz
    arquivo.writeframes(b''.join(frames))      # Juntar todos os frames
    arquivo.close()
    
    # Informações finais sobre a gravação
    print(f"Áudio salvo: audio.wav")
    print(f"Total de screenshots capturados: {contador_screenshots}")
    
    # Calcular duração aproximada da gravação
    duracao_segundos = len(frames) * 1024 / 44100
    print(f"Duração aproximada da gravação: {duracao_segundos:.1f} segundos")

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """
    Função principal que coordena todo o sistema.
    
    Esta função inicializa o sistema, gerencia as threads de gravação
    e captura de tela, e coordena o processo de transcrição. É o ponto
    de entrada principal do programa.
    
    Fluxo de execução:
    1. Inicialização e configuração
    2. Início da thread de captura de tela
    3. Início da gravação de áudio
    4. Finalização e limpeza
    5. Opção de transcrição do áudio
    
    Observações importantes:
    - Usa threads para executar gravação e captura simultaneamente
    - Thread de captura é marcada como daemon (para encerrar automaticamente)
    - Sistema pode ser interrompido com Ctrl+C a qualquer momento
    - Transcrição é opcional e requer confirmação do usuário
    
    Exemplo de uso:
        if __name__ == "__main__":
            main()
    """
    global executando
    
    # Cabeçalho do sistema
    print("Sistema de Gravação de Áudio e Captura de Tela")
    print("=" * 50)
    print("Este sistema irá:")
    print("1. Gravar áudio do seu microfone")
    print("2. Capturar screenshots da tela")
    print("3. Oferecer transcrição do áudio (opcional)")
    print("=" * 50)
    
    # Iniciar thread de captura de tela
    # Thread separada permite captura simultânea com gravação de áudio
    thread_screenshot = threading.Thread(target=capturar_tela)
    thread_screenshot.daemon = True  # Thread será encerrada quando programa principal terminar
    thread_screenshot.start()
    
    try:
        # Iniciar gravação de áudio
        # Esta função roda na thread principal
        gravar_audio()
        
    except KeyboardInterrupt:
        # Tratamento de interrupção manual
        print("\nInterrompendo gravação...")
    
    finally:
        # Bloco finally garante que a limpeza sempre seja executada
        # Mesmo se houver erro ou interrupção
        
        # Parar execução (sinaliza para threads pararem)
        executando = False
        
        # Aguardar thread de screenshot terminar
        # timeout=2 evita que o programa trave se a thread não responder
        thread_screenshot.join(timeout=2)
        
        # Resumo final dos arquivos gerados
        print("\nGravação finalizada!")
        print(f"Arquivos salvos:")
        print(f"- Áudio: audio.wav")
        print(f"- Screenshots: pasta '{PASTA_SCREENSHOTS}'")
        
        # Verificar se arquivo de áudio foi criado
        if os.path.exists("audio.wav"):
            tamanho_arquivo = os.path.getsize("audio.wav") / (1024 * 1024)  # MB
            print(f"- Tamanho do arquivo de áudio: {tamanho_arquivo:.2f} MB")
            
            # Perguntar se quer transcrever o áudio
            # Só oferece transcrição se o arquivo existe
            resposta = input("\nDeseja transcrever o áudio? (s/n): ").lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                # Transcrever áudio
                print("Iniciando processo de transcrição...")
                texto_transcrito = transcrever_audio()
                
                if texto_transcrito and not texto_transcrito.startswith("Erro"):
                    # Salvar transcrição apenas se foi bem-sucedida
                    sucesso = salvar_transcricao(texto_transcrito)
                    if sucesso:
                        print("\nTranscrição concluída e salva!")
                        print("Arquivo: transcricao.txt")
                    else:
                        print("\nErro ao salvar transcrição.")
                else:
                    print(f"\nFalha na transcrição: {texto_transcrito}")
                    print("Dicas para melhorar:")
                    print("- Verifique a qualidade do áudio")
                    print("- Certifique-se de ter conexão com internet")
                    print("- Tente falar mais claramente na próxima gravação")
            else:
                print("Transcrição ignorada.")
        else:
            print("Arquivo de áudio não encontrado. Transcrição não disponível.")

# =============================================================================
# PONTO DE ENTRADA DO PROGRAMA
# =============================================================================

if __name__ == "__main__":
    """
    Ponto de entrada principal do programa.
    
    Esta condição garante que o código só seja executado quando
    o arquivo for executado diretamente, não quando importado
    como módulo em outro programa.
    
    Execução:
    python Entrevista_Tecnica_Transcrita.py
    """
    main()