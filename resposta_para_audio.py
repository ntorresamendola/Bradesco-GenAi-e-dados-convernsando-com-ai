from gtts import  gTTS
import os

# transcreve a resposta dada pelo chatGPT, localizada no arquivo ./resposta/resposta.txt, para áudio
# o áudio é armazenado em ./audio/resposta.mp3

def traduzir_resposta_para_audio():
    # transcreve a resposta dada pelo chatGPT, localizada no arquivo ./resposta/resposta.txt, para áudio
    # o áudio é armazenado em ./audio/resposta.mp3

    language="pt"
    chatgpt_response = ""

    #caminho para a pasta do arquivo de resposta e a dos áudios
    path = os.path.join(os.getcwd(), "respostas")
    path_audio = os.path.join(os.getcwd(), "audios")

    # se as pastas não existirem, as cria
    if not os.path.exists(path):
        os.mkdir(path)

    if not os.path.exists(path_audio):
        os.mkdir(path_audio)

    # lê o arquivo gerado pelo chatGPT
    with open(os.path.join(os.getcwd(), "respostas", "resposta.txt"), 'r', encoding='utf-8') as arquivo:
        chatgpt_response = arquivo.read()
     

    # Cria um objeto gTTS com a resposta gerada pelo ChatGPT e a língua que será sintetizada em voz (variável "language").
    gtts_object = gTTS(text=chatgpt_response, lang=language, slow=False)

    response_audio = os.path.join(os.getcwd(), "audios", "resposta.mp3")
    
    # Salva o áudio da resposta na pasta ./audios/resposta.mp3
    gtts_object.save(response_audio)
