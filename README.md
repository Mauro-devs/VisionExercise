# VisionExercise

Projeto de visão computacional que **conta as repetições de agachamento e de flexão** em tempo real, a partir da webcam ou de um vídeo. O exercício é escolhido por **gesto de mão**, e o programa só conta quando o corpo está inteiro no quadro e na postura certa.

## Como funciona

1. **Escolha do exercício.** Com a mão perto da câmera, faça o gesto e segure por cerca de 1 segundo:
   - **1 dedo** (só o indicador levantado): agachamento.
   - **2 dedos** (indicador e médio, o "V"): flexão.
2. **Posicionamento.** Aparece uma contagem regressiva de 3 segundos. Afaste-se e fique de lado para a câmera, com o corpo inteiro visível. A contagem só avança enquanto o corpo estiver válido.
3. **Exercício.** O programa mostra o esqueleto, o ângulo da articulação e o contador de repetições.

### Teclas

| Tecla | O que faz |
|---|---|
| `B` | Volta para a escolha do exercício |
| `A` | Mostra ou esconde o esqueleto e o ângulo (o contador continua na tela) |
| `Q` | Sai do programa |

A janela do vídeo precisa estar em foco para as teclas funcionarem.

## Como rodar

**Requisitos:** Python 3.10 ou mais novo e o [`uv`](https://docs.astral.sh/uv/).

```bash
git clone <endereço do repositório>
cd VisionExercise
uv sync
uv run python main.py
```

Na **primeira execução**, o programa baixa sozinho os dois modelos do MediaPipe (cerca de 14 MB no total), o que leva alguns segundos.

### Opções

| Opção | O que faz |
|---|---|
| `--fonte 0` | Webcam de índice 0 (padrão). Use `--fonte 1`, `--fonte 2`... se houver mais de uma câmera |
| `--fonte caminho/do/video.mp4` | Usa um arquivo de vídeo em vez da webcam |
| `--exercicio agachamento` ou `--exercicio flexao` | Pula a escolha por gesto e já começa no exercício |
| `--sem-espelho` | Não espelha a imagem da webcam (por padrão ela é espelhada) |

Exemplos:

```bash
uv run python main.py
uv run python main.py --fonte 1
uv run python main.py --fonte videos/meu_video.mp4 --exercicio agachamento
uv run python main.py --help
```

A pasta `videos/` está vazia no repositório: para usar um vídeo, coloque o arquivo nela (ou passe qualquer caminho em `--fonte`).

## Requisitos de uso

- Câmera preferencialmente de **lado** (perfil), para facilitar a medição dos ângulos.
- **Uma pessoa** na cena, com boa iluminação.
- O que precisa aparecer inteiro no quadro:
  - **Agachamento:** ombros, quadris, joelhos e tornozelos.
  - **Flexão:** cabeça, ombros e quadris (os pés não são exigidos).
- O tronco precisa estar na postura do exercício: em pé ou inclinado para frente no agachamento, e na horizontal na flexão. Isso impede, por exemplo, que dobrar só o braço em pé seja contado como flexão.

## Como a contagem é feita

| Exercício | Articulação medida | A repetição conta quando o ângulo... |
|---|---|---|
| Agachamento | Joelho (quadril, joelho, tornozelo) | cai abaixo de **100°** e volta a passar de **160°** |
| Flexão | Cotovelo (ombro, cotovelo, punho) | cai abaixo de **110°** e volta a passar de **150°** |

- O programa usa o **lado do corpo mais visível** para a câmera.
- O ângulo passa por uma média de 150 ms para reduzir o tremor.
- Se a pessoa sair do quadro ou da postura por **1 segundo**, a contagem é **pausada**. Ao voltar, o total é mantido, mas a repetição que ficou incompleta não é contada.

## Escopo

**Incluído**
- Exercícios: flexão e agachamento.
- Entrada por webcam ou arquivo de vídeo.
- Escolha do exercício por gesto de mão.
- Esqueleto, ângulo, nome do exercício e contador sobre o vídeo.

**Implementação futura**
- Correção de postura e avaliação da qualidade do movimento.
- Mais de uma pessoa na cena.
- Outros exercícios.

## Limitações conhecidas

- Os limites de ângulo foram ajustados com **poucos vídeos**, de uma pessoa em cada exercício. Em outra pessoa ou ângulo de câmera, uma repetição mais rasa pode não contar.
- O reconhecimento dos gestos foi validado com uma pessoa.
- Com o corpo muito parcial no quadro, o modelo de pose pode "inventar" pontos que não vê, e a validação nem sempre bloqueia esse caso.

## Estrutura do projeto

```
main.py                  ponto de entrada: só chama executar()
src/
  app.py                 executar() (monta tudo e roda o loop) e a classe App (um método por modo)
  cli.py                 argumentos de linha de comando
  fonte.py               abre a webcam ou o vídeo
  pose.py                detecta a pose, valida o corpo, calcula o ângulo e desenha
  modelos/carregar.py    baixa os modelos do MediaPipe e monta as opções
  gestos.py              reconhece e confirma o gesto de escolha
  exercicios.py          definição dos exercícios e contador de repetições
  robustez.py            validação do corpo, pausa e suavização do ângulo
  angulos.py             cálculo de ângulos
  desenho.py             esqueleto, textos e contador sobre a imagem
models/                  modelos baixados na primeira execução
videos/                  vídeos de teste
```

O programa tem três modos, tratados pela classe `App`: **escolha** (gesto), **posicionamento** (contagem regressiva) e **exercício** (contagem de repetições).

## Tecnologias

- Python 3
- OpenCV
- MediaPipe (Pose Landmarker e Gesture Recognizer)
- NumPy
