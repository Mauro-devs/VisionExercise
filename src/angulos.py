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
