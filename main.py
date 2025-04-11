from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from uploader import upload_para_imgur
from relatorio_csv import gerar_planilha_csv
from message_logic import process_message, estado_usuario
from database import init_db
import os

app = Flask(__name__)

# Twilio config
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    phone = request.values.get("From", "")
    response = MessagingResponse()

    # ✅ Tratamento interativo do comando 'relatorio'
    if incoming_msg.startswith("relatorio"):
        periodo = incoming_msg.replace("relatorio", "").strip() or "mes"
        estado_usuario[phone] = {"etapa": "tipo_relatorio", "periodo": periodo}
        response.message(
            """📊 Que tipo de relatório você deseja?
1️⃣ Gráfico (imagem)
2️⃣ Planilha (CSV)"""
        )
        return str(response)

    # ✅ Continuação da interação após escolher tipo de relatório
    if phone in estado_usuario and estado_usuario[phone].get("etapa") == "tipo_relatorio":
        if incoming_msg in ["1", "2"]:
            periodo = estado_usuario[phone]["periodo"]
            del estado_usuario[phone]

            if incoming_msg == "1":
                resposta = process_message(f"relatorio_imagem {periodo}", phone)
                response.message(resposta)
            else:
                csv_path = gerar_planilha_csv(periodo, telefone=phone)
                if csv_path:
                    link = upload_para_imgur(csv_path)
                    if link:
                        send_media(phone, link, "📎 Seu relatório em planilha está pronto!")
                    else:
                        response.message("❌ Erro ao enviar a planilha.")
                else:
                    response.message("📭 Nenhum dado encontrado para gerar o relatório.")
        else:
            response.message("❌ Opção inválida. Responda com 1 ou 2.")
        return str(response)

    # ✅ Comandos gerais
    resposta = process_message(incoming_msg, phone)
    response.message(resposta)
    return str(response)

def send_media(to, media_url, caption):
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=caption,
        to=to,
        media_url=[media_url]
    )

# Inicializa o banco de dados ao subir o app
init_db()

if __name__ == "__main__":
    app.run()