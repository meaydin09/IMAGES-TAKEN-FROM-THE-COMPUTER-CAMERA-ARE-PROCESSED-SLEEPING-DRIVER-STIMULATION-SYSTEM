import cv2
import numpy as np
import dlib
from imutils import face_utils
import pygame
import time
import ctypes

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

pygame.init()

pygame.mixer.music.load("C:/Users/MEHMET/Desktop/tez/TEZ-CALISMA/alarm_sound.mp3")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:/Users/MEHMET/Desktop/shape_predictor_68_face_landmarks.dat")

tez_gif_path = "C:/Users/MEHMET/Desktop/tez/TEZ-CALISMA/tez.gif"
son_gif_path = "C:/Users/MEHMET/Desktop/tez/TEZ-CALISMA/son.gif"
giris_gif_path="C:/Users/MEHMET/Desktop/tez/TEZ-CALISMA/giris.gif"
alarm_on = False

cap = cv2.VideoCapture(0)

sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

sleep_start_time = None
sleep_threshold = 2     #2 saniye sonra uyarı vermek için 

#iki nokta arası mesafe hesaplama
def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

#göz açıklık oranını hesapla
def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2
    elif ratio > 0.21 and ratio <= 0.25:
        return 1
    else:
        return 0
    
def play_gif(gif_path, display_width, display_height, frame_display_time=50):
     pygame.mixer.init()
    
    
     user32 = ctypes.windll.user32
     screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    #ekran ortasına yerleştir
     x_position = (screen_width - display_width) // 2
     y_position = (screen_height - display_height) // 2

     gif = cv2.VideoCapture(gif_path)
     cv2.namedWindow("Tez GIF", cv2.WINDOW_NORMAL)
     cv2.moveWindow("Tez GIF", x_position, y_position)

     gif = cv2.VideoCapture(gif_path)
     while gif.isOpened():#gif dosyasını döndür
        ret, frame = gif.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (display_width, display_height))
        cv2.imshow("Tez GIF", frame_resized)
        if cv2.waitKey(frame_display_time) & 0xFF == ord('q'):     #q ile çıkış yap
            break
     gif.release()
     cv2.destroyWindow("Tez GIF")
     pygame.mixer.music.stop()
    
def play_gif_until_keypress(gif_path, display_width, display_height, frame_display_time=50):
    gif = cv2.VideoCapture(gif_path)
    while True:
        gif.set(cv2.CAP_PROP_POS_FRAMES, 0)  # GIF'in başına dön
        while gif.isOpened():
            ret, frame = gif.read()
            if not ret:
                break
            frame_resized = cv2.resize(frame, (display_width, display_height))
            cv2.imshow("Tez GIF", frame_resized)
            if cv2.waitKey(frame_display_time) & 0xFF == ord('p'):   #p ile çıkış yap  
                gif.release()
                cv2.destroyWindow("Tez GIF")
                return
    gif.release()
    cv2.destroyWindow("Tez GIF")

# Program başlangıcında giriş GIF'ini oynat
play_gif_until_keypress(giris_gif_path, SCREEN_WIDTH, SCREEN_HEIGHT)

while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #griye dönüştürür

    faces = detector(gray)
    for face in faces:   #yüzün koordinatlarını al
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)  #yüzdeki noktaları belirle
        landmarks = face_utils.shape_to_np(landmarks)

        left_blink = blinked(landmarks[36], landmarks[37],
                              landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43],
                               landmarks[44], landmarks[47], landmarks[46], landmarks[45])  #bu noktalardaki gözlerin kırpma durumunu kontrol et

        if left_blink == 0 or right_blink == 0:  #uykulu durum tespiti  
            if sleep_start_time is None:
                sleep_start_time = time.time()
            elapsed_time = time.time() - sleep_start_time
            if elapsed_time > sleep_threshold:
                status = "UYKULU DURUM!"
                color = (0, 0, 255)
                # Alarm çal
                if not alarm_on:
                    pygame.mixer.music.play()
                    alarm_on = True
                # Direksiyonun titremesi
                print("Direksiyon titriyor!")

                # if not safety_belt_fastened:
                    # safety_belt_fastened = True
                    # print("Emniyet kemeri sıkıldı!")

                print("Gösterge panelinde kırmızı uyarı çıktı!")

                cap.release()

                # play_gif_until_keypress(son_gif_path, SCREEN_WIDTH, SCREEN_HEIGHT)
                play_gif(son_gif_path, SCREEN_WIDTH, SCREEN_HEIGHT)

                cap = cv2.VideoCapture(0)
        else:
            sleep_start_time = None
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "UYANIK"
                color = (0, 255, 0)
                # Alarm durdur
                if alarm_on:
                    pygame.mixer.music.stop()
                    alarm_on = False
                # Direksiyonun titremesi
                print("Direksiyon titremesi durdu.")
                # Emniyet kemeri gevşetiliyor
                # if safety_belt_fastened:
                #     safety_belt_fastened = False
                #     print("Emniyet kemeri gevşetildi.")
                # Gösterge panelindeki kırmızı uyarı kapatılıyor
                print("Gösterge panelindeki kırmızı uyarı kapatıldı.")

        cv2.putText(frame, status, (100, 100),   #durumu ekrana yazar
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

        cv2.imshow("Result of detector", face_frame)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:  #esc ile çıkış yap  ASCII karakter seti
        break

cap.release()
cv2.destroyAllWindows()
