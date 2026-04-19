# importa as bibliotecas python
import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd
import numpy as np
import wave
import os
import subprocess 
import sys 

# importa os arquivos criados pelo desenvolvedor
import resposta_chatgpt 
import resposta_para_audio 
import transcreve_audio 

class AudioRecorder:
    # criar uma interface gráfica para um gravador de voz que automaticamente pergunta ao chatGPT o que dito 
    # e grava a resposta. Para reproduzir o arquivo de áudio gerado clique no botão "reproduzir resposta"
    # o botão "alterar tema" alterna entre o modo claro(padrão) e escuro

    def __init__(self, root, max_duration=20):
        self.root = root
        self.root.title("Gravador de Áudio")

        # Centralizar janela
        window_width = 360
        window_height = 340
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Estado do tema - padrão: claro
        self.dark_mode = False

        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Variáveis
        self.is_recording = False
        self.frames = []
        self.sample_rate = 44100
        self.elapsed_time = 0
        self.timer_job = None
        self.pulse_job = None
        self.pulse_state = False
        self.max_duration = max_duration

        # Layout
        self.frame = ttk.Frame(root, padding=15)
        self.frame.pack(expand=True, fill="both")

        self.label = ttk.Label(self.frame, text="Clique em 'Gravar' para iniciar")
        self.label.pack(pady=5)

        self.rec_label = tk.Label(self.frame, text="", font=("Segoe UI", 10, "bold"))
        self.rec_label.pack()

        self.timer_label = ttk.Label(self.frame, text="00:00")
        self.timer_label.pack(pady=5)

        self.limit_label = ttk.Label(self.frame, text=f"Limite: {self.max_duration}s")
        self.limit_label.pack(pady=2)

        self.record_button = tk.Button(self.frame, text="Gravar", command=self.start_recording)
        self.record_button.pack(pady=5, fill="x")

        self.stop_button = tk.Button(self.frame, text="Parar", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5, fill="x")

        # Botão de reprodução do arquivo resposta.wav
        self.play_button = ttk.Button(self.frame, text="Reproduzir resposta", command=self.play_response)
        self.play_button.pack(pady=10, fill="x")

        # Botão de alternância de tema
        self.theme_button = ttk.Button(self.frame, text="Alternar Tema", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        # Aplicar tema inicial
        self.apply_theme()


    def apply_theme(self):
        if self.dark_mode:
            bg = "#1e1e1e"
            fg = "#ffffff"
            btn_bg = "#28a745"
            stop_bg = "#dc3545"
        else:
            bg = "#f5f5f5"
            fg = "#000000"
            btn_bg = "#4CAF50"
            stop_bg = "#f44336"

        self.root.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))

        self.label.config(background=bg, foreground=fg)
        self.timer_label.config(background=bg, foreground=fg, font=("Segoe UI", 18, "bold"))
        self.limit_label.config(background=bg, foreground=fg)

        self.rec_label.config(bg=bg)

        self.record_button.config(bg=btn_bg, fg="white", relief="flat")
        self.stop_button.config(bg=stop_bg, fg="white", relief="flat")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    # função chamada quando a gravação começa
    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.elapsed_time = 0
        self.update_timer_label()

        self.label.config(text="Gravando...")
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.callback)
        self.stream.start()

        self.update_timer()
        self.animate_rec()

    # animação de "rec" quando está gravando
    def animate_rec(self):
        if self.is_recording:
            color = "red" if self.pulse_state else "#ff8080"
            self.rec_label.config(text="● REC", fg=color)
            self.pulse_state = not self.pulse_state
            self.pulse_job = self.root.after(500, self.animate_rec)
        else:
            self.rec_label.config(text="")

    # atualiza o timer exibido na interface gráfica, quando está gravando
    def update_timer(self):
        if self.is_recording:
            self.elapsed_time += 1
            self.update_timer_label()

            if self.elapsed_time >= self.max_duration:
                self.stop_recording()
                messagebox.showinfo("Limite atingido", "Tempo máximo de gravação atingido!")
                return

            self.timer_job = self.root.after(1000, self.update_timer)

    # atualiza o label do timer
    def update_timer_label(self):
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        self.timer_label.config(text=f"{minutes:02}:{seconds:02}")

    def callback(self, indata, frames, time, status):
        if self.is_recording:
            self.frames.append(indata.copy())

    # função chamada quando o botão "parar" é clicado
    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False

        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        if self.pulse_job:
            self.root.after_cancel(self.pulse_job)

        self.stream.stop()
        self.stream.close()

        self.label.config(text="Gravação finalizada!")
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.rec_label.config(text="")

        self.elapsed_time = 0
        self.update_timer_label()

        # salvao áudio gravado
        self.save_audio()

        # passo 1: transcreve o arquivo de áudio para texto
        try:
            transcreve_audio.transcreve_audio_usuario()
        except FileNotFoundError:
            messagebox.showinfo("Falha ao gravar o arquivo de áudio")
            return
        
        # passo 2: envia a transcrição para a API do chatGPT e gerar um arquivo com a resposta do chat
        try:
            resposta_chatgpt.gerar_resposta_do_chat_gpt()
        except:
            messagebox.showinfo("Falha ao gerar a resposta do chat gtp")
            return
        
        # passo 3: traduz a resposta do chatGPT para áudio
        try:
            resposta_para_audio.traduzir_resposta_para_audio()
        except:
            messagebox.showinfo("Falha ao traduzir a resposta do chat gpt para áudio")
            return

    # salva o áudio da pergunta feita pelo usuário
    def save_audio(self):
        if not self.frames:
            return

        filename = os.path.join(os.getcwd(), "audios", "gravacao.wav")
        audio_data = np.concatenate(self.frames, axis=0)

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16))

        messagebox.showinfo("Áudio gravado com sucesso na pasta audios")

    # abre o arquivo da resposta transcrito do chatGPT, em mp3, no programa padrão que reproduz MP3 no sistema.
    def play_response(self):
        try:
            path = os.path.join(os.getcwd(), "audios", "resposta.mp3")

            if not os.path.exists(path):
                raise FileNotFoundError

            path_resposta = os.path.join(os.getcwd(), "audios", "resposta.mp3")
            try: 
                # Para windos
                os.startfile(path_resposta) 
            except AttributeError: 
                # Para outros sistemas operacionais 
                if sys.platform == "darwin": 
                    subprocess.run(["open", path_resposta], check=False) 
                else: 
                    subprocess.run(["xdg-open", path_resposta], check=False) 
            except OSError as e: 
                messagebox.showerror("Open file failed", f"Não foi posspivel abrir o arquivo de áudio, mas ele está em audios/resposta.mp3':\n{e}")
            


            with wave.open(path, 'rb') as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)
                audio = audio / 32767.0
                sd.play(audio, wf.getframerate())

        except FileNotFoundError:
            messagebox.showerror("Erro, resposta não encontrada")

def start_recorder():
    root = tk.Tk()
    app = AudioRecorder(root)
    root.mainloop()
