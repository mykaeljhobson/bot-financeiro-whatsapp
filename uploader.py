import requests
import os

def upload_para_imgur(caminho_imagem):
    client_id = os.environ.get("IMGUR_CLIENT_ID")
    if not client_id:
        raise Exception("IMGUR_CLIENT_ID não definido")

    headers = {"Authorization": f"Client-ID {client_id}"}
    with open(caminho_imagem, "rb") as imagem:
        data = {"image": imagem.read(), "type": "file"}
        resposta = requests.post("https://api.imgur.com/3/upload", headers=headers, files={"image": imagem})
        
    if resposta.status_code == 200:
        return resposta.json()["data"]["link"]
    else:
        print("Erro ao enviar imagem para o Imgur:", resposta.text)
        return None