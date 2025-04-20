import mysql.connector
import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# === Conexão com o banco MySQL ===
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="38724300",
    database="herois_universo"
)
cursor = conn.cursor()
cursor.execute("SELECT nome_alter_ego, genero, raca FROM alter_egos")
dados = cursor.fetchall()
df_mysql = pd.DataFrame(dados, columns=["Title", "Genero", "Raca"])

# === Conexão com SharePoint ===
site_url = "https://7g7d7p.sharepoint.com/sites/XscientGroup"
username = "franciscolomas@xscient.com.br"
password = "Xscient@"
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