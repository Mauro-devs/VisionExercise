# Execução (a partir da raiz do projeto):
#   uv run python main.py                                          (webcam de índice 0)
#   uv run python main.py --fonte 1                                (outra webcam)
#   uv run python main.py --fonte videos/AgachamentoVideo.mp4 --exercicio agachamento
# Uso: faça o gesto para escolher o exercício (1 dedo = agachamento, 2 dedos = flexão), afaste-se e comece.
# Teclas: B troca o exercício, A mostra/esconde esqueleto e ângulo, Q sai (a janela do vídeo precisa estar em foco).
# Modelos: Pose Landmarker (lite) e Gesture Recognizer, do Google MediaPipe, baixados na primeira execução.
from src.app import executar

if __name__ == "__main__":
    executar()
