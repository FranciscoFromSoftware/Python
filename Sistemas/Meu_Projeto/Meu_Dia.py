# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento de Atividade do Computador
===================================================

Este sistema monitora continuamente as atividades do usuário no computador,
rastreando qual aplicativo ou janela está ativa e por quanto tempo. Os dados
são salvos em arquivo JSON temporário e posteriormente inseridos em um banco
de dados MySQL para análise e relatórios.

Funcionalidades:
- Monitoramento em tempo real de janelas ativas
- Registro de tempo de uso por aplicativo/URL
- Salvamento automático em arquivo JSON
- Inserção em banco de dados MySQL
- Configuração via variáveis de ambiente (.env)

Dependências necessárias:
- psutil: Para informações do sistema
- pygetwindow: Para captura de janelas ativas
- pandas: Para manipulação de dados
- sqlalchemy: Para conexão com banco de dados
- pymysql: Driver MySQL para Python
- python-dotenv: Para carregar variáveis de ambiente

Requisitos do sistema:
- MySQL rodando localmente ou remotamente
- Permissões de acesso às janelas do sistema
- Arquivo .env configurado com credenciais

Criado em: 28/06/2025
Autor: Francisco H. Lomas
Versão: 1.0
"""

import psutil
import time
import datetime
import json
import pygetwindow as gw
import pandas as pd
from sqlalchemy import create_engine
import pymysql  # Necessário para o SQLAlchemy se conectar ao MySQL
from dotenv import load_dotenv
import os

# =============================================================================
# CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# =============================================================================

# Carrega variáveis de ambiente do arquivo .env
# Isso permite manter credenciais seguras fora do código
load_dotenv()

# Obtém credenciais do banco de dados das variáveis de ambiente
# Formato esperado no arquivo .env:
# LOGIN=seu_usuario_mysql
# PASSWORD=sua_senha_mysql
user = os.getenv("LOGIN")
password = os.getenv("SENHA")

# =============================================================================
# CONFIGURAÇÕES DO SISTEMA
# =============================================================================

# Intervalo entre verificações de atividade (em segundos)
# Valores menores = mais precisão, mas mais uso de CPU
# Valores maiores = menos precisão, mas menos uso de recursos
RECORD_INTERVAL_SECONDS = 5

# Nome do arquivo JSON temporário para armazenar logs
# Este arquivo é usado como backup antes de inserir no banco
OUTPUT_FILE = "activity_log.json"

# Configurações do banco de dados MySQL
DATABASE_HOST = "localhost"          # Host do banco de dados
DATABASE_USER = user                 # Usuário do MySQL (carregado do .env)
DATABASE_PASSWORD = password         # Senha do MySQL (carregado do .env)
DATABASE_NAME = "meus_dados"         # Nome do banco de dados
TABLE_NAME = "uso_aplicativos"       # Nome da tabela onde os dados serão inseridos

# =============================================================================
# VARIÁVEIS DE RASTREAMENTO
# =============================================================================

# Lista para armazenar todas as atividades registradas
# Cada item contém: timestamp_end, application_or_url, duration_seconds
activity_log = []

# Janela/aplicativo atualmente ativo
# Usado para detectar mudanças de atividade
current_active_window = None

# Timestamp de quando a sessão atual começou
# Usado para calcular a duração da atividade
session_start_time = None

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_active_application_info():
    """
    Obtém informações da janela/aplicativo atualmente ativo.
    
    Esta função utiliza pygetwindow para capturar o título da janela
    que está em foco no momento da chamada. É usada para detectar
    mudanças de atividade do usuário.
    
    Returns:
        str or None: Título da janela ativa ou None se não conseguir obter
        
    Observações importantes:
    - Pode retornar None se não houver janela ativa
    - Pode falhar se não tiver permissões adequadas
    - Funciona apenas com janelas visíveis (não minimizadas)
    - Em alguns sistemas, pode não detectar aplicativos em tela cheia
    
    Exemplo de retorno:
        "Documento - Microsoft Word"
        "https://www.google.com - Google Chrome"
        "Visual Studio Code"
        None (se não conseguir detectar)
    """
    try:
        # Obtém a janela que está atualmente em foco
        active_window = gw.getActiveWindow()
        
        if active_window:
            # Retorna o título da janela ativa
            return active_window.title
    except Exception as e:
        # Erros podem ocorrer por várias razões:
        # - Não há janela ativa no momento
        # - Permissões insuficientes
        # - Problemas com drivers de vídeo
        # - Aplicativos em modo de segurança
        
        # Comentado para não poluir o log, mas pode ser útil para debug
        # print(f"Erro ao obter janela ativa: {e}")
        return None
    
    return None

def save_log_to_json():
    """
    Salva o log de atividades em um arquivo JSON temporário.
    
    Esta função cria/atualiza um arquivo JSON com todos os dados
    de atividade coletados até o momento. Serve como backup
    antes da inserção no banco de dados e permite recuperação
    em caso de falha na conexão com o MySQL.
    
    Observações:
    - Arquivo é sobrescrito a cada chamada
    - Encoding UTF-8 para suportar caracteres especiais
    - Formato indentado para fácil leitura
    - Dados são salvos em formato ISO para timestamps
    
    Estrutura do JSON:
    [
        {
            "timestamp_end": "2025-06-28T14:30:15.123456",
            "application_or_url": "Documento - Microsoft Word",
            "duration_seconds": 45.67
        },
        ...
    ]
    """
    try:
        # Abre arquivo em modo de escrita com encoding UTF-8
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # Salva dados em formato JSON indentado
            json.dump(activity_log, f, indent=4, ensure_ascii=False)
        
        print(f"Log salvo temporariamente em {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Erro ao salvar log em JSON: {e}")
        print("Possíveis causas:")
        print("- Sem permissão de escrita no diretório")
        print("- Disco cheio")
        print("- Arquivo aberto por outro programa")

def create_dataframe_and_insert_into_mysql(log_data):
    """
    Cria um DataFrame a partir dos dados do log e os insere no MySQL.
    
    Esta função converte os dados coletados em um DataFrame do pandas
    e os insere em uma tabela MySQL. É o passo final do processo
    de monitoramento, transferindo os dados para armazenamento permanente.
    
    Args:
        log_data (list): Lista de dicionários com dados de atividade
                        Cada dicionário deve ter:
                        - timestamp_end: string ISO
                        - application_or_url: string
                        - duration_seconds: float
    
    Observações importantes:
    - Requer conexão com MySQL ativa
    - Tabela deve existir com colunas corretas
    - Usa 'append' para adicionar dados sem apagar existentes
    - Trata erros de conexão e inserção graciosamente
    
    Estrutura esperada da tabela MySQL:
    CREATE TABLE uso_aplicativos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp_end DATETIME,
        application_or_url VARCHAR(500),
        duration_seconds DECIMAL(10,2)
    );
    
    Exemplo de uso:
        create_dataframe_and_insert_into_mysql(activity_log)
    """
    # Verifica se há dados para inserir
    if not log_data:
        print("Nenhum dado para inserir no banco de dados.")
        return

    # 1. Criar DataFrame a partir dos dados do log
    # pandas.DataFrame converte automaticamente a lista de dicionários
    df = pd.DataFrame(log_data)
    
    # Opcional: Converter timestamp para datetime se necessário
    # Útil para ordenação e operações de data/hora
    # df['timestamp_end'] = pd.to_datetime(df['timestamp_end'])
    
    # Exibe informações sobre o DataFrame criado
    print("\n--- DataFrame Gerado ---")
    print(f"Total de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print("\nPrimeiros registros:")
    print(df.head())
    print("\n")

    # 2. Conectar ao Banco de Dados MySQL
    try:
        # String de conexão no formato SQLAlchemy
        # mysql+pymysql://usuario:senha@host/nome_do_banco
        db_connection_str = f'mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'
        
        # Cria engine de conexão
        db_connection = create_engine(db_connection_str)

        # 3. Inserir DataFrame no MySQL
        # if_exists='append': adiciona novas linhas sem apagar existentes
        # if_exists='replace': apaga a tabela e recria (CUIDADO!)
        # index=False: não inclui índice do DataFrame como coluna
        df.to_sql(TABLE_NAME, con=db_connection, if_exists='append', index=False)
        
        print(f"Dados inseridos com sucesso na tabela '{TABLE_NAME}' do MySQL.")
        print(f"Total de registros inseridos: {len(df)}")

    except Exception as e:
        # Tratamento detalhado de erros
        print(f"Erro ao conectar ou inserir no MySQL: {e}")
        print("\nPossíveis causas e soluções:")
        print("1. Verifique se o MySQL está rodando")
        print("2. Confirme as credenciais no arquivo .env")
        print("3. Verifique se o banco de dados existe")
        print("4. Confirme se a tabela tem as colunas corretas")
        print("5. Verifique se 'if_exists' está como 'append'")
        print("\nDados salvos em JSON como backup.")

# =============================================================================
# LÓGICA PRINCIPAL DE MONITORAMENTO
# =============================================================================

def main():
    """
    Função principal que executa o monitoramento de atividade.
    
    Esta função implementa o loop principal de monitoramento,
    verificando periodicamente qual aplicativo está ativo e
    registrando as mudanças de atividade com suas durações.
    
    Fluxo de execução:
    1. Inicialização e configuração
    2. Loop de monitoramento contínuo
    3. Detecção de mudanças de atividade
    4. Registro de sessões completadas
    5. Salvamento em JSON e MySQL
    
    Observações importantes:
    - Loop infinito até interrupção manual (Ctrl+C)
    - Registra apenas mudanças de atividade (não tempo contínuo)
    - Salva dados em JSON a cada mudança
    - Insere no MySQL apenas ao final
    
    Exemplo de uso:
        if __name__ == "__main__":
            main()
    """
    global current_active_window, session_start_time, activity_log
    
    print("Sistema de Monitoramento de Atividade do Computador")
    print("=" * 60)
    print("Este sistema irá monitorar:")
    print("1. Qual aplicativo/janela está ativo")
    print("2. Por quanto tempo cada atividade durou")
    print("3. Salvar dados em JSON e MySQL")
    print("=" * 60)
    print(f"Intervalo de verificação: {RECORD_INTERVAL_SECONDS} segundos")
    print(f"Arquivo de backup: {OUTPUT_FILE}")
    print(f"Banco de dados: {DATABASE_NAME}.{TABLE_NAME}")
    print("=" * 60)
    print("Iniciando rastreamento de atividade. Pressione Ctrl+C para parar.")
    print("-" * 60)

    try:
        # Loop principal de monitoramento
        while True:
            # Obtém timestamp atual e aplicativo ativo
            timestamp_now = datetime.datetime.now()
            current_app_info = get_active_application_info()

            # Verifica se houve mudança de atividade
            if current_app_info != current_active_window:
                # Se havia uma atividade anterior, registra ela
                if current_active_window is not None and session_start_time is not None:
                    # Calcula duração da sessão anterior
                    duration_seconds = (timestamp_now - session_start_time).total_seconds()
                    
                    # Adiciona à lista de atividades
                    activity_log.append({
                        "timestamp_end": timestamp_now.isoformat(),
                        "application_or_url": current_active_window,
                        "duration_seconds": round(duration_seconds, 2)
                    })
                    
                    # Exibe informação no console
                    print(f"Log: {current_active_window} por {round(duration_seconds, 2)} segundos")
                    
                    # Salva backup em JSON
                    save_log_to_json()

                # Inicia nova sessão
                current_active_window = current_app_info
                session_start_time = timestamp_now
                
                # Exibe nova atividade
                print(f"Ativo agora: {current_active_window} em {timestamp_now.isoformat()}")
            
            # Aguarda próximo intervalo de verificação
            time.sleep(RECORD_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        # Tratamento de interrupção manual (Ctrl+C)
        print("\n" + "-" * 60)
        print("Interrupção detectada. Finalizando monitoramento...")
        
        # Registra a última sessão ativa
        if current_active_window is not None and session_start_time is not None:
            duration_seconds = (datetime.datetime.now() - session_start_time).total_seconds()
            activity_log.append({
                "timestamp_end": datetime.datetime.now().isoformat(),
                "application_or_url": current_active_window,
                "duration_seconds": round(duration_seconds, 2)
            })
            print(f"Log da sessão final: {current_active_window} por {round(duration_seconds, 2)} segundos")
        
        # Salva log final
        save_log_to_json()
        print("Rastreamento de atividade parado.")
        
        # Insere dados no MySQL
        print("\nInserindo dados no banco de dados...")
        create_dataframe_and_insert_into_mysql(activity_log)
        
        # Resumo final
        print("\n" + "=" * 60)
        print("MONITORAMENTO FINALIZADO")
        print("=" * 60)
        print(f"Total de atividades registradas: {len(activity_log)}")
        print(f"Arquivo de backup: {OUTPUT_FILE}")
        print(f"Dados inseridos em: {DATABASE_NAME}.{TABLE_NAME}")
        print("=" * 60)

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
    python Meu_Dia.py
    
    Pré-requisitos:
    - Arquivo .env configurado com LOGIN e PASSWORD
    - MySQL rodando e acessível
    - Tabela 'uso_aplicativos' criada no banco 'meus_dados'
    """
    main()