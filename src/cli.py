import argparse

from src.exercicios import EXERCICIOS


def ler_args():

    parser = argparse.ArgumentParser(description="Identifica o exercicio (agachamento ou flexao) e conta as repeticoes por visao computacional.")

    parser.add_argument("--fonte", default="0",
                        help="Indice da webcam (ex.: 0) ou caminho de um video. Padrao: 0")
    parser.add_argument("--exercicio", choices=list(EXERCICIOS), default=None,
                        help="Pula a escolha por gesto e ja comeca neste exercicio")
    parser.add_argument("--sem-espelho", action="store_true",
                        help="Nao espelha a imagem de camera (por padrao, camera e espelhada)")

    return parser.parse_args()
