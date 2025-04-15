import pandas as pd
import sqlite3
import tempfile

def gerar_planilha_csv(periodo="mes", telefone=None):
    if telefone and telefone.startswith("whatsapp:"):
        telefone = telefone.replace("whatsapp:", "")

    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()

    if periodo == "hoje":
        query = "SELECT data_hora, descricao, categoria, valor FROM gastos WHERE telefone=? AND date(data_hora) = date('now')"
        c.execute(query, (telefone,))
    elif periodo == "semana":
        query = "SELECT data_hora, descricao, categoria, valor FROM gastos WHERE telefone=? AND date(data_hora) >= date('now', '-6 days')"
        c.execute(query, (telefone,))
    elif periodo == "mes":
        query = "SELECT data_hora, descricao, categoria, valor FROM gastos WHERE telefone=? AND strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now')"
        c.execute(query, (telefone,))
    else:
        conn.close()
        return None

    dados = c.fetchall()
    conn.close()

    if not dados:
        return None

    df = pd.DataFrame(dados, columns=["Data/Hora", "Descrição", "Categoria", "Valor (R$)"])
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(temp.name, index=False)
    return temp.name