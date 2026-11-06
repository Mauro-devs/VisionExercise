from collections import deque

from src.angulos import inclinacao_tronco


class MonitorPresenca:

    def __init__(self, tolerancia_s=1.0):
        self.tolerancia_ms = tolerancia_s * 1000
        self.ausente_desde_ms = None
        self.pausado = False

    def atualizar(self, presente, timestamp_ms):

        if presente:
            voltou = self.pausado
            self.ausente_desde_ms = None
            self.pausado = False
            return voltou

        if self.ausente_desde_ms is None:
            self.ausente_desde_ms = timestamp_ms

        if timestamp_ms - self.ausente_desde_ms >= self.tolerancia_ms:
            self.pausado = True

        return False


class SuavizadorAngulo:

    def __init__(self, janela_ms=150):
        self.janela_ms = janela_ms
        self.amostras = deque()

    def suavizar(self, angulo, timestamp_ms):

        self.amostras.append((timestamp_ms, angulo))

        while self.amostras[0][0] < timestamp_ms - self.janela_ms:
            self.amostras.popleft()

        return sum(a for _, a in self.amostras) / len(self.amostras)


def _ponto_aproveitavel(ponto):
    # A visibilidade sozinha nao basta: o modelo da confianca alta ate para pontos que ele inventa fora da imagem
    margem_quadro = 0.02
    dentro_do_quadro = margem_quadro <= ponto.x <= 1 - margem_quadro and margem_quadro <= ponto.y <= 1 - margem_quadro

    return dentro_do_quadro and ponto.visibility >= 0.5


def validar_corpo(pessoa, pontos_px, exercicio):

    # De cada grupo (ex.: ombro esquerdo e direito) basta um ponto aproveitavel, pois o outro lado pode estar escondido
    for grupo in exercicio.grupos_corpo:
        if not any(_ponto_aproveitavel(pessoa[i]) for i in grupo):
            return False, "Mostre o corpo inteiro"

    inclinacao = inclinacao_tronco(pontos_px)

    if not exercicio.inclinacao_min <= inclinacao <= exercicio.inclinacao_max:
        return False, "Postura incompativel"

    return True, None
