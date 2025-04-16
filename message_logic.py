import re
from database import insert_gasto, get_resumo, set_limite, check_limite, excluir_ultimo_gasto

estado_usuario = {}

def process_message(msg, telefone):
    msg = msg.strip().lower().replace(",", ".")

    # Cancelar pendente se novo gasto começar
    if telefone in estado_usuario and estado_usuario[telefone].get("etapa") == "categoria":
        if re.search(r"(\d+(\.\d+)?\s+\w+|\w+\s+\d+(\.\d+)?)", msg):
            estado_usuario.pop(telefone)

    # Cancelar última compra
    if msg in ["cancelar", "desfazer", "remover último"]:
        return excluir_ultimo_gasto(telefone)

    # Definir limite
    if msg.startswith("limite"):
        try:
            valor = float(re.findall(r"\d+(\.\d+)?", msg)[0])
            return set_limite(telefone, valor)
        except:
            return "❌ Informe o valor corretamente. Ex: limite 1000"

    # Relatório manual
    if msg == "relatorio manual":
        return get_resumo(telefone, "mes")

    # Relatório imagem
    if msg.startswith("relatorio_imagem"):
        return "📈 (em breve: gráfico com seus gastos por categoria!)"

    # Resumo
    if msg.startswith("resumo"):
        periodo = "hoje"
        if "semana" in msg:
            periodo = "semana"
        elif "mes" in msg or "mês" in msg:
            periodo = "mes"
        return get_resumo(telefone, periodo)

    # Gastos tipo "cafe 14", "14 uber", "gastei 13 com lanche"
    match = re.match(r"(\d+(\.\d+)?)[\s\-]+(.*)", msg)
    if match:
        valor = float(match.group(1))
        descricao = match.group(3).strip()
    else:
        match = re.match(r"(.*?)[\s\-]+(\d+(\.\d+)?)", msg)
        if match:
            descricao = match.group(1).strip()
            valor = float(match.group(2))
        else:
            return "🤖 Não entendi. Tente algo como `lanche 20`, `resumo hoje`, `limite 1000`, ou `cancelar`."

    estado_usuario[telefone] = {
        "etapa": "categoria",
        "valor": valor,
        "descricao": descricao
    }

    return f"📌 Qual categoria para \"{descricao} {valor:.2f}\"?\n" + (
        "1️⃣ Alimentação\n"
        "2️⃣ Transporte\n"
        "3️⃣ Lazer\n"
        "4️⃣ Saúde\n"
        "5️⃣ Moradia\n"
        "6️⃣ Outros"
    )

def process_categoria(msg, telefone):
    categorias = {
        "1": "alimentação",
        "2": "transporte",
        "3": "lazer",
        "4": "saúde",
        "5": "moradia",
        "6": "outros"
    }

    if telefone not in estado_usuario:
        return "⚠️ Nenhum gasto pendente para categorizar."

    if msg not in categorias:
        return "❌ Categoria inválida. Escolha um número de 1 a 6."

    valor = estado_usuario[telefone]["valor"]
    descricao = estado_usuario[telefone]["descricao"]
    categoria = categorias[msg]
    del estado_usuario[telefone]

    insert_gasto(telefone, valor, descricao, categoria)
    alerta = check_limite(telefone)
    return f"✅ Gasto registrado: R${valor:.2f} - {descricao} (Categoria: {categoria})\n{alerta}"