from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from main import process_message

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    phone = request.values.get("From", "")
    
    response = MessagingResponse()
    reply = process_message(incoming_msg, phone)
    response.message(reply)

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)