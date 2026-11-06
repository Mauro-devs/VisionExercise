import cv2
import mediapipe as mp

# Cores em BGR (o padrao do OpenCV)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

FONTE = cv2.FONT_HERSHEY_SIMPLEX


def _parametros_texto(frame):
    altura, largura, _ = frame.shape
    lado_maior = max(altura, largura)

    # O texto cresce proporcionalmente a imagem: escala 0.7 para um lado maior de 832 px, com minimo de 0.5
    escala = max(0.5, lado_maior / 832 * 0.7)
    espessura = max(1, round(escala * 2.5))
    margem = int(largura * 0.03)

    return escala, espessura, margem


def _escrever_texto(frame, texto, posicao, escala, cor, espessura):
    x, y = posicao
    deslocamento = max(2, round(escala * 2.5))

    for dx in (-deslocamento, 0, deslocamento):
        for dy in (-deslocamento, 0, deslocamento):
            if dx or dy:
                cv2.putText(frame, texto, (x + dx, y + dy), FONTE, escala, PRETO, espessura, cv2.LINE_AA)

    cv2.putText(frame, texto, posicao, FONTE, escala, cor, espessura, cv2.LINE_AA)


def landmarks_p_pixels(pessoa, largura, altura):
    pontos_px = []
    for ponto in pessoa:
        px = int(ponto.x * largura)
        py = int(ponto.y * altura)

        pontos_px.append((px, py))

    return pontos_px

def desenhar_esqueleto(frame, pontos_px):
    for conexao in mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS:
        inicio = pontos_px[conexao.start]
        fim = pontos_px[conexao.end]
        cv2.line(frame, inicio, fim, VERDE, 2)

    for px, py in pontos_px:
        cv2.circle(frame, (px, py), 5, VERDE, -1)


def desenhar_aviso(frame, texto):
    escala, espessura, margem = _parametros_texto(frame)
    (_, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = margem
    y = altura_texto + margem

    _escrever_texto(frame, texto, (x, y), escala, VERMELHO, espessura)


def desenhar_angulo(frame, pontopx, angulo):
    altura, largura, _ = frame.shape
    escala, espessura, margem = _parametros_texto(frame)

    texto = f"Angulo: {angulo:.0f}"
    (largura_texto, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    px, py = pontopx
    x = max(margem, min(px, largura - largura_texto - margem))
    y = max(altura_texto + margem, min(py, altura - margem))

    _escrever_texto(frame, texto, (x, y), escala, BRANCO, espessura)


def desenhar_contador(frame, repeticoes):
    _, largura, _ = frame.shape
    escala, espessura, margem = _parametros_texto(frame)

    texto = f"Repeticoes: {repeticoes}"
    (largura_texto, altura_texto), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = largura - largura_texto - margem
    y = altura_texto + margem

    _escrever_texto(frame, texto, (x, y), escala, VERDE, espessura)


def desenhar_texto_centralizado(frame, texto, posicao_vertical, cor=BRANCO, escala_relativa=1.0):
    altura, largura, _ = frame.shape
    escala, espessura, _ = _parametros_texto(frame)

    escala *= escala_relativa
    espessura = max(1, round(espessura * escala_relativa))

    (largura_texto, _), _ = cv2.getTextSize(texto, FONTE, escala, espessura)

    x = max(0, (largura - largura_texto) // 2)
    y = int(altura * posicao_vertical)

    _escrever_texto(frame, texto, (x, y), escala, cor, espessura)
