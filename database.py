import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("gastos.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY,
    phone TEXT,
    valor REAL,
    descricao TEXT,
    data TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS limites (
    phone TEXT PRIMARY KEY,
    limite REAL
)
""")
conn.commit()

def insert_gasto(phone, valor, descricao):
    cursor.execute("INSERT INTO gastos (phone, valor, descricao, data) VALUES (?, ?, ?, ?)",
                   (phone, valor, descricao, datetime.now().isoformat()))
    conn.commit()

def get_resumo(phone, periodo):
    now = datetime.now()
    if periodo == "semana":
        inicio = now - timedelta(days=7)
    elif periodo == "mês":
        inicio = now.replace(day=1)
    else:
        inicio = now.replace(hour=0, minute=0, second=0, microsecond=0)

    cursor.execute("SELECT valor, descricao, data FROM gastos WHERE phone = ? AND data >= ?",
                   (phone, inicio.isoformat()))
    rows = cursor.fetchall()
    total = sum([r[0] for r in rows])
    linhas = "\n".join([f"- R${r[0]:.2f} {r[1]}" for r in rows])
    return f"📊 Resumo {periodo}:\n{linhas}\n\nTotal: R${total:.2f}"

def set_limite(phone, valor):
    cursor.execute("REPLACE INTO limites (phone, limite) VALUES (?, ?)", (phone, valor))
    conn.commit()

def check_limite(phone):
    cursor.execute("SELECT limite FROM limites WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    if not row:
        return ""
    limite = row[0]

    cursor.execute("SELECT SUM(valor) FROM gastos WHERE phone = ? AND data >= ?",
                   (phone, datetime.now().replace(day=1).isoformat()))
    total = cursor.fetchone()[0] or 0

    if total > limite:
        return f"🚨 Você ultrapassou o limite mensal de R${limite:.2f}!"
    elif total > limite * 0.9:
        return f"⚠️ Atenção: Você já usou mais de 90% do limite mensal."
    return ""