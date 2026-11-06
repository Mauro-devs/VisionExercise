import pathlib
from urllib import request

import mediapipe as mp
from loguru import logger

URL_POSE = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
URL_GESTOS = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"


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


def criar_opcoes():

    caminho_modelo_pose = garantir_modelo("pose_landmarker_lite.task", URL_POSE)
    caminho_modelo_gestos = garantir_modelo("gesture_recognizer.task", URL_GESTOS)

    BaseOptions = mp.tasks.BaseOptions
    RunningMode = mp.tasks.vision.RunningMode

    opcoes_pose = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=caminho_modelo_pose),
        running_mode=RunningMode.VIDEO,
    )

    opcoes_gestos = mp.tasks.vision.GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=caminho_modelo_gestos),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
    )

    return opcoes_pose, opcoes_gestos
