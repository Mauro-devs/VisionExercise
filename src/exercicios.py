from dataclasses import dataclass

from src.robustez import MonitorPresenca, SuavizadorAngulo


@dataclass
class Exercicio:
    nome: str
    pontos_esq: tuple
    pontos_dir: tuple
    limiar_baixo: int
    limiar_alto: int
    grupos_corpo: tuple
    inclinacao_min: int
    inclinacao_max: int


EXERCICIOS = {
    "agachamento": Exercicio("agachamento", (23, 25, 27), (24, 26, 28), 100, 160,
                             grupos_corpo=((11, 12), (23, 24), (25, 26), (27, 28)),
                             inclinacao_min=0, inclinacao_max=60),
    "flexao": Exercicio("flexao", (11, 13, 15), (12, 14, 16), 110, 150,
                        grupos_corpo=((0,), (11, 12), (23, 24)),
                        inclinacao_min=50, inclinacao_max=90),
}


class ContadorRepeticoes:

    def __init__(self, limiar_baixo, limiar_alto):
        self.limiar_baixo = limiar_baixo
        self.limiar_alto = limiar_alto
        self.estado = "desconhecido"
        self.contador = 0


    def zerar_contagem(self):
        self.contador = 0


    def reiniciar_estado(self):
        self.estado = "desconhecido"


    def atualizar(self, angulo):

        if angulo is None:
            return

        if self.estado == "desconhecido" and angulo > self.limiar_alto:
            self.estado = "em_cima"

        elif self.estado == "em_cima" and angulo < self.limiar_baixo:
            self.estado = "embaixo"

        elif self.estado == "embaixo" and angulo > self.limiar_alto:
            self.estado = "em_cima"
            self.contador+=1


class SessaoExercicio:

    def __init__(self, exercicio):
        self.exercicio = exercicio
        self.contador = ContadorRepeticoes(exercicio.limiar_baixo, exercicio.limiar_alto)
        self.monitor = MonitorPresenca()
        self.suavizador = SuavizadorAngulo()
