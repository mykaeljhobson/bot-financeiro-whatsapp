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

    # 💡 NOVO: entender comandos como "cafe 20"
    try:
        partes = msg.lower().split()
        for i, p in enumerate(partes):
            try:
                valor = float(p.replace(",", "."))
                descricao = " ".join(partes[:i] + partes[i+1:])
                break
            except:
                continue
        else:
            return "🤖 Comando não reconhecido. Tente: gasto 20 almoço"

        # Sugerir categoria
        categorias = {
            "café": "alimentação",
            "cafe": "alimentação",
            "mercado": "alimentação",
            "almoço": "alimentação",
            "pizza": "alimentação",
            "uber": "transporte",
            "gasolina": "transporte",
            "ônibus": "transporte",
            "aluguel": "moradia",
            "luz": "moradia",
            "netflix": "lazer",
        }

        categoria = "outros"
        for palavra in categorias:
            if palavra in descricao:
                categoria = categorias[palavra]
                break

        insert_gasto(phone, valor, descricao)  # se quiser salvar a categoria, pode adaptar aqui
        alerta = check_limite(phone)
        return f"✅ Gasto registrado: R${valor:.2f} - {descricao} (Categoria sugerida: {categoria})\n{alerta}"
    except:
        return "🤖 Comando não reconhecido. Use: gasto 25 almoço"

    return "🤖 Comandos disponíveis: gasto, resumo [hoje|semana|mês], limite"