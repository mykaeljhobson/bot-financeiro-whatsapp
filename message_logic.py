import re
from database import insert_gasto, get_resumo, set_limite, check_limite, excluir_ultimo_gasto

estado_usuario = {}

def process_message(msg, telefone):
    msg = msg.strip().lower()

    # Cancelar última compra
    if msg in ["cancelar", "desfazer", "remover último"]:
        return excluir_ultimo_gasto(telefone)

    # Definir limite direto
    if msg.startswith("limite"):
        try:
            valor = float(re.findall(r"\d+(\.\d+)?", msg)[0])
            return set_limite(telefone, valor)
        except:
            return "❌ Informe o valor corretamente. Ex: limite 1000"

    # Relatório manual (resumo mês)
    if msg == "relatorio manual":
        return get_resumo(telefone, "mes")

    # Relatório imagem (opção 1)
    if msg.startswith("relatorio_imagem"):
        return "📈 Relatório em gráfico ainda não está disponível. Em breve!"

    # Resumo
    if msg.startswith("resumo"):
        periodo = "hoje"
        if "semana" in msg:
            periodo = "semana"
        elif "mes" in msg or "mês" in msg:
            periodo = "mes"
        return get_resumo(telefone, periodo)

    # Gastos simplificados tipo: "cafe 20" ou "20 uber"
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
            return "🤖 Comandos disponíveis: gasto 25 lanche | resumo hoje | limite 1500 | relatorio manual"

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