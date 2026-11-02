

class Agachamento:

    LIMIAR_BAIXO = 100
    LIMIAR_ALTO = 160

    def __init__(self):
        self.estado = "desconhecido"
        self.contador = 0


    def atualizar(self, angulo):

        if angulo is None:
            return

        if self.estado == "desconhecido" and angulo > self.LIMIAR_ALTO:
            self.estado = "em_cima"

        elif self.estado == "em_cima" and angulo < self.LIMIAR_BAIXO:
            self.estado = "embaixo"

        elif self.estado == "embaixo" and angulo > self.LIMIAR_ALTO:
            self.estado = "em_cima"
            self.contador+=1
