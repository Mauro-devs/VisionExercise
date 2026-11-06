# Escolha do exercicio por gesto de mao, usando o Gesture Recognizer do MediaPipe.

GESTOS_EXERCICIOS = {
    "Pointing_Up": "agachamento",
    "Victory": "flexao",
}


def extrair_gesto(resultado):
    if not resultado.gestures:
        return None, 0.0

    melhor = resultado.gestures[0][0]
    return melhor.category_name, melhor.score


class ConfirmadorGesto:

    def __init__(self, tempo_confirmacao_s=1.0, confianca_minima=0.6):
        self.tempo_confirmacao_ms = tempo_confirmacao_s * 1000
        self.confianca_minima = confianca_minima
        self.gesto_atual = None
        self.inicio_ms = None
        self.progresso = 0.0

    def atualizar(self, gesto, score, timestamp_ms):

        valido = gesto in GESTOS_EXERCICIOS and score >= self.confianca_minima

        if not valido:
            self._reiniciar()
            return None

        if gesto != self.gesto_atual:
            self.gesto_atual = gesto
            self.inicio_ms = timestamp_ms

        decorrido = timestamp_ms - self.inicio_ms
        self.progresso = min(1.0, decorrido / self.tempo_confirmacao_ms)

        if decorrido >= self.tempo_confirmacao_ms:
            return GESTOS_EXERCICIOS[gesto]

        return None

    def _reiniciar(self):
        self.gesto_atual = None
        self.inicio_ms = None
        self.progresso = 0.0
