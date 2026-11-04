import math

import numpy as np


def calcular_angulo(a, b, c):

    #Atribuicao dos pontos como arrays para permitir calcular
    a,b,c = np.array(a), np.array(b), np.array(c)

    #Subtracao dos pontos: cria os vetores v1 e v2, as setas que saem do vértice b até a e c
    v1 = a - b
    v2 = c - b

    #tamanho1 = (v1[0]**2 + v1[1]**2) ** 0.5
    #Serve para calcular o comprimento da seta (Pitágoras)
    tamanho1 = np.linalg.norm(v1)
    tamanho2 = np.linalg.norm(v2)


    if tamanho1 == 0 or tamanho2 == 0:
        return None

    #Calcular o cosseno do angulo
    cosseno = np.dot(v1, v2) / (tamanho1 * tamanho2)
    cosseno = np.clip(cosseno, -1.0, 1.0)

    #Transformar de cosseno para angulo
    return float(np.degrees(np.arccos(cosseno)))



def escolher_lado(pessoa, pontos_esq, pontos_dir):

    visibilidade_esq = np.mean([pessoa[i].visibility for i in pontos_esq])
    visibilidade_dir = np.mean([pessoa[i].visibility for i in pontos_dir])

    if visibilidade_esq > visibilidade_dir:
        return pontos_esq

    return pontos_dir


def inclinacao_tronco(pontos_px):

    # O tronco e a seta do meio dos ombros (pontos 11 e 12) ate o meio dos quadris (pontos 23 e 24)
    ombro_x = (pontos_px[11][0] + pontos_px[12][0]) / 2
    ombro_y = (pontos_px[11][1] + pontos_px[12][1]) / 2
    quadril_x = (pontos_px[23][0] + pontos_px[24][0]) / 2
    quadril_y = (pontos_px[23][1] + pontos_px[24][1]) / 2

    # 0 graus = tronco na vertical (em pe), 90 graus = tronco na horizontal (deitado)
    return math.degrees(math.atan2(abs(quadril_x - ombro_x), abs(quadril_y - ombro_y)))
