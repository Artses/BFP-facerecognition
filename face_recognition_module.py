import cv2
import face_recognition
import threading
import os
import requests
import json
import time

class VideoCaptureThread(threading.Thread):
    def __init__(self, camera):
        threading.Thread.__init__(self)
        self.camera = camera
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, self.frame = self.camera.read()
            if ret:
                self.frame = cv2.resize(self.frame, (640, 480))

    def stop(self):
        self.running = False

def carregar_imagens_de_diretorio(diretorio):
    imagens_conhecidas = []
    for filename in os.listdir(diretorio):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            imagem = face_recognition.load_image_file(os.path.join(diretorio, filename))
            codificacao = face_recognition.face_encodings(imagem)
            if codificacao:
                imagens_conhecidas.append((codificacao[0], filename.split('.')[0]))
    return imagens_conhecidas

class PresencaRegistro:
    def __init__(self):
        self.presencas_registradas = {}
        self.tempo_minimo_entre_registros = 600

    def pode_registrar_presenca(self, nome):
        if nome not in self.presencas_registradas:
            self.presencas_registradas[nome] = time.time()
            return True
        
        tempo_ultimo_registro = self.presencas_registradas[nome]
        tempo_atual = time.time()
        
        if tempo_atual - tempo_ultimo_registro >= self.tempo_minimo_entre_registros:
            self.presencas_registradas[nome] = tempo_atual
            return True
        
        return False

def enviar_presenca(id):
    url = "http://localhost:3000/chamada"
    data = {
        "aluno": id,
        "professor": 1,
        "tipoChamada":"Saída"
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  
        print(f"Presença de {id} registrada com sucesso!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao registrar presença de {id}: {e}")
        return False

def iniciar_reconhecimento(camera):
    capture_thread = VideoCaptureThread(camera)
    capture_thread.start()

    imagens_conhecidas = carregar_imagens_de_diretorio("images")
    registro_presenca = PresencaRegistro()

    while True:
        frame = capture_thread.frame
        if frame is not None:
            localizacao_rostos = face_recognition.face_locations(frame)
            codificacoes_rostos = face_recognition.face_encodings(frame, localizacao_rostos)

            for (top, right, bottom, left), codificacao in zip(localizacao_rostos, codificacoes_rostos):
                distancias = face_recognition.face_distance([codificacao_conhecida for codificacao_conhecida, _ in imagens_conhecidas], codificacao)
                menor_distancia_index = distancias.argmin()
                menor_distancia = distancias[menor_distancia_index]

                porcentagem_seme = (1 - menor_distancia) * 100

                if porcentagem_seme > 50:
                    nome = imagens_conhecidas[menor_distancia_index][1]

                    # Verificar se pode registrar presença
                    if registro_presenca.pode_registrar_presenca(nome):
                        # Enviar presença para a API
                        enviar_presenca(nome)

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{nome} - {porcentagem_seme:.2f}% similar", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

                    cv2.rectangle(frame, (left, bottom + 5), (right, bottom + 35), (0, 255, 0), -1)
                    cv2.putText(frame, "Presente", (left + 10, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, f"Acesso negado", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            cv2.imshow("Reconhecimento Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture_thread.stop()
    camera.release()
    cv2.destroyAllWindows()
    return "Fechado"