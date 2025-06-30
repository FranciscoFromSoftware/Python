import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector

# --- CONEXÃO COM O BANCO ---
def conectar_banco():
    return mysql.connector.connect(
        host='',
        user='',
        password='',
        database=''
    )

# --- FUNÇÕES DE SALVAR ---
def salvar_alter_ego():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        sql = """
            INSERT INTO alter_egos 
            (nome_alter_ego, genero, raca, descricao_poderes, nome_heroi)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (
            entry_nome_ego.get(),
            combo_genero.get(),
            entry_raca.get(),
            entry_descricao_poderes.get("1.0", tk.END).strip(),
            entry_nome_heroi.get()
        )
        cursor.execute(sql, valores)
        conn.commit()
        messagebox.showinfo("✅ Sucesso", "Alter Ego registrado com sucesso!")
        limpar_campos([entry_nome_ego, entry_raca, entry_nome_heroi], entry_descricao_poderes, combo_genero)
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Erro ao inserir: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def salvar_local():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        sql = """
            INSERT INTO Locais_Criticos 
            (Nome, Tipo, Coordenadas, Descricao, Personagens_Associados, Alinhamento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            entry_nome_local.get(),
            entry_tipo.get(),
            entry_coordenadas.get(),
            entry_descricao_local.get("1.0", tk.END).strip(),
            entry_personagens.get(),
            combo_alinhamento.get()
        )
        cursor.execute(sql, valores)
        conn.commit()
        messagebox.showinfo("✅ Sucesso", "Local registrado com sucesso!")
        limpar_campos([entry_nome_local, entry_tipo, entry_coordenadas, entry_personagens], entry_descricao_local, combo_alinhamento)
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Erro ao inserir: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def salvar_vilao():
    try:
        nivel_periculosidade = int(entry_nivel_periculosidade.get())
        if nivel_periculosidade < 1 or nivel_periculosidade > 5:
            raise ValueError("Nível de Periculosidade deve ser entre 1 e 5.")
        conn = conectar_banco()
        cursor = conn.cursor()
        sql = """
            INSERT INTO Viloes 
            (Nome, Codinome, Crimes_Conhecidos, Nivel_Periculosidade, Ultima_Aparicao, Status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            entry_nome_vilao.get(),
            entry_codinome.get(),
            entry_crimes_conhecidos.get("1.0", tk.END).strip(),
            nivel_periculosidade,
            entry_ultima_aparicao.get(),
            combo_status.get()
        )
        cursor.execute(sql, valores)
        conn.commit()
        messagebox.showinfo("✅ Sucesso", "Vilão registrado com sucesso!")
        limpar_campos([entry_nome_vilao, entry_codinome, entry_ultima_aparicao, entry_nivel_periculosidade], entry_crimes_conhecidos, combo_status)
    except ValueError as ve:
        messagebox.showerror("❌ Erro", f"Nível de Periculosidade inválido: {ve}")
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Erro ao inserir: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# --- FUNÇÃO PARA LIMPAR CAMPOS ---
def limpar_campos(entries, text_widget=None, combo=None):
    for entry in entries:
        entry.delete(0, tk.END)
    if text_widget:
        text_widget.delete("1.0", tk.END)
    if combo:
        combo.set('')

# --- JANELA PRINCIPAL ---
janela = tk.Tk()
janela.title("ORÁCULO - Sistema Unificado")
janela.geometry("800x600")
janela.resizable(False, False)

# --- ABAS ---
abas = ttk.Notebook(janela)
abas.pack(fill="both", expand=True)

# --- FUNÇÃO PARA ADICIONAR IMAGEM DE FUNDO ---
def adicionar_imagem_fundo(frame, caminho_imagem):
    imagem = Image.open(caminho_imagem)
    imagem = imagem.resize((800, 600))
    bg = ImageTk.PhotoImage(imagem)
    label_bg = tk.Label(frame, image=bg)
    label_bg.image = bg  # Manter referência
    label_bg.place(x=0, y=0, relwidth=1, relheight=1)

# --- ABA ALTER EGOS ---
aba_ego = tk.Frame(abas)
abas.add(aba_ego, text="Alter Egos")

# Imagem de fundo
imagem_ego = Image.open(r"C:\Users\franc\OneDrive - Xscient\Arquivos Xscient\VScode\Projeto_Heroes_Sistema\Interface\BackgroundSystemAlterEgos.png")
imagem_ego = imagem_ego.resize((800, 600))
bg_ego = ImageTk.PhotoImage(imagem_ego)
canvas_ego = tk.Canvas(aba_ego, width=800, height=600)
canvas_ego.pack(fill="both", expand=True)
canvas_ego.create_image(0, 0, image=bg_ego, anchor="nw")

# Frame centralizado
frame_ego = tk.Frame(aba_ego, bg="#0F1523", width=400, height=500)
frame_ego.pack_propagate(False)
frame_ego.place(relx=0.5, rely=0.5, anchor="center")
aba_ego.bg_ref = bg_ego  # Para evitar garbage collection

def criar_label_entry_ego(texto):
    tk.Label(frame_ego, text=texto, fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
    entry = tk.Entry(frame_ego, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
    entry.pack()
    return entry

entry_nome_ego = criar_label_entry_ego("Nome do Alter Ego")
tk.Label(frame_ego, text="Gênero", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
combo_genero = ttk.Combobox(frame_ego, values=["Masculino", "Feminino", "Outro"], width=42, font=("Consolas", 11))
combo_genero.pack()

entry_raca = criar_label_entry_ego("Raça")

tk.Label(frame_ego, text="Descrição dos Poderes", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
entry_descricao_poderes = tk.Text(frame_ego, height=4, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
entry_descricao_poderes.pack()

entry_nome_heroi = criar_label_entry_ego("Nome do Herói")

tk.Button(frame_ego, text="💾 Salvar Alter Ego", command=salvar_alter_ego,
          bg="#152A3B", fg="#51FAF7", font=("Consolas", 11, "bold")).pack(pady=20)


# --- ABA LOCAIS CRÍTICOS ---
aba_local = tk.Frame(abas)
abas.add(aba_local, text="Locais Críticos")

# Imagem de fundo
imagem_local = Image.open(r"C:\Users\franc\OneDrive - Xscient\Arquivos Xscient\VScode\Projeto_Heroes_Sistema\Interface\BackgroundSystemLocalCritico.png")
imagem_local = imagem_local.resize((800, 600))
bg_local = ImageTk.PhotoImage(imagem_local)
canvas_local = tk.Canvas(aba_local, width=800, height=600)
canvas_local.pack(fill="both", expand=True)
canvas_local.create_image(0, 0, image=bg_local, anchor="nw")

# Frame centralizado
frame_local = tk.Frame(aba_local, bg="#0F1523", width=400, height=550)
frame_local.pack_propagate(False)
frame_local.place(relx=0.5, rely=0.5, anchor="center")
aba_local.bg_ref = bg_local

def criar_label_entry_local(texto):
    tk.Label(frame_local, text=texto, fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
    entry = tk.Entry(frame_local, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
    entry.pack()
    return entry

entry_nome_local = criar_label_entry_local("Nome do Local")
entry_tipo = criar_label_entry_local("Tipo do Local")
entry_coordenadas = criar_label_entry_local("Coordenadas Geográficas")

tk.Label(frame_local, text="Descrição", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
entry_descricao_local = tk.Text(frame_local, height=4, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
entry_descricao_local.pack()

entry_personagens = criar_label_entry_local("Personagens Envolvidos")

tk.Label(frame_local, text="Alinhamento", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
combo_alinhamento = ttk.Combobox(frame_local, values=["Herói", "Vilão", "Neutro"], width=42, font=("Consolas", 11))
combo_alinhamento.pack()

tk.Button(frame_local, text="💾 Salvar Local", command=salvar_local,
          bg="#152A3B", fg="#51FAF7", font=("Consolas", 11, "bold")).pack(pady=20)


# --- ABA VILÕES ---
aba_vilao = tk.Frame(abas)
abas.add(aba_vilao, text="Vilões")

# Imagem de fundo
imagem_vilao = Image.open(r"C:\Users\franc\OneDrive - Xscient\Arquivos Xscient\VScode\Projeto_Heroes_Sistema\Interface\BackgroundSystemCadastroViloes.png")
imagem_vilao = imagem_vilao.resize((800, 600))
bg_vilao = ImageTk.PhotoImage(imagem_vilao)
canvas_vilao = tk.Canvas(aba_vilao, width=800, height=600)
canvas_vilao.pack(fill="both", expand=True)
canvas_vilao.create_image(0, 0, image=bg_vilao, anchor="nw")

# Frame centralizado
frame_vilao = tk.Frame(aba_vilao, bg="#0F1523", width=400, height=550)
frame_vilao.pack_propagate(False)
frame_vilao.place(relx=0.5, rely=0.5, anchor="center")
aba_vilao.bg_ref = bg_vilao

def criar_label_entry_vilao(texto):
    tk.Label(frame_vilao, text=texto, fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
    entry = tk.Entry(frame_vilao, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
    entry.pack()
    return entry

entry_nome_vilao = criar_label_entry_vilao("Nome do Vilão")
entry_codinome = criar_label_entry_vilao("Codinome")

tk.Label(frame_vilao, text="Crimes Conhecidos", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
entry_crimes_conhecidos = tk.Text(frame_vilao, height=4, width=45, font=("Consolas", 11), bg="#152A3B", fg="#51FAF7", insertbackground="#51FAF7")
entry_crimes_conhecidos.pack()

entry_nivel_periculosidade = criar_label_entry_vilao("Nível de Periculosidade (1 a 5)")
entry_ultima_aparicao = criar_label_entry_vilao("Última Aparição (YYYY-MM-DD)")

tk.Label(frame_vilao, text="Status", fg="#51FAF7", bg="#0F1523", font=("Consolas", 11)).pack(pady=(5, 0))
combo_status = ttk.Combobox(frame_vilao, values=["Ativo", "Preso", "Desaparecido"], width=42, font=("Consolas", 11))
combo_status.pack()

tk.Button(frame_vilao, text="💾 Salvar Vilão", command=salvar_vilao,
          bg="#152A3B", fg="#51FAF7", font=("Consolas", 11, "bold")).pack(pady=20)

janela.mainloop()