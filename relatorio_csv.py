import pandas as pd
import sqlite3
import tempfile

def gerar_planilha_csv(periodo="mes", telefone=None):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()

    # Para testes: ignora o filtro de data e retorna tudo do telefone
    query = "SELECT data_hora, descricao, categoria, valor FROM gastos WHERE telefone=?"
    c.execute(query, (telefone,))

    dados = c.fetchall()
    conn.close()

    if not dados:
        return None

    df = pd.DataFrame(dados, columns=["Data/Hora", "Descrição", "Categoria", "Valor (R$)"])
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(temp.name, index=False)
    return temp.name