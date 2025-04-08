import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telefone TEXT,
                    valor REAL,
                    descricao TEXT,
                    categoria TEXT,
                    data_hora TEXT
                )''')
    conn.commit()
    conn.close()

def insert_gasto(telefone, valor, descricao, categoria):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("INSERT INTO gastos (telefone, valor, descricao, categoria, data_hora) VALUES (?, ?, ?, ?, ?)",
              (telefone, valor, descricao, categoria, data_hora))
    conn.commit()
    conn.close()

def get_resumo(telefone, periodo="hoje"):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    if periodo == "hoje":
        data = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT valor, descricao, categoria, data_hora FROM gastos WHERE telefone=? AND data_hora LIKE ?", (telefone, f"{data}%"))
    elif periodo == "semana":
        c.execute("SELECT valor, descricao, categoria, data_hora FROM gastos WHERE telefone=? AND date(data_hora) >= date('now', '-6 days')", (telefone,))
    elif periodo == "mes":
        c.execute("SELECT valor, descricao, categoria, data_hora FROM gastos WHERE telefone=? AND strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now')", (telefone,))
    else:
        conn.close()
        return "❌ Período inválido."

    resultados = c.fetchall()
    conn.close()

    if not resultados:
        return "📭 Nenhum gasto encontrado nesse período."

    total = sum([r[0] for r in resultados])
    detalhes = "\n".join([f"- R${r[0]:.2f} {r[1]} ({r[2]}) em {r[3]}" for r in resultados])
    return f"📊 Total gasto no período ({periodo}): R${total:.2f}\n{detalhes}"

def check_limite(telefone):
    return ""