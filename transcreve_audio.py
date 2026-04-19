#transcreve o áudio obtido pelo gravador de áudio para texto usado o Whisper model através da API da OpenAi

from openai import OpenAI
import os
from dotenv import load_dotenv

# Documentação Oficial da API OpenAI: https://platform.openai.com/docs/api-reference/introduction
# Informações sobre o Período Gratuito: https://help.openai.com/en/articles/4936830

# Para gerar uma API Key:
# 1. Crie uma conta na OpenAI
# 2. Acesse a seção "API Keys"
# 3. Clique em "Create API Key"
# Link direto: https://platform.openai.com/account/api-keys
# Link direto para a documentação da API whisper: https://developers.openai.com/api/docs/guides/speech-to-text
# O Whisper é open source e pode ser usado localmente com o comando: 
# !pip install git+https://github.com/openai/whisper.git -q


def transcreve_audio_usuario():
    # transcreve um áudio no formato wav localizado na pasta ./audios e chamado gravacao.wav
    # a transcrição vai para a pasta ./transcricoes (se não existir ela é criada)
    # produz um arquivo em txt na pasta com a transcrição


    load_dotenv()  # Carrega as variáveis do arquivo .env em os.environ

    # o caminho onde será salvo o arquivo 
    path = os.path.join(os.getcwd(), "transcricoes")

    # se a pasta não existir, a cria
    if not os.path.exists(path):
        os.mkdir(path)

    client = OpenAI()

    # caminho onde o arquivo de áudio a ser transcrito está localizado 
    audio_file_path = os.path.join(os.getcwd(), "audios", "gravacao.wav")

    # se a pasta não existir, a cria
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError

    # abre o arquivo de áudio para leitura no modo binário
    audio_file = open(audio_file_path, "rb")

    # manda o áudio para o GPT transcrever
    # retorna um arquivo json e o texto transcrito em si é acessado via transcricao.text
    transcricao = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file
    )

    # guarda o texto transcrito na pastra ./transcricoes como transcricao.txt
    with open(os.path.join(os.getcwd(), "transcricoes", "transcricao.txt"), "w", encoding="utf-8") as file:
        file.write(transcricao.text)
