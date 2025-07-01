from dotenv import load_dotenv
import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os # Importar o módulo os para manipular caminhos de arquivo

load_dotenv()

user = os.getenv("LOGIN")
password = os.getenv("PASSWORD")

def gerar_sql_create_table(caminho_excel, nome_tabela):
    """
    Gera um script SQL CREATE TABLE a partir dos cabeçalhos da primeira linha de um arquivo Excel.
    """
    try:
        df = pd.read_excel(caminho_excel, nrows=0)
        colunas = df.columns.tolist()

        if not colunas:
            return "Nenhum cabeçalho de coluna encontrado no arquivo Excel."

        sql_script = f"CREATE TABLE IF NOT EXISTS `{nome_tabela}` (\n" # Adicionado IF NOT EXISTS e backticks

        for i, coluna in enumerate(colunas):
            coluna_sql = ''.join(e for e in coluna if e.isalnum() or e == '_').replace(' ', '_')
            sql_script += f"    `{coluna_sql}` VARCHAR(255)" # Envolva os nomes das colunas com backticks
            if i < len(colunas) - 1:
                sql_script += ",\n"
            else:
                sql_script += "\n"

        sql_script += ");"
        return sql_script

    except FileNotFoundError:
        return f"Erro: O arquivo '{caminho_excel}' não foi encontrado."
    except Exception as e:
        return f"Ocorreu um erro ao gerar o SQL CREATE TABLE: {e}"

def importar_excel_para_mysql(caminho_excel, db_config):
    """
    Importa dados de um arquivo Excel para uma tabela MySQL, usando o nome do arquivo (sem extensão)
    como o nome da tabela.

    Args:
        caminho_excel (str): O caminho completo para o arquivo Excel.
        db_config (dict): Dicionário com as configurações de conexão do MySQL
                          (host, database, user, password).
    """
    # Extrai o nome do arquivo sem o caminho e a extensão para usar como nome da tabela
    nome_base_arquivo = os.path.basename(caminho_excel)
    nome_tabela = os.path.splitext(nome_base_arquivo)[0]

    # Substitui caracteres inválidos para nomes de tabela MySQL (opcional, mas boa prática)
    nome_tabela = ''.join(e for e in nome_tabela if e.isalnum() or e == '_').replace(' ', '_')
    if not nome_tabela: # Se o nome ficar vazio após a limpeza
        print("Erro: O nome da tabela derivado do arquivo Excel está vazio ou inválido.")
        return

    conexao = None
    try:
        # 1. Conectar ao MySQL
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        print("Conexão ao MySQL estabelecida com sucesso!")

        # 2. Gerar e Executar o CREATE TABLE
        create_table_sql = gerar_sql_create_table(caminho_excel, nome_tabela)
        if "Erro:" in create_table_sql or "Nenhum cabeçalho" in create_table_sql:
            print(create_table_sql)
            return

        print(f"\nExecutando SQL para criar a tabela '{nome_tabela}':\n{create_table_sql}")
        cursor.execute(create_table_sql)
        print(f"Tabela '{nome_tabela}' criada (ou já existente).")

        # 3. Ler todos os dados do Excel
        df = pd.read_excel(caminho_excel)

        if df.empty:
            print("O arquivo Excel está vazio. Nenhuma linha para inserir.")
            return

        # 4. Preparar o comando INSERT
        # Renomeia as colunas do DataFrame para corresponder aos nomes de coluna SQL válidos
        df.columns = [''.join(e for e in col if e.isalnum() or e == '_').replace(' ', '_') for col in df.columns]

        colunas_sql = [f"`{col}`" for col in df.columns] # Envolva os nomes das colunas com backticks
        placeholders = ', '.join(['%s'] * len(colunas_sql))
        insert_sql = f"INSERT INTO `{nome_tabela}` ({', '.join(colunas_sql)}) VALUES ({placeholders})" # Use backticks aqui também

        # 5. Inserir dados
        dados_para_inserir = [tuple(row) for row in df.values]

        print(f"\nInserindo {len(dados_para_inserir)} linhas na tabela '{nome_tabela}'...")
        cursor.executemany(insert_sql, dados_para_inserir)
        conexao.commit()
        print(f"Dados inseridos com sucesso! {cursor.rowcount} linhas afetadas.")

    except Error as e:
        print(f"Erro no MySQL: {e}")
    except FileNotFoundError:
        print(f"Erro: O arquivo Excel '{caminho_excel}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()
            print("Conexão ao MySQL fechada.")

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # --- Configurações do seu banco de dados MySQL ---
    db_config = {
        'host': 'localhost',      # Ou o IP do seu servidor MySQL
        'database': 'brasil', # Nome do seu banco de dados
        'user': user,    # Seu usuário do MySQL
        'password': password,   # Sua senha do MySQL
    }

    # --- Caminho do arquivo Excel ---
    # Crie um arquivo Excel de exemplo, por exemplo, 'produtos_junho.xlsx'
    # Ele criará uma tabela chamada 'produtos_junho' no seu MySQL
    caminho_do_seu_excel = r"C:\Users\franc\OneDrive - Xscient\Arquivos Xscient\Power BI\Dados População\Municipio.xlsx" # Altere para o caminho do seu arquivo Excel

    importar_excel_para_mysql(caminho_do_seu_excel, db_config)
