import matplotlib.pyplot as plt
import sqlite3
import tempfile
from datetime import datetime

def gerar_grafico_categoria(tipo="pizza"):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("SELECT categoria, SUM(valor) FROM gastos WHERE strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now', 'localtime') GROUP BY categoria")
    dados = c.fetchall()
    conn.close()

    categorias = [row[0] for row in dados]
    valores = [row[1] for row in dados]

    fig, ax = plt.subplots()
    if tipo == "pizza":
        ax.pie(valores, labels=categorias, autopct="%1.1f%%")
        ax.set_title("Gastos por Categoria")
    else:
        ax.bar(categorias, valores)
        ax.set_title("Gastos por Categoria")
        plt.xticks(rotation=45)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.tight_layout()
    plt.savefig(temp.name)
    plt.close()
    return temp.name

def gerar_grafico_diario():
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("SELECT data, SUM(valor) FROM gastos WHERE strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now', 'localtime') GROUP BY data")
    dados = c.fetchall()
    conn.close()

    dias = [row[0][-2:] for row in dados]
    valores = [row[1] for row in dados]

    fig, ax = plt.subplots()
    ax.plot(dias, valores, marker="o")
    ax.set_title("Gastos Diários do Mês")
    ax.set_xlabel("Dia")
    ax.set_ylabel("Total (R$)")
    plt.tight_layout()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp.name)
    plt.close()
    return temp.name