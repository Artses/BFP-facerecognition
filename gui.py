import tkinter as tk
from tkinter import messagebox
import cv2
import PIL.Image, PIL.ImageTk
from face_recognition_module import iniciar_reconhecimento
from screenshot_module import screenshot
from tkinter.simpledialog import askstring



camera = cv2.VideoCapture(0)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bfp Registro de Presença")
        self.minsize(800,600)
        self.maxsize(800,600)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.create_buttons()

        self.label = tk.Label(self)
        self.label.pack(side=tk.BOTTOM)

        self.update_camera()

    def create_buttons(self):
        botao_chamada = tk.Button(self.button_frame, text="Fazer Chamada", command=self.fazer_chamada, width=20)
        botao_chamada.pack(side=tk.LEFT, padx=5)

        botao_cadastrar = tk.Button(self.button_frame, text="Cadastrar Aluno", command=self.cadastrar_aluno, width=20)
        botao_cadastrar.pack(side=tk.LEFT, padx=5)        

    def cadastrar_aluno(self):
        
        self.tirar_screenshot()

    def fazer_chamada(self):
        iniciar_reconhecimento(camera)
        

    def tirar_screenshot(self):
        nome = askstring("Cadastro","Qual o nome do aluno?")
        
        if nome is None:
            return
        if screenshot(camera, nome):
            messagebox.showinfo("Screenshot", "Screenshot tirada com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível tirar a screenshot.")

    def update_camera(self):
        ret, frame = camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(frame)
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        self.label.after(10, self.update_camera)


if __name__ == "__main__":
    app = Application()
    app.mainloop()

    camera.release()