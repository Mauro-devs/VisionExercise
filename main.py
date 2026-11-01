import pathlib
from urllib import request

import cv2
import mediapipe as mp
from loguru import logger

from src.desenho import desenhar_aviso, desenhar_esqueleto, landmarks_p_pixels


def validar_video_aberto(cap) -> bool:

    if not cap.isOpened():
        logger.info("Falha ao abrir video")
        return False

    logger.info("Video acessado corretamente")
    return True

def validar_pose_landmarker() -> str:

    caminho_modelo = pathlib.Path("models/pose_landmarker_lite.task")

    if not caminho_modelo.exists():

        caminho_modelo.parent.mkdir(parents=True, exist_ok=True)

        request.urlretrieve("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task", caminho_modelo)

        logger.info("Modelo importado com sucesso!")
    else:
        logger.info("Modelo já importado anteriormente, não necessário nova importacão")
        
    return str(caminho_modelo)

if __name__ == "__main__":

    video_path = "videos/FlexaoVideo.mp4"
    cap = cv2.VideoCapture(video_path)

    if not validar_video_aberto(cap=cap):
        raise Exception("Erro ao abrir video")


    caminho_modelo = validar_pose_landmarker()

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    RunningMode = mp.tasks.vision.RunningMode

    opcoes = PoseLandmarkerOptions(
        base_options = BaseOptions(model_asset_path=caminho_modelo),
        running_mode = RunningMode.VIDEO
    )

    with PoseLandmarker.create_from_options(opcoes) as landmarker:

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

            resultado = landmarker.detect_for_video(imagem_np, timestamp)

            #Caso seja necessário acompanhar a identificacão pelos quadros descomente esse trecho:
            #logger.debug(f"Quadro {indice_do_quadro}: {len(resultado.pose_landmarks)} pessoas")

            altura, largura, _ = frame.shape

            if resultado.pose_landmarks:
                pontos_px = landmarks_p_pixels(resultado.pose_landmarks[0], largura, altura)
                desenhar_esqueleto(frame, pontos_px)
                
            else:
                desenhar_aviso(frame, "Pessoa nao detectada!!")

            cv2.imshow("QuadroAtual", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            indice_do_quadro+=1

    cap.release()
    cv2.destroyAllWindows()
    