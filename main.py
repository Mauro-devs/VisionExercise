import pathlib
from urllib import request

import cv2
import mediapipe as mp
from loguru import logger


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
    PoseLandmarksconnections = mp.tasks.vision.PoseLandmarksConnections

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

            logger.info(f"Quadro {indice_do_quadro}: {len(resultado.pose_landmarks)} pessoas")


            altura, largura, _ = frame.shape

            if resultado.pose_landmarks:
                pessoa = resultado.pose_landmarks[0]

                pontos_px = []

                for ponto in pessoa:
                    px = int(ponto.x * largura)
                    py = int(ponto.y * altura)
                    pontos_px.append((px, py))

                for conexao in PoseLandmarksconnections.POSE_LANDMARKS:
                    inicio = pontos_px[conexao.start]
                    fim = pontos_px[conexao.end]
                    cv2.line(frame,inicio, fim, (0, 255, 0), 2)

                for px, py in pontos_px:
                    cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)
            else:
                cv2.putText(frame, "Pessoa nao detectada", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("QuadroAtual", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            indice_do_quadro+=1

    cap.release()
    cv2.destroyAllWindows()
    