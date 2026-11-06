from loguru import logger

from src.angulos import calcular_angulo, escolher_lado
from src.desenho import (
    desenhar_angulo,
    desenhar_aviso,
    desenhar_contador,
    desenhar_esqueleto,
    landmarks_p_pixels,
)
from src.robustez import validar_corpo


def processar_pose(landmarker, mostrar_marcacoes, imagem_np, timestamp, frame, sessao, exibir_resultado):

    altura, largura, _ = frame.shape
    exercicio = sessao.exercicio

    resultado = landmarker.detect_for_video(imagem_np, timestamp)

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
        if mostrar_marcacoes:
            desenhar_esqueleto(frame, pontos_px)

        if valido:
            inicio, articulacao, fim = escolher_lado(pessoa, exercicio.pontos_esq, exercicio.pontos_dir)

            angulo_encontrado = calcular_angulo(pontos_px[inicio], pontos_px[articulacao], pontos_px[fim])

            if angulo_encontrado is not None:
                angulo_suavizado = sessao.suavizador.suavizar(angulo_encontrado, timestamp)
                if mostrar_marcacoes:
                    desenhar_angulo(frame, pontos_px[articulacao], angulo_suavizado)
                sessao.contador.atualizar(angulo_suavizado)
        else:
            desenhar_aviso(frame, motivo)
    elif exibir_resultado:
        desenhar_aviso(frame, "Contagem pausada" if sessao.monitor.pausado else "Pessoa nao detectada!!")

    if exibir_resultado:
        desenhar_contador(frame, sessao.contador.contador)
