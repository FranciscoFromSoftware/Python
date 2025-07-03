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
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Importar funções do script principal
try:
    # Adicionar o diretório atual ao path para importar Meu_Dia
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    import Meu_Dia
except ImportError as e:
    print(f"Erro ao importar Meu_Dia.py: {e}")
    print("Certifique-se de que o arquivo Meu_Dia.py está no mesmo diretório.")

# Importa as funções do sistema de monitoramento
from Meu_Dia import (
    get_active_application_info, 
    save_log_to_json, 
    create_dataframe_and_insert_into_mysql,
    RECORD_INTERVAL_SECONDS,
    OUTPUT_FILE
)

class ConfiguracaoBancoDialog:
    """Dialog para configuração do banco de dados."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # Criar janela de diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuração do Banco de Dados")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar na tela
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.criar_widgets()
        self.carregar_configuracao_atual()
    
    def criar_widgets(self):
        """Cria os widgets da interface de configuração."""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        tk.Label(main_frame, text="Configuração MySQL", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Host
        tk.Label(main_frame, text="Host:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_var = tk.StringVar(value="localhost")
        self.host_entry = tk.Entry(main_frame, textvariable=self.host_var, width=30)
        self.host_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Usuário
        tk.Label(main_frame, text="Usuário:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_var = tk.StringVar()
        self.user_entry = tk.Entry(main_frame, textvariable=self.user_var, width=30)
        self.user_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Senha
        tk.Label(main_frame, text="Senha:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(main_frame, textvariable=self.password_var, 
                                       show="*", width=30)
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Banco de dados
        tk.Label(main_frame, text="Banco:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.database_var = tk.StringVar(value="meus_dados")
        self.database_entry = tk.Entry(main_frame, textvariable=self.database_var, width=30)
        self.database_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Tabela
        tk.Label(main_frame, text="Tabela:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.table_var = tk.StringVar(value="uso_aplicativos")
        self.table_entry = tk.Entry(main_frame, textvariable=self.table_var, width=30)
        self.table_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Testar Conexão", 
                  command=self.testar_conexao).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.salvar_configuracao).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancelar).pack(side=tk.LEFT)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def carregar_configuracao_atual(self):
        """Carrega configuração atual do arquivo .env se existir."""
        try:
            load_dotenv()
            user = os.getenv("LOGIN")
            password = os.getenv("SENHA")
            
            if user:
                self.user_var.set(user)
            if password:
                self.password_var.set(password)
        except:
            pass
    
    def testar_conexao(self):
        """Testa a conexão com o banco de dados."""
        try:
            from sqlalchemy import create_engine, text
            import pymysql
            
            # String de conexão
            connection_str = f'mysql+pymysql://{self.user_var.get()}:{self.password_var.get()}@{self.host_var.get()}/{self.database_var.get()}'
            
            # Testar conexão
            engine = create_engine(connection_str)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            messagebox.showinfo("Sucesso", "Conexão com o banco de dados estabelecida com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na conexão com o banco de dados:\n{str(e)}")
    
    def salvar_configuracao(self):
        """Salva a configuração e fecha o diálogo."""
        if not self.user_var.get() or not self.password_var.get():
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios!")
            return
        
        self.result = {
            'host': self.host_var.get(),
            'user': self.user_var.get(),
            'password': self.password_var.get(),
            'database': self.database_var.get(),
            'table': self.table_var.get()
        }
        
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela a configuração."""
        self.dialog.destroy()

class SistemaMonitoramentoGUI:
    """
    Interface gráfica principal do sistema de monitoramento.
    
    Esta classe cria uma janela com controles para iniciar/parar
    o monitoramento de atividade e exibe logs em tempo real.
    """
    
    def __init__(self, root):
        """
        Inicializa a interface gráfica.
        
        Args:
            root: Widget raiz do tkinter (Tk())
        """
        self.root = root
        self.root.title("Sistema de Monitoramento de Atividade")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.monitoring = False
        self.monitor_thread = None
        self.activity_log = []
        self.current_active_window = None
        self.session_start_time = None
        
        # Configuração do banco de dados
        self.db_config = None
        
        # Criar interface
        self.criar_interface()
        
        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def criar_interface(self):
        """Cria todos os elementos da interface gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Monitoramento de Atividade", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões
        self.start_button = ttk.Button(control_frame, text="Iniciar Monitoramento", 
                                      command=self.iniciar_monitoramento, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Parar Monitoramento", 
                                     command=self.parar_monitoramento, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.config_button = ttk.Button(control_frame, text="Configurar Banco", 
                                       command=self.configurar_banco)
        self.config_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(control_frame, text="Limpar Logs", 
                                      command=self.limpar_logs)
        self.clear_button.pack(side=tk.LEFT)
        
        # Frame de logs
        log_frame = ttk.LabelFrame(main_frame, text="Logs de Atividade", padding="10")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de logs
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80, 
                                                 font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Status
        self.status_label = tk.Label(status_frame, text="Status: Parado", 
                                     font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Contador de atividades
        self.count_label = tk.Label(status_frame, text="Atividades: 0", 
                                    font=("Arial", 10))
        self.count_label.pack(side=tk.RIGHT)
    
    def configurar_banco(self):
        """Abre diálogo para configuração do banco de dados."""
        dialog = ConfiguracaoBancoDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.db_config = dialog.result
            self.adicionar_log("Configuração do banco de dados salva com sucesso!")
            messagebox.showinfo("Sucesso", "Configuração do banco de dados salva!")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento de atividade em uma thread separada."""
        if not self.db_config:
            messagebox.showerror("Erro", "Configure o banco de dados primeiro!")
            return
        
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitorar_atividade, daemon=True)
            self.monitor_thread.start()
            
            # Atualizar interface
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Monitorando")
            
            self.adicionar_log("Monitoramento iniciado!")
    
    def parar_monitoramento(self):
        """Para o monitoramento de atividade."""
        if self.monitoring:
            self.monitoring = False
            
            # Aguardar thread terminar
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
            
            # Registrar última sessão
            if self.current_active_window and self.session_start_time:
                duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
                self.activity_log.append({
                    "timestamp_end": datetime.datetime.now().isoformat(),
                    "application_or_url": self.current_active_window,
                    "duration_seconds": round(duration, 2)
                })
                self.adicionar_log(f"Sessão final: {self.current_active_window} por {round(duration, 2)}s")
            
            # Salvar e inserir no banco
            self.salvar_dados()
            
            # Atualizar interface
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="Status: Parado")
            
            self.adicionar_log("Monitoramento parado!")
    
    def monitorar_atividade(self):
        """Função principal de monitoramento executada em thread separada."""
        while self.monitoring:
            try:
                timestamp_now = datetime.datetime.now()
                current_app_info = get_active_application_info()
                
                # Verifica mudança de atividade
                if current_app_info != self.current_active_window:
                    # Registra sessão anterior
                    if self.current_active_window and self.session_start_time:
                        duration = (timestamp_now - self.session_start_time).total_seconds()
                        self.activity_log.append({
                            "timestamp_end": timestamp_now.isoformat(),
                            "application_or_url": self.current_active_window,
                            "duration_seconds": round(duration, 2)
                        })
                        
                        # Atualiza log na interface
                        self.root.after(0, self.adicionar_log, 
                                       f"Atividade: {self.current_active_window} por {round(duration, 2)}s")
                    
                    # Inicia nova sessão
                    self.current_active_window = current_app_info
                    self.session_start_time = timestamp_now
                    
                    if current_app_info:
                        self.root.after(0, self.adicionar_log, f"Ativo agora: {current_app_info}")
                
                # Atualiza contador
                self.root.after(0, self.atualizar_contador)
                
                time.sleep(RECORD_INTERVAL_SECONDS)
                
            except Exception as e:
                self.root.after(0, self.adicionar_log, f"Erro: {str(e)}")
                time.sleep(RECORD_INTERVAL_SECONDS)
    
    def salvar_dados(self):
        """Salva dados em JSON e insere no banco de dados."""
        try:
            # Salva em JSON
            save_log_to_json()
            self.adicionar_log("Dados salvos em JSON")
            
            # Insere no banco
            if self.db_config:
                # Atualiza configurações globais
                import Meu_Dia
                Meu_Dia.DATABASE_HOST = self.db_config['host']
                Meu_Dia.DATABASE_USER = self.db_config['user']
                Meu_Dia.DATABASE_PASSWORD = self.db_config['password']
                Meu_Dia.DATABASE_NAME = self.db_config['database']
                Meu_Dia.TABLE_NAME = self.db_config['table']
                
                create_dataframe_and_insert_into_mysql(self.activity_log)
                self.adicionar_log("Dados inseridos no banco de dados!")
            
        except Exception as e:
            self.adicionar_log(f"Erro ao salvar dados: {str(e)}")
    
    def adicionar_log(self, mensagem):
        """Adiciona mensagem ao log da interface."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def atualizar_contador(self):
        """Atualiza o contador de atividades."""
        self.count_label.config(text=f"Atividades: {len(self.activity_log)}")
    
    def limpar_logs(self):
        """Limpa a área de logs."""
        self.log_text.delete(1.0, tk.END)
        self.adicionar_log("Logs limpos!")
    
    def on_closing(self):
        """Trata o fechamento da janela."""
        if self.monitoring:
            if messagebox.askokcancel("Sair", "O monitoramento está ativo. Deseja parar e sair?"):
                self.parar_monitoramento()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Função principal para iniciar a interface gráfica."""
    root = tk.Tk()
    app = SistemaMonitoramentoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 