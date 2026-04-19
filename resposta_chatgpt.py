# Documentação Oficial da API OpenAI: https://platform.openai.com/docs/api-reference/introduction
# Informações sobre o Período Gratuito: https://help.openai.com/en/articles/4936830

# Para gerar uma API Key:
# 1. Crie uma conta na OpenAI
# 2. Acesse a seção "API Keys"
# 3. Clique em "Create API Key"
# Link direto: https://platform.openai.com/account/api-keys

# Coloque sua chave API em um arquivo .env, conforme o arquivo .env.example

from openai import OpenAI
import os
from dotenv import load_dotenv

def gerar_resposta_do_chat_gpt():
    # Lê o arquivo com a pergunta transcrita, localizado em ./transcricoes/transcricao.txt
    # Envia para o chatGPT e grava a resposta em ./respostas/resposta.txt

    load_dotenv()  # Carrega as variáveis do arquivo .env em os.environ

    client = OpenAI()

    # local onde o arquivo com a resposta transcrita deverá estar
    path = os.path.join(os.getcwd(), "transcricoes", "transcricao.txt")

    # se ele não existir, gera erro
    if not os.path.exists(path):
        raise FileNotFoundError 

    # pasta da resposta, se não existir, a cria
    path_resposta = os.path.join(os.getcwd(), "respostas")
    if not os.path.exists(path_resposta):
        os.mkdir(path_resposta)

    # lê o arquivo com a pergunta transcrita
    with open(path, "r", encoding="utf-8") as file:
        pergunta_transcrita = file.read()

    # envia para a API do chatGPT, na variável response. O texto da resposta é acessado com response.output_text
    response = client.responses.create(
        model="gpt-5.4",
        input=pergunta_transcrita + " Por favor, forneça a resposta em texto puro (plain text), sem Markdown, negrito, itálico ou listas numeradas/bullet points."
    )

    # escreve a resposta para o arquivo ./respostas/resposta.txt
    with open(os.path.join(os.getcwd(), "respostas", "resposta.txt"), "w", encoding="utf-8") as file:
        file.write(response.output_text)
