from database import insert_gasto, get_resumo, set_limite, check_limite
from relatorio_csv import gerar_planilha_csv
from uploader import upload_para_imgur
from datetime import datetime

estado_usuario = {}

def process_message(msg, phone):
    global estado_usuario
    msg = msg.lower().strip()

    # Etapa: aguardando categoria
    if phone in estado_usuario:
        etapa = estado_usuario[phone].get("etapa")

        if etapa == "categoria":
            categorias = {
                "1": "alimentação",
                "2": "transporte",
                "3": "lazer",
                "4": "saúde",
                "5": "moradia",
                "6": "outros"
            }
            if msg in categorias:
                if msg == "6":
                    estado_usuario[phone]["etapa"] = "outra_categoria"
                    return "✍️ Digite a categoria personalizada para este gasto:"
                else:
                    gasto = estado_usuario.pop(phone)
                    insert_gasto(phone, gasto["valor"], gasto["descricao"], categorias[msg])
                    alerta = check_limite(phone)
                    return f"✅ Gasto registrado: R${gasto['valor']:.2f} - {gasto['descricao']} (Categoria: {categorias[msg]})\n{alerta}"

        elif etapa == "outra_categoria":
            gasto = estado_usuario.pop(phone)
            insert_gasto(phone, gasto["valor"], gasto["descricao"], msg)
            alerta = check_limite(phone)
            return f"✅ Gasto registrado: R${gasto['valor']:.2f} - {gasto['descricao']} (Categoria: {msg})\n{alerta}"

    # Detectar mensagens do tipo "cafe 15", "15 uber", "gastei 30 com pizza"
    tokens = msg.split()
    valor = None
    descricao = []

    for token in tokens:
        try:
            valor = float(token.replace(",", "."))
            continue
        except:
            descricao.append(token)

    if valor and descricao:
        descricao_final = " ".join(descricao)
        estado_usuario[phone] = {
            "valor": valor,
            "descricao": descricao_final,
            "etapa": "categoria"
        }
        return (
            f"📌 Qual categoria para "{descricao_final} {valor}"?\n"
            "1️⃣ Alimentação\n"
            "2️⃣ Transporte\n"
            "3️⃣ Lazer\n"
            "4️⃣ Saúde\n"
            "5️⃣ Moradia\n"
            "6️⃣ Outros"
        )

    # Comandos padrões
    if msg.startswith("resumo"):
        periodo = msg.replace("resumo", "").strip() or "hoje"
        return get_resumo(phone, periodo)

    elif msg.startswith("limite"):
        try:
            tokens = msg.split()
            valor = float(tokens[1])
            set_limite(phone, valor)
            return f"🔒 Limite mensal definido: R${valor:.2f}"
        except:
            return "❌ Use: limite 1500"

    return "🤖 Comandos disponíveis: gasto 25 lanche | resumo hoje | limite 1500 | relatorio"