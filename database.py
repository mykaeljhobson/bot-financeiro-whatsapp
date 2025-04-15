import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT,
            valor REAL,
            descricao TEXT,
            categoria TEXT,
            data_hora TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS limites (
            telefone TEXT PRIMARY KEY,
            limite REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_gasto(telefone, valor, descricao, categoria):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO gastos (telefone, valor, descricao, categoria, data_hora) VALUES (?, ?, ?, ?, ?)",
              (telefone, valor, descricao, categoria, data_hora))
    conn.commit()
    conn.close()

def get_resumo(telefone, periodo):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()

    if periodo == "hoje":
        query = "SELECT descricao, categoria, valor, data_hora FROM gastos WHERE telefone=? AND date(data_hora) = date('now')"
    elif periodo == "semana":
        query = "SELECT descricao, categoria, valor, data_hora FROM gastos WHERE telefone=? AND date(data_hora) >= date('now', '-6 days')"
    elif periodo == "mes":
        query = "SELECT descricao, categoria, valor, data_hora FROM gastos WHERE telefone=? AND strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now')"
    else:
        conn.close()
        return "❌ Período inválido."

    c.execute(query, (telefone,))
    dados = c.fetchall()
    conn.close()

    if not dados:
        return "📭 Nenhum gasto encontrado no período."

    total = sum([float(d[2]) for d in dados])
    linhas = [f"- R${d[2]:.2f} {d[0]} ({d[1]}) em {d[3]}" for d in dados]
    return f"📊 Total gasto no período ({periodo}): R${total:.2f}\n" + "\n".join(linhas)

def set_limite(telefone, limite):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO limites (telefone, limite) VALUES (?, ?)", (telefone, limite))
    conn.commit()
    conn.close()

def check_limite(telefone):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()

    c.execute("SELECT limite FROM limites WHERE telefone=?", (telefone,))
    row = c.fetchone()
    if not row:
        conn.close()
        return ""

    limite = row[0]
    c.execute("SELECT SUM(valor) FROM gastos WHERE telefone=? AND strftime('%Y-%m', data_hora) = strftime('%Y-%m', 'now')", (telefone,))
    total = c.fetchone()[0] or 0

    conn.close()
    if total > limite:
        return f"⚠️ Atenção: você ultrapassou o limite mensal de R${limite:.2f}!"
    return ""