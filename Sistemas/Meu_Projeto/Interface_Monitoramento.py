# -*- coding: utf-8 -*-
"""
Interface Gráfica para Sistema de Monitoramento de Atividade
============================================================

Esta interface permite controlar o programa de monitoramento de atividade
do computador de forma visual, com botões para iniciar/parar o monitoramento
e uma área de texto para exibir logs em tempo real.

Funcionalidades:
- Iniciar/parar monitoramento com botões
- Exibição de logs em tempo real
- Controle visual do status do sistema
- Interface simples e intuitiva

Dependências:
- tkinter (incluído no Python)
- threading (para execução paralela)
- Meu_Dia.py (script principal de monitoramento)

Criado em: 28/06/2025
Autor: Francisco H. Lomas
Versão: 1.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import datetime
import os
import sys
from pathlib import Path

# Importar funções do script principal
try:
    # Adicionar o diretório atual ao path para importar Meu_Dia
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    
    # Importar funções específicas do Meu_Dia.py
    import Meu_Dia
except ImportError as e:
    print(f"Erro ao importar Meu_Dia.py: {e}")
    print("Certifique-se de que o arquivo Meu_Dia.py está no mesmo diretório.")

class InterfaceMonitoramento:
    """
    Interface gráfica para controle do sistema de monitoramento.
    
    Esta classe cria uma janela com controles para iniciar/parar
    o monitoramento e exibir logs em tempo real.
    """
    
    def __init__(self, root):
        """
        Inicializa a interface gráfica.
        
        Args:
            root: Janela principal do tkinter
        """
        self.root = root
        self.root.title("Sistema de Monitoramento de Atividade")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.monitoramento_ativo = False
        self.thread_monitoramento = None
        self.ultima_atividade = None
        self.contador_atividades = 0
        
        # Configurar interface
        self.configurar_interface()
        
        # Inicializar variáveis globais do Meu_Dia
        self.inicializar_variaveis_monitoramento()
        
        # Configurar atualização de logs
        self.atualizar_logs()
    
    def configurar_interface(self):
        """Configura todos os elementos da interface gráfica."""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Sistema de Monitoramento de Atividade", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controles_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botão Iniciar
        self.btn_iniciar = ttk.Button(controles_frame, text="▶ Iniciar Monitoramento", 
                                     command=self.iniciar_monitoramento, style="Accent.TButton")
        self.btn_iniciar.grid(row=0, column=0, padx=(0, 10))
        
        # Botão Parar
        self.btn_parar = ttk.Button(controles_frame, text="⏹ Parar Monitoramento", 
                                   command=self.parar_monitoramento, state="disabled")
        self.btn_parar.grid(row=0, column=1, padx=(0, 10))
        
        # Botão Limpar Logs
        self.btn_limpar = ttk.Button(controles_frame, text="🗑 Limpar Logs", 
                                    command=self.limpar_logs)
        self.btn_limpar.grid(row=0, column=2, padx=(0, 10))
        
        # Status
        self.lbl_status = ttk.Label(controles_frame, text="Status: Parado", 
                                   font=("Arial", 10, "bold"))
        self.lbl_status.grid(row=0, column=3, padx=(20, 0))
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Labels de informação
        self.lbl_atividade_atual = ttk.Label(info_frame, text="Atividade Atual: Nenhuma")
        self.lbl_atividade_atual.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.lbl_contador = ttk.Label(info_frame, text="Atividades Registradas: 0")
        self.lbl_contador.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.lbl_tempo_execucao = ttk.Label(info_frame, text="Tempo de Execução: 00:00:00")
        self.lbl_tempo_execucao.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Frame de logs
        logs_frame = ttk.LabelFrame(main_frame, text="Logs em Tempo Real", padding="10")
        logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Área de texto para logs
        self.text_logs = scrolledtext.ScrolledText(logs_frame, height=15, width=80, 
                                                 font=("Consolas", 9))
        self.text_logs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de rodapé
        rodape_frame = ttk.Frame(main_frame)
        rodape_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Informações do rodapé
        self.lbl_rodape = ttk.Label(rodape_frame, 
                                   text="Pressione 'Iniciar Monitoramento' para começar a rastrear atividades")
        self.lbl_rodape.grid(row=0, column=0, sticky=tk.W)
        
        # Configurar estilos
        self.configurar_estilos()
    
    def configurar_estilos(self):
        """Configura estilos visuais da interface."""
        style = ttk.Style()
        
        # Estilo para botão de iniciar (verde)
        style.configure("Accent.TButton", 
                       background="#28a745", 
                       foreground="white")
    
    def inicializar_variaveis_monitoramento(self):
        """Inicializa variáveis globais do script de monitoramento."""
        try:
            # Importar variáveis do Meu_Dia
            Meu_Dia.executando = False
            Meu_Dia.activity_log = []
            Meu_Dia.current_active_window = None
            Meu_Dia.session_start_time = None
            Meu_Dia.contador_screenshots = 0
            
            self.tempo_inicio = None
            self.adicionar_log("Sistema inicializado. Pronto para monitoramento.")
            
        except Exception as e:
            self.adicionar_log(f"Erro ao inicializar variáveis: {e}")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento de atividade em uma thread separada."""
        if self.monitoramento_ativo:
            return
        
        try:
            # Configurar interface
            self.monitoramento_ativo = True
            self.btn_iniciar.config(state="disabled")
            self.btn_parar.config(state="normal")
            self.lbl_status.config(text="Status: Monitorando", foreground="green")
            
            # Inicializar variáveis
            self.tempo_inicio = datetime.datetime.now()
            self.contador_atividades = 0
            self.ultima_atividade = None
            
            # Inicializar variáveis do Meu_Dia
            Meu_Dia.executando = True
            Meu_Dia.activity_log = []
            Meu_Dia.current_active_window = None
            Meu_Dia.session_start_time = None
            
            # Iniciar thread de monitoramento
            self.thread_monitoramento = threading.Thread(target=self.executar_monitoramento, daemon=True)
            self.thread_monitoramento.start()
            
            self.adicionar_log("Monitoramento iniciado com sucesso!")
            self.lbl_rodape.config(text="Monitoramento ativo. Pressione 'Parar Monitoramento' para finalizar.")
            
        except Exception as e:
            self.adicionar_log(f"Erro ao iniciar monitoramento: {e}")
            self.parar_monitoramento()
    
    def parar_monitoramento(self):
        """Para o monitoramento de atividade."""
        if not self.monitoramento_ativo:
            return
        
        try:
            # Parar monitoramento
            Meu_Dia.executando = False
            
            # Aguardar thread terminar
            if self.thread_monitoramento and self.thread_monitoramento.is_alive():
                self.thread_monitoramento.join(timeout=2)
            
            # Registrar última atividade se houver
            if Meu_Dia.current_active_window and Meu_Dia.session_start_time:
                duracao = (datetime.datetime.now() - Meu_Dia.session_start_time).total_seconds()
                Meu_Dia.activity_log.append({
                    "timestamp_end": datetime.datetime.now().isoformat(),
                    "application_or_url": Meu_Dia.current_active_window,
                    "duration_seconds": round(duracao, 2)
                })
                self.adicionar_log(f"Sessão final: {Meu_Dia.current_active_window} por {round(duracao, 2)}s")
            
            # Salvar dados
            if Meu_Dia.activity_log:
                try:
                    Meu_Dia.save_log_to_json()
                    Meu_Dia.create_dataframe_and_insert_into_mysql(Meu_Dia.activity_log)
                    self.adicionar_log(f"Dados salvos: {len(Meu_Dia.activity_log)} atividades registradas")
                except Exception as e:
                    self.adicionar_log(f"Erro ao salvar dados: {e}")
            
            # Configurar interface
            self.monitoramento_ativo = False
            self.btn_iniciar.config(state="normal")
            self.btn_parar.config(state="disabled")
            self.lbl_status.config(text="Status: Parado", foreground="red")
            
            self.adicionar_log("Monitoramento finalizado.")
            self.lbl_rodape.config(text="Monitoramento parado. Pressione 'Iniciar Monitoramento' para recomeçar.")
            
        except Exception as e:
            self.adicionar_log(f"Erro ao parar monitoramento: {e}")
    
    def executar_monitoramento(self):
        """Executa o loop principal de monitoramento."""
        try:
            self.adicionar_log("Iniciando loop de monitoramento...")
            
            while Meu_Dia.executando:
                # Obter atividade atual
                timestamp_now = datetime.datetime.now()
                current_app_info = Meu_Dia.get_active_application_info()
                
                # Verificar mudança de atividade
                if current_app_info != Meu_Dia.current_active_window:
                    # Registrar atividade anterior
                    if Meu_Dia.current_active_window and Meu_Dia.session_start_time:
                        duration_seconds = (timestamp_now - Meu_Dia.session_start_time).total_seconds()
                        Meu_Dia.activity_log.append({
                            "timestamp_end": timestamp_now.isoformat(),
                            "application_or_url": Meu_Dia.current_active_window,
                            "duration_seconds": round(duration_seconds, 2)
                        })
                        
                        # Atualizar contador
                        self.contador_atividades += 1
                        
                        # Log da atividade
                        self.adicionar_log(f"Atividade: {Meu_Dia.current_active_window} ({round(duration_seconds, 2)}s)")
                    
                    # Iniciar nova sessão
                    Meu_Dia.current_active_window = current_app_info
                    Meu_Dia.session_start_time = timestamp_now
                    
                    if current_app_info:
                        self.adicionar_log(f"Nova atividade: {current_app_info}")
                
                # Aguardar próximo intervalo
                time.sleep(Meu_Dia.RECORD_INTERVAL_SECONDS)
                
        except Exception as e:
            self.adicionar_log(f"Erro no loop de monitoramento: {e}")
    
    def adicionar_log(self, mensagem):
        """Adiciona uma mensagem ao log com timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}\n"
        
        # Adicionar à área de texto (thread-safe)
        self.root.after(0, self._adicionar_log_thread_safe, log_entry)
    
    def _adicionar_log_thread_safe(self, log_entry):
        """Adiciona log de forma thread-safe."""
        self.text_logs.insert(tk.END, log_entry)
        self.text_logs.see(tk.END)  # Rolar para o final
    
    def limpar_logs(self):
        """Limpa a área de logs."""
        self.text_logs.delete(1.0, tk.END)
        self.adicionar_log("Logs limpos.")
    
    def atualizar_logs(self):
        """Atualiza informações da interface periodicamente."""
        try:
            # Atualizar contador de atividades
            self.lbl_contador.config(text=f"Atividades Registradas: {self.contador_atividades}")
            
            # Atualizar atividade atual
            if Meu_Dia.current_active_window:
                self.lbl_atividade_atual.config(text=f"Atividade Atual: {Meu_Dia.current_active_window}")
            else:
                self.lbl_atividade_atual.config(text="Atividade Atual: Nenhuma")
            
            # Atualizar tempo de execução
            if self.tempo_inicio and self.monitoramento_ativo:
                tempo_decorrido = datetime.datetime.now() - self.tempo_inicio
                horas = int(tempo_decorrido.total_seconds() // 3600)
                minutos = int((tempo_decorrido.total_seconds() % 3600) // 60)
                segundos = int(tempo_decorrido.total_seconds() % 60)
                self.lbl_tempo_execucao.config(text=f"Tempo de Execução: {horas:02d}:{minutos:02d}:{segundos:02d}")
            
        except Exception as e:
            print(f"Erro ao atualizar logs: {e}")
        
        # Agendar próxima atualização (a cada 1 segundo)
        self.root.after(1000, self.atualizar_logs)
    
    def on_closing(self):
        """Função chamada quando a janela é fechada."""
        if self.monitoramento_ativo:
            if messagebox.askokcancel("Sair", "O monitoramento está ativo. Deseja parar e sair?"):
                self.parar_monitoramento()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Função principal para executar a interface."""
    try:
        # Criar janela principal
        root = tk.Tk()
        
        # Criar interface
        app = InterfaceMonitoramento(root)
        
        # Configurar fechamento da janela
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Iniciar loop da interface
        root.mainloop()
        
    except Exception as e:
        print(f"Erro ao executar interface: {e}")
        messagebox.showerror("Erro", f"Erro ao executar interface: {e}")

if __name__ == "__main__":
    main() 