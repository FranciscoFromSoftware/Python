"""
ConectorMySQL_List.py
Este script realiza a integração entre um banco de dados MySQL e uma lista do SharePoint. 
Ele extrai dados do banco MySQL, apaga todos os itens existentes em uma lista do SharePoint 
e insere os novos dados extraídos.
Dependências:
- mysql-connector-python
- pandas
- office365-rest-python-client
Funcionalidades:
1. Conexão com um banco de dados MySQL para extrair dados de uma tabela específica.
2. Conexão com um site do SharePoint para manipular uma lista.
3. Exclusão de todos os itens existentes na lista do SharePoint.
4. Inserção de novos dados do MySQL na lista do SharePoint.
Variáveis e Configurações:
- Conexão MySQL:
    - `host`: Endereço do servidor MySQL.
    - `user`: Nome de usuário para autenticação no MySQL.
    - `password`: Senha para autenticação no MySQL.
    - `database`: Nome do banco de dados a ser acessado.
    - `cursor.execute("SELECT ...")`: Consulta SQL para extrair os dados desejados.
- Conexão SharePoint:
    - `site_url`: URL do site SharePoint.
    - `username`: Nome de usuário para autenticação no SharePoint.
    - `password`: Senha para autenticação no SharePoint.
    - `lista_nome`: Nome da lista no SharePoint onde os dados serão manipulados.
Estrutura do Código:
1. Conexão com o banco de dados MySQL e extração dos dados para um DataFrame do pandas.
2. Conexão com o SharePoint utilizando `ClientContext` e `UserCredential`.
3. Exclusão de todos os itens existentes na lista do SharePoint.
4. Inserção dos dados extraídos do MySQL na lista do SharePoint.
Tratamento de Erros:
- O bloco `try-except` captura e exibe erros relacionados ao acesso ou edição da lista do SharePoint.
Encerramento:
- O bloco `finally` garante o fechamento da conexão com o banco MySQL e o cursor, independentemente de erros.
Notas:
- Certifique-se de preencher as variáveis de conexão (`host`, `user`, `password`, `database`, `site_url`, `username`, `password`) antes de executar o script.
- Verifique se os nomes das colunas no DataFrame correspondem aos campos da lista do SharePoint.
"""
import mysql.connector
import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# === Conexão com o banco MySQL ===
conn = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
cursor = conn.cursor()
cursor.execute("SELECT nome_alter_ego, genero, raca FROM alter_egos")
dados = cursor.fetchall()
df_mysql = pd.DataFrame(dados, columns=["Title", "Genero", "Raca"])

# === Conexão com SharePoint ===
site_url = ""
username = ""
password = ""
lista_nome = "Nomes_Herois"

try:
    # Conectar ao SharePoint
    ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
    lista = ctx.web.lists.get_by_title(lista_nome)
    items = lista.items
    ctx.load(items)
    ctx.execute_query()

    # Apagar todos os itens existentes na lista
    print("Apagando todos os itens existentes na lista...")
    for item in items:
        item.delete_object()
    ctx.execute_query()
    print("Todos os itens foram apagados com sucesso!")

    # Inserir os novos dados do MySQL na lista do SharePoint
    print("Inserindo novos dados na lista...")
    for _, row in df_mysql.iterrows():
        item_properties = {
            "Nome": row["Title"],  # Certifique-se de que 'Title' é o nome correto da coluna no SharePoint
            "Genero": row["Genero"],
            "Raca": row["Raca"]
        }
        lista.add_item(item_properties)
        ctx.execute_query()
    print(f"{len(df_mysql)} novo(s) herói(s) adicionado(s) com sucesso!")

except Exception as e:
    print("Erro ao acessar ou editar a lista do SharePoint:", e)

finally:
    cursor.close()
    conn.close()