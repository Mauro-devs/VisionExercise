# Execução (a partir da raiz do projeto):
#   uv run python main.py                                          (webcam de índice 0)
#   uv run python main.py --fonte 1                                (outra webcam)
#   uv run python main.py --fonte videos/AgachamentoVideo.mp4 --exercicio agachamento
# Uso: faça o gesto para escolher o exercício (1 dedo = agachamento, 2 dedos = flexão), afaste-se e comece.
# Teclas: B troca o exercício, Q sai (a janela do vídeo precisa estar em foco).
# Modelos: Pose Landmarker (lite) e Gesture Recognizer, do Google MediaPipe, baixados na primeira execução.
import argparse
import math
import pathlib
import time
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
from src.robustez import validar_corpo

URL_POSE = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
URL_GESTOS = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

TEMPO_POSICIONAMENTO_S = 3


def ler_args():

    parser = argparse.ArgumentParser(description="Identifica o exercicio (agachamento ou flexao) e conta as repeticoes por visao computacional.")

    parser.add_argument("--fonte", default="0",
                        help="Indice da webcam (ex.: 0) ou caminho de um video. Padrao: 0")
    parser.add_argument("--exercicio", choices=list(EXERCICIOS), default=None,
                        help="Pula a escolha por gesto e ja comeca neste exercicio")
    parser.add_argument("--sem-espelho", action="store_true",
                        help="Nao espelha a imagem de camera (por padrao, camera e espelhada)")

    return parser.parse_args()


def abrir_fonte(fonte):

    # Camera local (so digitos, ex.: "0") e uma fonte "ao vivo": nao tem fim nem fps confiavel
    ao_vivo = fonte.isdigit()

    # A webcam e aberta pelo numero (int) e o video pelo caminho (texto)
    cap = cv2.VideoCapture(int(fonte) if ao_vivo else fonte)

    if ao_vivo:
        # Guarda so o quadro mais recente, para a imagem nao ficar atrasada em relacao a pessoa
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    return cap, ao_vivo

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
    valido = False
    motivo = None

    if presente:
        pessoa = resultado.pose_landmarks[0]
        pontos_px = landmarks_p_pixels(pessoa, largura, altura)

        # O corpo so conta se estiver inteiro no quadro e na postura do exercicio (evita contar so um braco dobrando)
        valido, motivo = validar_corpo(pessoa, pontos_px, exercicio)

    estava_pausado = sessao.monitor.pausado
    voltou = sessao.monitor.atualizar(valido, timestamp)

    if sessao.monitor.pausado and not estava_pausado:
        logger.info("Contagem pausada: corpo fora do quadro ou postura incompativel")

    # Ao voltar de uma pausa, o contador volta a esperar a pessoa em pe, para nao contar uma repeticao que nao viu inteira
    if voltou:
        sessao.contador.reiniciar_estado()
        logger.info("Corpo valido de novo: contagem retomada")

    if presente:

        desenhar_esqueleto(frame, pontos_px)

        if valido:
            inicio, articulacao, fim = escolher_lado(pessoa, exercicio.pontos_esq, exercicio.pontos_dir)

            angulo_encontrado = calcular_angulo(pontos_px[inicio], pontos_px[articulacao], pontos_px[fim])

            if angulo_encontrado is not None:
                angulo_suavizado = sessao.suavizador.suavizar(angulo_encontrado, timestamp)
                desenhar_angulo(frame, pontos_px[articulacao], angulo_suavizado)
                sessao.contador.atualizar(angulo_suavizado)
        else:
            desenhar_aviso(frame, motivo)
    elif exibir_resultado:
        desenhar_aviso(frame, "Contagem pausada" if sessao.monitor.pausado else "Pessoa nao detectada!!")

    if exibir_resultado:
        desenhar_contador(frame, sessao.contador.contador)

if __name__ == "__main__":

    argumentos = ler_args()
    cap, ao_vivo = abrir_fonte(argumentos.fonte)

    if not validar_video_aberto(cap=cap):
        raise SystemExit(f"Nao foi possivel abrir a fonte '{argumentos.fonte}'.\n"
                         "- Webcam: confira se ela esta conectada e nao esta em uso por outro programa; "
                         "se houver mais de uma, tente --fonte 1.\n"
                         "- Video: passe o caminho do arquivo, ex.: --fonte videos/AgachamentoVideo.mp4.")


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

        if argumentos.exercicio:
            modo = "exercicio"
            sessao = SessaoExercicio(EXERCICIOS[argumentos.exercicio])
        else:
            modo = "escolha"
            sessao = None

        confirmador = ConfirmadorGesto()
        inicio_posicionamento_ms = None

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        indice_do_quadro = 0
        inicio_relogio = time.monotonic()
        ultimo_timestamp = -1
        espelhar = ao_vivo and not argumentos.sem_espelho

        while True:

            # O (ret) retorna True se o quadro foi capturado e decodificado com sucesso e Falso caso contrario
            # O (frame) contém os dados visuais da imagem atual lida, no OpenCV é representado como uma matriz
            # multidimensional de pixels no espaco de cores BGR (Azul, Verde, Vermelho)
            ret, frame = cap.read()

            if not ret:
                if ao_vivo:
                    logger.warning("A camera parou de enviar imagem")
                break

            if espelhar:
                frame = cv2.flip(frame, 1)

            imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            imagem_np = mp.Image(image_format=mp.ImageFormat.SRGB, data=imagem)

            if ao_vivo:
                timestamp = int((time.monotonic() - inicio_relogio) * 1000)
            else:
                timestamp = int(indice_do_quadro * 1000 / fps)

            timestamp = max(timestamp, ultimo_timestamp + 1)
            ultimo_timestamp = timestamp

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

                # Se o corpo ficou fora do quadro ou na postura errada por 1 s, a contagem recomeca quando a pessoa se posicionar
                if sessao.monitor.pausado:
                    inicio_posicionamento_ms = timestamp

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
