# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento de Atividade do Computador (CSV)
=========================================================

Monitora continuamente as atividades do usuário no computador,
rastreando qual aplicativo ou janela está ativa e por quanto tempo.
Os dados são salvos em arquivo CSV para análise posterior.

Funcionalidades:
- Monitoramento em tempo real de janelas ativas
- Registro de tempo de uso por aplicativo/URL
- Salvamento automático em arquivo CSV

Dependências necessárias:
- psutil
- pygetwindow
- pandas

Criado em: 28/06/2025
Autor: Francisco H. Lomas
Versão: 1.0
"""

import psutil
import time
import datetime
import pygetwindow as gw
import pandas as pd
import os

# =============================================================================
# CONFIGURAÇÕES DO SISTEMA
# =============================================================================

RECORD_INTERVAL_SECONDS = 5
OUTPUT_FILE = "activity_log.csv"

# =============================================================================
# VARIÁVEIS DE RASTREAMENTO
# =============================================================================

activity_log = []
current_active_window = None
session_start_time = None

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_active_application_info():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return active_window.title
    except Exception:
        return None
    return None

def save_log_to_csv():
    try:
        df = pd.DataFrame(activity_log)
        # Se o arquivo já existe, faz append sem cabeçalho
        if os.path.exists(OUTPUT_FILE):
            df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False, encoding='utf-8')
        else:
            df.to_csv(OUTPUT_FILE, mode='w', header=True, index=False, encoding='utf-8')
        print(f"Log salvo em {OUTPUT_FILE}")
    except Exception as e:
        print(f"Erro ao salvar log em CSV: {e}")

# =============================================================================
# LÓGICA PRINCIPAL DE MONITORAMENTO
# =============================================================================

def main():
    global current_active_window, session_start_time, activity_log

    print("Sistema de Monitoramento de Atividade do Computador (CSV)")
    print("=" * 60)
    print(f"Intervalo de verificação: {RECORD_INTERVAL_SECONDS} segundos")
    print(f"Arquivo de backup: {OUTPUT_FILE}")
    print("=" * 60)
    print("Iniciando rastreamento de atividade. Pressione Ctrl+C para parar.")
    print("-" * 60)

    try:
        while True:
            timestamp_now = datetime.datetime.now()
            current_app_info = get_active_application_info()

            if current_app_info != current_active_window:
                if current_active_window is not None and session_start_time is not None:
                    duration_seconds = (timestamp_now - session_start_time).total_seconds()
                    activity_log.append({
                        "timestamp_end": timestamp_now.isoformat(),
                        "application_or_url": current_active_window,
                        "duration_seconds": round(duration_seconds, 2)
                    })
                    print(f"Log: {current_active_window} por {round(duration_seconds, 2)} segundos")
                    save_log_to_csv()
                    activity_log = []  # Limpa após salvar

                current_active_window = current_app_info
                session_start_time = timestamp_now
                print(f"Ativo agora: {current_active_window} em {timestamp_now.isoformat()}")

            time.sleep(RECORD_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n" + "-" * 60)
        print("Interrupção detectada. Finalizando monitoramento...")

        if current_active_window is not None and session_start_time is not None:
            duration_seconds = (datetime.datetime.now() - session_start_time).total_seconds()
            activity_log.append({
                "timestamp_end": datetime.datetime.now().isoformat(),
                "application_or_url": current_active_window,
                "duration_seconds": round(duration_seconds, 2)
            })
            print(f"Log da sessão final: {current_active_window} por {round(duration_seconds, 2)} segundos")
            save_log_to_csv()

        print("\n" + "=" * 60)
        print("MONITORAMENTO FINALIZADO")
        print("=" * 60)
        print(f"Arquivo de backup: {OUTPUT_FILE}")
        print("=" * 60)

# =============================================================================
# PONTO DE ENTRADA DO PROGRAMA
# =============================================================================

if __name__ == "__main__":
    main()
