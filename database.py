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