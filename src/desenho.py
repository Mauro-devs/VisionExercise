import cv2
import mediapipe as mp

PoseLandmarksConnections = mp.tasks.vision.PoseLandmarksConnections

COR_LINHA = (0, 255, 0)
COR_PONTO = (0, 255, 0)
COR_AVISO = (0, 0, 255)
COR_TEXTO_ANGULO = (255, 255, 255)

ESPESSURA_LINHA = 2
RAIO_PONTO = 5

FONTE = cv2.FONT_HERSHEY_SIMPLEX
LADO_REFERENCIA = 832
ESCALA_REFERENCIA = 0.7
ESCALA_MINIMA = 0.5
MARGEM_PROPORCIONAL = 0.03


def _parametros_texto(frame):
    altura, largura, _ = frame.shape
    lado_maior = max(altura, largura)

    escala = max(ESCALA_MINIMA, lado_maior / LADO_REFERENCIA * ESCALA_REFERENCIA)
    espessura = max(1, round(escala * 2.5))
    margem = int(largura * MARGEM_PROPORCIONAL)

    return escala, espessura, margem


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
    escala, espessura, margem = _parametros_texto(frame)
    (_, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = margem
    y = altura_texto + margem

    cv2.putText(frame, texto, (x, y), FONTE, escala, COR_AVISO, espessura)


def desenhar_angulo(frame, pontopx, angulo):
    altura, largura, _ = frame.shape
    escala, espessura, margem = _parametros_texto(frame)

    texto = f"Angulo: {angulo:.0f}"
    (largura_texto, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    px, py = pontopx
    x = max(margem, min(px, largura - largura_texto - margem))
    y = max(altura_texto + margem, min(py, altura - margem))

    cv2.putText(frame, texto, (x, y), FONTE, escala, COR_TEXTO_ANGULO, espessura)


def desenhar_contador(frame, repeticoes):
    _, largura, _ = frame.shape
    escala, espessura, margem = _parametros_texto(frame)

    texto = f"Repeticoes: {repeticoes}"
    (largura_texto, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = largura - largura_texto - margem
    y = altura_texto + margem

    cv2.putText(frame, texto, (x, y), FONTE, escala, COR_LINHA, espessura)


def desenhar_texto_centralizado(frame, texto, posicao_vertical, cor=COR_TEXTO_ANGULO, escala_relativa=1.0):
    altura, largura, _ = frame.shape
    escala, espessura, _ = _parametros_texto(frame)

    escala *= escala_relativa
    espessura = max(1, round(espessura * escala_relativa))

    (largura_texto, _), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = max(0, (largura - largura_texto) // 2)
    y = int(altura * posicao_vertical)

    cv2.putText(frame, texto, (x, y), FONTE, escala, cor, espessura)
