import cv2
from loguru import logger



def validar_video_aberto(cap) -> bool:

    if not cap.isOpened():
        logger.info("Falha ao abrir video")
        return False

    logger.info("Video acessado corretamente")
    return True


if __name__ == "__main__":

    video_path = "videos/AgachamentoVideo.mp4"
    cap = cv2.VideoCapture(video_path)

    if not validar_video_aberto(cap=cap):
        raise Exception("Erro ao abrir video")


    while True:

        # O (ret) retorna True se o quadro foi capturado e decodificado com sucesso e Falso caso contrario
        # O (frame) contém os dados visuais da imagem atual lida, no OpenCV é representado como uma matriz
        # multidimensional de pixels no espaco de cores BGR (Azul, Verde, Vermelho)
        ret, frame = cap.read() 

        if not ret:
            break

        cv2.imshow("QuadroAtual", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    