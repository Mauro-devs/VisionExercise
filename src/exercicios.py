from dataclasses import dataclass


@dataclass
class Exercicio:
    nome: str
    pontos_esq: tuple
    pontos_dir: tuple
    limiar_baixo: int
    limiar_alto: int


EXERCICIOS = {
    "agachamento": Exercicio("agachamento", (23, 25, 27), (24, 26, 28), 100, 160),
    "flexao": Exercicio("flexao", (11, 13, 15), (12, 14, 16), 100, 150),
}


class ContadorRepeticoes:

    def __init__(self, limiar_baixo, limiar_alto):
        self.limiar_baixo = limiar_baixo
        self.limiar_alto = limiar_alto
        self.estado = "desconhecido"
        self.contador = 0


    def zerar_contagem(self):
        self.contador = 0


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
