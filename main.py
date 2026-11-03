# Execução (a partir da raiz do projeto):
#   uv run python main.py
# Modelos: Pose Landmarker (lite) e Gesture Recognizer, do Google MediaPipe, baixados na primeira execução.

import math
import pathlib
from urllib import request

import cv2
import mediapipe as mp
from loguru import logger

from src.angulos import calcular_angulo, escolher_lado
from src.desenho import (
    desenhar_angulo,
    desenhar_aviso,
    desenhar_contador,
    desenhar_esqueleto,
    desenhar_texto_centralizado,
    landmarks_p_pixels,
)
from src.exercicios import EXERCICIOS, SessaoExercicio
from src.gestos import GESTOS_EXERCICIOS, ConfirmadorGesto, extrair_gesto

URL_POSE = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
URL_GESTOS = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

TEMPO_POSICIONAMENTO_S = 5

# Para pular a escolha por gesto durante os testes, use "agachamento" ou "flexao". Em uso normal, deixe None.
EXERCICIO_FIXO = None


def validar_video_aberto(cap) -> bool:

    if not cap.isOpened():
        logger.info("Falha ao abrir video")
        return False

    logger.info("Video acessado corretamente")
    return True

def garantir_modelo(nome_arquivo, url) -> str:

    caminho_modelo = pathlib.Path("models") / nome_arquivo

    if not caminho_modelo.exists():

        caminho_modelo.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Baixando o modelo {nome_arquivo}...")
        request.urlretrieve(url, caminho_modelo)

        logger.info(f"Modelo {nome_arquivo} importado com sucesso!")
    else:
        logger.info(f"Modelo {nome_arquivo} já importado anteriormente, não necessário nova importacão")

    return str(caminho_modelo)

def processar_pose(landmarker, imagem_np, timestamp, frame, sessao, exibir_resultado):

    altura, largura, _ = frame.shape
    exercicio = sessao.exercicio

    resultado = landmarker.detect_for_video(imagem_np, timestamp)

    #Caso seja necessário acompanhar a identificacão pelos quadros descomente esse trecho:
    #logger.debug(f"Pessoas detectadas: {len(resultado.pose_landmarks)}")

    presente = bool(resultado.pose_landmarks)

    estava_pausado = sessao.monitor.pausado
    voltou = sessao.monitor.atualizar(presente, timestamp)

    if sessao.monitor.pausado and not estava_pausado:
        logger.info("Pessoa fora do quadro: contagem pausada")

    # Ao voltar de uma pausa, o contador volta a esperar a pessoa em pe, para nao contar uma repeticao que nao viu inteira
    if voltou:
        sessao.contador.reiniciar_estado()
        logger.info("Pessoa de volta: contagem retomada")

    if presente:

        pessoa = resultado.pose_landmarks[0]
        pontos_px = landmarks_p_pixels(pessoa, largura, altura)

        inicio, articulacao, fim = escolher_lado(pessoa, exercicio.pontos_esq, exercicio.pontos_dir)

        angulo_encontrado = calcular_angulo(pontos_px[inicio], pontos_px[articulacao], pontos_px[fim])

        desenhar_esqueleto(frame, pontos_px)

        if angulo_encontrado is not None:
            angulo_suavizado = sessao.suavizador.suavizar(angulo_encontrado, timestamp)
            desenhar_angulo(frame, pontos_px[articulacao], angulo_suavizado)
            sessao.contador.atualizar(angulo_suavizado)
    elif exibir_resultado:
        desenhar_aviso(frame, "Contagem pausada" if sessao.monitor.pausado else "Pessoa nao detectada!!")

    if exibir_resultado:
        desenhar_contador(frame, sessao.contador.contador)

if __name__ == "__main__":

    video_path = "videos/VideoIndicador.mp4"
    cap = cv2.VideoCapture(video_path)

    if not validar_video_aberto(cap=cap):
        raise Exception("Erro ao abrir video")


    caminho_modelo_pose = garantir_modelo("pose_landmarker_lite.task", URL_POSE)
    caminho_modelo_gestos = garantir_modelo("gesture_recognizer.task", URL_GESTOS)

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    RunningMode = mp.tasks.vision.RunningMode

    opcoes_pose = PoseLandmarkerOptions(
        base_options = BaseOptions(model_asset_path=caminho_modelo_pose),
        running_mode = RunningMode.VIDEO
    )

    opcoes_gestos = GestureRecognizerOptions(
        base_options = BaseOptions(model_asset_path=caminho_modelo_gestos),
        running_mode = RunningMode.VIDEO,
        num_hands = 1
    )

    with PoseLandmarker.create_from_options(opcoes_pose) as landmarker, \
         GestureRecognizer.create_from_options(opcoes_gestos) as reconhecedor:

        if EXERCICIO_FIXO:
            modo = "exercicio"
            sessao = SessaoExercicio(EXERCICIOS[EXERCICIO_FIXO])
        else:
            modo = "escolha"
            sessao = None

        confirmador = ConfirmadorGesto()
        inicio_posicionamento_ms = None

        fps = cap.get(cv2.CAP_PROP_FPS)
        indice_do_quadro = 0

        while True:

            # O (ret) retorna True se o quadro foi capturado e decodificado com sucesso e Falso caso contrario
            # O (frame) contém os dados visuais da imagem atual lida, no OpenCV é representado como uma matriz
            # multidimensional de pixels no espaco de cores BGR (Azul, Verde, Vermelho)
            ret, frame = cap.read()

            if not ret:
                break

            imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            imagem_np = mp.Image(image_format=mp.ImageFormat.SRGB, data=imagem)

            timestamp = int(indice_do_quadro *1000 / fps)

            if modo == "escolha":

                resultado_gesto = reconhecedor.recognize_for_video(imagem_np, timestamp)
                gesto, confianca = extrair_gesto(resultado_gesto)
                exercicio_escolhido = confirmador.atualizar(gesto, confianca, timestamp)

                desenhar_texto_centralizado(frame, "Escolha o exercicio", 0.10)
                desenhar_texto_centralizado(frame, "1 dedo: agachamento", 0.16)
                desenhar_texto_centralizado(frame, "2 dedos: flexao", 0.22)

                if confirmador.gesto_atual:
                    nome = GESTOS_EXERCICIOS[confirmador.gesto_atual]
                    desenhar_texto_centralizado(frame, f"{nome}: {confirmador.progresso:.0%}", 0.30, (0, 255, 255))

                if exercicio_escolhido:
                    sessao = SessaoExercicio(EXERCICIOS[exercicio_escolhido])
                    inicio_posicionamento_ms = timestamp
                    modo = "posicionamento"
                    logger.info(f"Exercicio escolhido: {sessao.exercicio.nome}")

            elif modo == "posicionamento":

                # A pose ja roda durante a contagem para o contador ver a pessoa em pe antes do inicio
                processar_pose(landmarker, imagem_np, timestamp, frame, sessao, exibir_resultado=False)

                restante = TEMPO_POSICIONAMENTO_S - (timestamp - inicio_posicionamento_ms) / 1000

                if restante <= 0:
                    sessao.contador.zerar_contagem()
                    modo = "exercicio"
                else:
                    desenhar_texto_centralizado(frame, sessao.exercicio.nome, 0.10)
                    desenhar_texto_centralizado(frame, "Posicione-se", 0.20)
                    desenhar_texto_centralizado(frame, str(math.ceil(restante)), 0.35, (0, 255, 255), 2.5)

            else:

                processar_pose(landmarker, imagem_np, timestamp, frame, sessao, exibir_resultado=True)

                desenhar_texto_centralizado(frame, f"Exercicio: {sessao.exercicio.nome}", 0.97)

            if modo != "escolha":
                desenhar_texto_centralizado(frame, "B: trocar exercicio", 0.93)

            cv2.imshow("QuadroAtual", frame)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            if tecla == ord("b") and modo != "escolha":
                modo = "escolha"
                sessao = None
                confirmador = ConfirmadorGesto()
                logger.info("Voltando para a escolha do exercicio")

            indice_do_quadro+=1

    cap.release()
    cv2.destroyAllWindows()
