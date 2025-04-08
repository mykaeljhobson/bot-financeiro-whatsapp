from database import insert_gasto, get_resumo, set_limite, check_limite
from relatorio_csv import gerar_planilha_csv
from uploader import upload_para_imgur
from datetime import datetime
import openai
import os

# Inicialização da API do OpenAI (se necessário para sugestões futuras)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def sugerir_categoria_ia(descricao):
    prompt = f"Classifique a seguinte descrição de gasto em uma categoria: '{descricao}'. Sugira uma categoria curta como alimentação, transporte, lazer, saúde, etc."
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.5,
        )
        return resposta.choices[0].message.content.strip().lower()
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
            insert_gasto(phone, valor, descricao, categoria)
            alerta = check_limite(phone)
            return f"✅ Gasto registrado: R${valor:.2f} - {descricao} (Categoria: {categoria})\n{alerta}"
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

    return "🤖 Comandos disponíveis: gasto, resumo [hoje|semana|mês], limite, relatorio"