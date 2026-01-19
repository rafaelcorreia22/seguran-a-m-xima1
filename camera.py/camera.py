import cv2
import os
import winsound
import datetime
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print("Câmera aberta?", ret)
cap.release()


# Pasta para salvar os vídeos
os.makedirs("videos", exist_ok=True)

cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
ret, frame2 = cap.read()

# Configurações do vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 20.0
frame_size = (int(cap.get(3)), int(cap.get(4)))

gravando = False
video_writer = None
frames_sem_movimento = 0
FRAMES_TOLERANCIA = 20  # ~1 segundo sem movimento antes de parar de gravar

while cap.isOpened():
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    movimento_detectado = False

    for contour in contours:
        if cv2.contourArea(contour) > 5000:
            movimento_detectado = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Controle de gravação
    if movimento_detectado:
        print("Movimento detectado!")
        winsound.Beep(1000, 100)

        if not gravando:
            # Inicia nova gravação
            nome_arquivo = datetime.datetime.now().strftime("videos/%Y-%m-%d_%H-%M-%S.avi")
            video_writer = cv2.VideoWriter(nome_arquivo, fourcc, fps, frame_size)
            gravando = True
            print(f"🔴 Gravando: {nome_arquivo}")

        frames_sem_movimento = 0
    else:
        if gravando:
            frames_sem_movimento += 1
            if frames_sem_movimento > FRAMES_TOLERANCIA:
                # Para a gravação
                gravando = False
                video_writer.release()
                video_writer = None
                print("🟢 Gravação finalizada.")

    # Salva frame no vídeo se estiver gravando
    if gravando and video_writer:
        video_writer.write(frame1)

    cv2.imshow("Camera", frame1)

    frame1 = frame2
    ret, frame2 = cap.read()
    if not ret:
        break

    if cv2.waitKey(1) == ord('q'):
        break

# Libera tudo ao sair
if video_writer:
    video_writer.release()

cap.release()
cv2.destroyAllWindows()
