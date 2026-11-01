# VisionExercise

Projeto de visão computacional que **identifica automaticamente qual exercício físico está sendo feito** (flexão ou agachamento) e **conta as repetições** em tempo real.

## Objetivo

Dado um vídeo ou a webcam, o sistema deve:

1. Detectar a pessoa e extrair os pontos do corpo (pose).
2. Identificar qual exercício está sendo executado.
3. Contar as repetições completas desse exercício.
4. Exibir o resultado na tela (exercício detectado + contagem).

Exemplo: a pessoa começa a fazer flexões, o sistema mostra "Flexão" e incrementa o contador a cada repetição. Se ela passa a fazer agachamentos, o sistema troca para "Agachamento" e conta as novas repetições.

## Como vai funcionar

- **Pose:** um modelo pré-treinado (MediaPipe Pose) extrai os pontos do corpo, como ombros, cotovelos, quadris, joelhos e tornozelos.
- **Ângulos:** a partir desses pontos, calcula-se o ângulo das articulações relevantes (joelho no agachamento, cotovelo na flexão).
- **Identificação:** o exercício é reconhecido pela posição do corpo (em pé ou horizontal) e pela articulação que mais se movimenta.
- **Contagem:** cada repetição completa (descer e voltar à posição inicial) soma 1 ao contador.

## Escopo

**Incluído**
- Exercícios: flexão e agachamento.
- Entrada por webcam e/ou arquivo de vídeo.
- Exibição do esqueleto, do nome do exercício e do contador sobre o vídeo.

**Fora do escopo (por enquanto)**
- Correção de postura e avaliação da qualidade do movimento.
- Mais de uma pessoa na cena.
- Outros exercícios.

## Requisitos de uso
- Câmera preferencialmente de **lado** (perfil), para facilitar a medição dos ângulos.
- Corpo inteiro visível e boa iluminação.

## Tecnologias previstas
- Python 3
- OpenCV
- MediaPipe
- NumPy
