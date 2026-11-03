from collections import deque

TOLERANCIA_AUSENCIA_S = 1.0
JANELA_SUAVIZACAO_MS = 150


class MonitorPresenca:

    def __init__(self, tolerancia_s=TOLERANCIA_AUSENCIA_S):
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

    def __init__(self, janela_ms=JANELA_SUAVIZACAO_MS):
        self.janela_ms = janela_ms
        self.amostras = deque()

    def suavizar(self, angulo, timestamp_ms):

        self.amostras.append((timestamp_ms, angulo))

        while self.amostras[0][0] < timestamp_ms - self.janela_ms:
            self.amostras.popleft()

        return sum(a for _, a in self.amostras) / len(self.amostras)
