import cv2
import face_recognition
import threading

class VideoCaptureThread(threading.Thread):
    def __init__(self, camera):
        threading.Thread.__init__(self)
        self.camera = camera
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, self.frame = self.camera.read()
            self.frame = cv2.resize(self.frame, (640, 480))

    def stop(self):
        self.running = False

def iniciar_reconhecimento(camera):
    capture_thread = VideoCaptureThread(camera)
    capture_thread.start()

    imagem_conhecida = face_recognition.load_image_file("images/usuario1.jpg")
    codificacao_conhecida = face_recognition.face_encodings(imagem_conhecida)[0]

    while True:
        frame = capture_thread.frame
        if frame is not None:
            localizacao_rostos = face_recognition.face_locations(frame)
            codificacoes_rostos = face_recognition.face_encodings(frame, localizacao_rostos)

            for (top, right, bottom, left), codificacao in zip(localizacao_rostos, codificacoes_rostos):
                match = face_recognition.compare_faces([codificacao_conhecida], codificacao)

                if match[0]:
                    cv2.putText(frame, "Acesso permitido", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Acesso negado", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            cv2.imshow("Reconhecimento Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture_thread.stop()
    camera.release()
    cv2.destroyAllWindows()
