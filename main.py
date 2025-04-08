from database import insert_gasto, get_resumo, set_limite, check_limite
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def sugerir_categoria_ia(descricao):
    prompt = f"Classifique a seguinte descrição de gasto em uma categoria: '{descricao}'. Sugira uma categoria curta e clara como alimentação, transporte, lazer, moradia, saúde, educação, etc."

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.5,
        )
        categoria = resposta["choices"][0]["message"]["content"].strip().lower()
        return categoria
    except Exception as e:
        print(f"Erro ao usar IA: {e}")
        return "outros"

def process_message(msg, phone):
    tokens = msg.lower().split()

    if tokens[0] == "gasto":
        try:
            valor = float(tokens[1])
            descricao = " ".join(tokens[2:])
            categoria = sugerir_categoria_ia(descricao)
            insert_gasto(phone, valor, descricao)  # pode adaptar para salvar categoria também
            alerta = check_limite(phone)
            return f"✅ Gasto registrado: R${valor:.2f} - {descricao} (Categoria sugerida: {categoria})\n{alerta}"
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

    # 💡 Comando resumido, tipo: "pizza 40"
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

        categoria = sugerir_categoria_ia(descricao)
        insert_gasto(phone, valor, descricao)
        alerta = check_limite(phone)
        return f"✅ Gasto registrado: R${valor:.2f} - {descricao} (Categoria sugerida: {categoria})\n{alerta}"
    except:
        return "🤖 Comando não reconhecido. Use: gasto 25 almoço"

    return "🤖 Comandos disponíveis: gasto, resumo [hoje|semana|mês], limite"