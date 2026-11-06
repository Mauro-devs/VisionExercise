import cv2
from loguru import logger


def abrir_fonte(fonte):

    # Camera local (so digitos, ex.: "0") e uma fonte "ao vivo": nao tem fim nem fps confiavel
    ao_vivo = fonte.isdigit()

    # A webcam e aberta pelo numero (int) e o video pelo caminho (texto)
    cap = cv2.VideoCapture(int(fonte) if ao_vivo else fonte)

    if not cap.isOpened():
        logger.info("Falha ao abrir video")
        raise SystemExit(f"Nao foi possivel abrir a fonte '{fonte}'.\n"
                         "- Webcam: confira se ela esta conectada e nao esta em uso por outro programa; "
                         "se houver mais de uma, tente --fonte 1.\n"
                         "- Video: passe o caminho do arquivo, ex.: --fonte videos/AgachamentoVideo.mp4.")

    logger.info("Video acessado corretamente")

    if ao_vivo:
        # Guarda so o quadro mais recente, para a imagem nao ficar atrasada em relacao a pessoa
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    return cap, ao_vivo
