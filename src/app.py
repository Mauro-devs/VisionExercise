import math
import time

import cv2
import mediapipe as mp
from loguru import logger

from src.cli import ler_args
from src.desenho import desenhar_texto_centralizado
from src.exercicios import EXERCICIOS, SessaoExercicio
from src.fonte import abrir_fonte
from src.gestos import GESTOS_EXERCICIOS, ConfirmadorGesto, extrair_gesto
from src.modelos.carregar import criar_opcoes
from src.pose import processar_pose


class App:
    """Guarda o estado da execucao e trata cada quadro conforme o modo atual."""

    def __init__(self, landmarker, reconhecedor, exercicio_inicial=None, tempo_posicionamento_s=3):

        self.landmarker = landmarker
        self.reconhecedor = reconhecedor
        self.confirmador = ConfirmadorGesto()
        self.inicio_posicionamento_ms = None
        self.mostrar_marcacoes = True
        self.tempo_posicionamento_s = tempo_posicionamento_s

        if exercicio_inicial:
            self.modo = "exercicio"
            self.sessao = SessaoExercicio(EXERCICIOS[exercicio_inicial])
        else:
            self.modo = "escolha"
            self.sessao = None

    def processar_quadro(self, frame, imagem_np, timestamp):

        if self.modo == "escolha":
            self._escolha(frame, imagem_np, timestamp)
        elif self.modo == "posicionamento":
            self._posicionamento(frame, imagem_np, timestamp)
        else:
            self._exercicio(frame, imagem_np, timestamp)

        if self.modo != "escolha":
            desenhar_texto_centralizado(frame, "B: trocar exercicio", 0.93)
            desenhar_texto_centralizado(frame, "A: esqueleto", 0.89)

    def tratar_tecla(self, tecla) -> bool:
        """Devolve False quando o usuario pediu para sair."""

        if tecla == ord("q"):
            return False

        if tecla == ord("b") and self.modo != "escolha":
            self.modo = "escolha"
            self.sessao = None
            self.confirmador = ConfirmadorGesto()
            logger.info("Voltando para a escolha do exercicio")

        if tecla == ord("a"):
            self.mostrar_marcacoes = not self.mostrar_marcacoes

        return True

    def _escolha(self, frame, imagem_np, timestamp):

        resultado_gesto = self.reconhecedor.recognize_for_video(imagem_np, timestamp)
        gesto, confianca = extrair_gesto(resultado_gesto)
        exercicio_escolhido = self.confirmador.atualizar(gesto, confianca, timestamp)

        desenhar_texto_centralizado(frame, "Escolha o exercicio", 0.10)
        desenhar_texto_centralizado(frame, "1 dedo: agachamento", 0.16)
        desenhar_texto_centralizado(frame, "2 dedos: flexao", 0.22)

        if self.confirmador.gesto_atual:
            nome = GESTOS_EXERCICIOS[self.confirmador.gesto_atual]
            desenhar_texto_centralizado(frame, f"{nome}: {self.confirmador.progresso:.0%}", 0.30, (0, 255, 255))

        if exercicio_escolhido:
            self.sessao = SessaoExercicio(EXERCICIOS[exercicio_escolhido])
            self.inicio_posicionamento_ms = timestamp
            self.modo = "posicionamento"
            logger.info(f"Exercicio escolhido: {self.sessao.exercicio.nome}")

    def _posicionamento(self, frame, imagem_np, timestamp):

        # A pose ja roda durante a contagem para o contador ver a pessoa em pe antes do inicio
        processar_pose(self.landmarker, self.mostrar_marcacoes, imagem_np, timestamp, frame, self.sessao, exibir_resultado=False)

        # Se o corpo ficou fora do quadro ou na postura errada por 1 s, a contagem recomeca quando a pessoa se posicionar
        if self.sessao.monitor.pausado:
            self.inicio_posicionamento_ms = timestamp

        restante = self.tempo_posicionamento_s - (timestamp - self.inicio_posicionamento_ms) / 1000

        if restante <= 0:
            self.sessao.contador.zerar_contagem()
            self.modo = "exercicio"
        else:
            desenhar_texto_centralizado(frame, self.sessao.exercicio.nome, 0.10)
            desenhar_texto_centralizado(frame, "Posicione-se", 0.20)
            desenhar_texto_centralizado(frame, str(math.ceil(restante)), 0.35, (0, 255, 255), 2.5)

    def _exercicio(self, frame, imagem_np, timestamp):

        processar_pose(self.landmarker, self.mostrar_marcacoes, imagem_np, timestamp, frame, self.sessao, exibir_resultado=True)

        desenhar_texto_centralizado(frame, f"Exercicio: {self.sessao.exercicio.nome}", 0.97)


def calcular_timestamp(ao_vivo, inicio_relogio, indice_do_quadro, fps, ultimo_timestamp):
    """Timestamp em ms, sempre crescente (o MediaPipe no modo VIDEO exige isso)."""

    if ao_vivo:
        timestamp = int((time.monotonic() - inicio_relogio) * 1000)
    else:
        timestamp = int(indice_do_quadro * 1000 / fps)

    return max(timestamp, ultimo_timestamp + 1)


def executar():

    argumentos = ler_args()
    cap, ao_vivo = abrir_fonte(argumentos.fonte)
    opcoes_pose, opcoes_gestos = criar_opcoes()

    espelhar = ao_vivo and not argumentos.sem_espelho
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    inicio_relogio = time.monotonic()
    ultimo_timestamp = -1
    indice_do_quadro = 0

    try:
        with mp.tasks.vision.PoseLandmarker.create_from_options(opcoes_pose) as landmarker, \
             mp.tasks.vision.GestureRecognizer.create_from_options(opcoes_gestos) as reconhecedor:

            app = App(landmarker, reconhecedor, argumentos.exercicio)

            while True:

                # ret e True se o quadro foi lido; frame e a imagem (matriz de pixels BGR)
                ret, frame = cap.read()

                if not ret:
                    if ao_vivo:
                        logger.warning("A camera parou de enviar imagem")
                    break

                if espelhar:
                    frame = cv2.flip(frame, 1)

                imagem_np = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                timestamp = calcular_timestamp(ao_vivo, inicio_relogio, indice_do_quadro, fps, ultimo_timestamp)
                ultimo_timestamp = timestamp

                app.processar_quadro(frame, imagem_np, timestamp)

                cv2.imshow("QuadroAtual", frame)

                if not app.tratar_tecla(cv2.waitKey(1) & 0xFF):
                    break

                indice_do_quadro += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()
