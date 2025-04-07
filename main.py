from database import insert_gasto, get_resumo, set_limite, check_limite

def process_message(msg, phone):
    tokens = msg.lower().split()

    if tokens[0] == "gasto":
        try:
            valor = float(tokens[1])
            descricao = " ".join(tokens[2:])
            insert_gasto(phone, valor, descricao)
            alerta = check_limite(phone)
            return f"✅ Gasto registrado: R${valor:.2f} - {descricao}\n{alerta}"
        except:
            return "❌ Formato inválido. Use: gasto 25 almoço"
    
    elif tokens[0] == "resumo":
        periodo = tokens[1] if len(tokens) > 1 else "hoje"
        return get_resumo(phone, periodo)

    elif tokens[0] == "limite":
        try:
            valor = float(tokens[1])
            set_limite(phone, valor)
            return f"🔒 Limite mensal definido: R${valor:.2f}"
        except:
            return "❌ Use: limite 1500"

    return "🤖 Comandos disponíveis: gasto, resumo [hoje|semana|mês], limite"