import cv2
import mediapipe as mp

PoseLandmarksConnections = mp.tasks.vision.PoseLandmarksConnections

COR_LINHA = (0, 255, 0)
COR_PONTO = (0, 255, 0)
COR_AVISO = (0, 0, 255)
COR_TEXTO_ANGULO = (255, 255, 255)

ESPESSURA_LINHA = 2
RAIO_PONTO = 5


def landmarks_p_pixels(pessoa, largura, altura):
    pontos_px = []
    for ponto in pessoa:
        px = int(ponto.x * largura)
        py = int(ponto.y * altura)

        pontos_px.append((px, py))

    return pontos_px

def desenhar_esqueleto(frame, pontos_px):
    for conexao in PoseLandmarksConnections.POSE_LANDMARKS:
        inicio = pontos_px[conexao.start]
        fim = pontos_px[conexao.end]
        cv2.line(frame, inicio, fim, COR_LINHA, ESPESSURA_LINHA)

    for px, py in pontos_px:
        cv2.circle(frame, (px, py), RAIO_PONTO, COR_PONTO, -1)


def desenhar_aviso(frame, texto):
    cv2.putText(frame, texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_AVISO, 2)


def desenhar_angulo(frame, pontopx, angulo):
    cv2.putText(frame, f"Angulo: {angulo:.0f}", pontopx, cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_TEXTO_ANGULO, 2)
    