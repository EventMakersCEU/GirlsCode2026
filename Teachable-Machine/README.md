# Girls Code 2026 - Desafio Teachable Machine (CEU / Unifei)

Desafio de **Teachable Machine** do **Girls Code 2026**, organizado pelo CEU - Centro de Empreendedorismo Unifei

> **Foco do desafio:** treinar seu próprio **modelo de IA** no [Teachable Machine](https://teachablemachine.withgoogle.com/) e construir todo o **frontend (HTML)** e a **estilização (CSS)** do zero! A lógica em JavaScript já vem pronta e comentada em português - você só precisa conectar tudo.

---

## O que esse projeto faz?

São **três miniprojetos** que rodam **100% no navegador** (sem backend, sem servidor!) usando modelos de IA treinados por **você** no [Teachable Machine](https://teachablemachine.withgoogle.com/) do Google.

- **Projeto 1 - Imagem:** usa a **webcam** para reconhecer objetos, expressões, gestos, cores... o que você quiser ensinar!
- **Projeto 2 - Áudio:** usa o **microfone** para reconhecer palmas, assobios, palavras, sons de instrumentos...
- **Projeto 3 - Pose:** usa a **webcam** e detecta os pontos do **corpo da pessoa** (mãos, ombros, joelhos) para reconhecer poses, alongamentos, exercícios...

> **Por que Teachable Machine?** É uma ferramenta gratuita do Google que deixa qualquer pessoa treinar um modelo de IA em minutos, sem escrever uma linha de código. O modelo treinado roda direto no navegador usando TensorFlow.js (não precisa de servidor!).

## Estrutura do projeto

```
girls-code-teachable-machine/
├── 1-projeto-imagem/           # Reconhecimento de IMAGEM via webcam
│   ├── index.html              # HTML base
│   ├── style.css               # CSS vazio
│   └── script.js               # Lógica pronta (só falta colar a URL do modelo)
├── 2-projeto-audio/            # Reconhecimento de AUDIO via microfone
│   ├── index.html              # HTML base
│   ├── style.css               # CSS vazio
│   └── script.js               # Logica pronta (só falta colar a URL do modelo)
├── 3-projeto-pose/             # Reconhecimento de POSE via webcam
│   ├── index.html              # HTML base
│   ├── style.css               # CSS vazio
│   └── script.js               # Logica pronta (só falta colar a URL do modelo)
└── README.md
```

Cada pasta é um projeto **independente** - você pode escolher um, dois ou os três para trabalhar.

---

## Pré-requisitos

- Um **navegador moderno** (Chrome ou Edge funcionam melhor com câmera e microfone).
- Uma **conta Google** (gratuita) para acessar o Teachable Machine e salvar seu modelo.
- **Webcam** (para os projetos de imagem e pose) e **microfone** (para o de áudio).
- Conexão com a **internet** para carregar o modelo e as bibliotecas do TensorFlow.js.
- Um editor de código (recomendamos o **VS Code**).

> Não precisa instalar Python, Node, nem nada - tudo roda no navegador!

---

## Como treinar seu modelo no Teachable Machine

Esse é o **coração** do desafio. Antes de mexer no código, você precisa criar e treinar um modelo:

### 1) Acesse o Teachable Machine

Vá até [https://teachablemachine.withgoogle.com/](https://teachablemachine.withgoogle.com/) e clique em **"Comece já"**.

### 2) Escolha o tipo de projeto

Escolha de acordo com o subprojeto que você vai trabalhar:

- **Projeto de imagem** → escolha **"Projeto de imagem"** → **"Modelo de imagem padrão"**.
- **Projeto de áudio** → escolha **"Projeto de áudio"**.
- **Projeto de pose** → escolha **"Projeto de pose"**.

### 3) Treine as classes

- Crie **no mínimo 2 classes** (ex.: "feliz" e "triste", "palma" e "assobio", "braço para cima" e "agachada").
- Dê **nomes claros** para cada classe.
- Capture várias amostras de cada classe usando sua webcam/microfone (quanto mais, melhor - tente passar de 50 amostras por classe).
- Clique em **"Treinar Modelo"** e aguarde alguns segundos.
- Teste no painel **"Visualizar"** se está reconhecendo bem.

> Dica: capture amostras em **ângulos e luzes diferentes** para o modelo ser mais robusto.

### 4) Exporte o modelo

- Clique em **"Exportar modelo"** (canto superior direito).
- Vá na aba **"TensorFlow.js"**.
- Selecione **"Carregar (compartilhável)"**.
- Clique em **"Carregar meu modelo"** e aguarde o upload.
- Copie a **URL gerada** (ela termina com uma `/`, algo como `https://teachablemachine.withgoogle.com/models/AbCdEfGhI/`).

### 5) Cole a URL no `script.js`

Abra o arquivo `script.js` do subprojeto escolhido e cole a URL dentro das aspas, exemplo:

```js
const URL_DO_MODELO = "https://teachablemachine.withgoogle.com/models/XXXXXX/";
```

Pronto! Agora é só rodar o projeto.

---

## Como rodar o projeto

Como tudo é HTML + CSS + JS puro, basta abrir o `index.html` no navegador. Recomendamos **dois jeitos**:

### Opção A) Servidor local com Python (mais confiável)

Abra um terminal **dentro da pasta do subprojeto** (por exemplo, `1-projeto-imagem/`) e rode:

```bash
python -m http.server 5500
```

Depois, no navegador, acesse [http://localhost:5500](http://localhost:5500).

### Opção B) Extensão Live Server (mais prático)

- No VS Code, instale a extensão **Live Server**.
- Abra a pasta do subprojeto.
- Clique com o botão direito no `index.html` → **"Open with Live Server"**.

> **Atenção:** evite abrir o `index.html` clicando duas vezes (modo `file://`). Alguns navegadores bloqueiam a câmera/microfone fora de `http://` ou `https://`.

Quando o navegador abrir, **autorize o acesso à câmera/microfone** e clique no botão **"Iniciar"** da página. Em segundos você vai ver as porcentagens de cada classe aparecendo conforme o modelo reconhece o que vê/ouve.

---

## Como funciona cada projeto (visão rápida)

### 1) Projeto de Imagem (`1-projeto-imagem/`)

- Usa a biblioteca `@teachablemachine/image` por trás dos panos.
- Liga sua webcam, captura quadros e o modelo classifica cada quadro entre as classes treinadas.
- Os resultados aparecem como `nome_da_classe: probabilidade` dentro da `<div id="label-container">`.

### 2) Projeto de Áudio (`2-projeto-audio/`)

- Usa a biblioteca `@tensorflow-models/speech-commands` (reconhecimento de sons curtos).
- Liga o microfone, escuta em pequenos blocos e tenta classificar o som.
- O parâmetro `probabilityThreshold: 0.75` no `script.js` faz o modelo só considerar uma classe "detectada" se tiver pelo menos 75% de certeza. Você pode mexer nisso se quiser deixar mais sensível ou mais rigoroso.

### 3) Projeto de Pose (`3-projeto-pose/`)

- Usa a biblioteca `@teachablemachine/pose`, que por baixo dos panos roda a **PoseNet** (uma rede neural que encontra pontos do corpo).
- Além de classificar a pose, também **desenha o esqueleto** da pessoa em um `<canvas>` por cima da imagem da câmera.
- A função `desenharPose()` no `script.js` é responsável por isso.

---

## Como personalizar a interface (foco do desafio!)

Toda a estilização está **em branco** - é sua chance de brilhar. Cada projeto tem os mesmos elementos no HTML que você pode estilizar via CSS:


| Elemento HTML                | Para que serve                                                      |
| ---------------------------- | ------------------------------------------------------------------- |
| `h1`                         | Título da página                                                    |
| `#botao-iniciar`             | Botão que liga a câmera/microfone                                   |
| `#webcam-container` (imagem) | Onde o vídeo da webcam aparece                                      |
| `#canvas` (pose)             | Onde o vídeo + esqueleto da pessoa aparecem                         |
| `#label-container`           | Lista com o nome de cada classe e sua probabilidade em tempo real   |
| `#mensagem`                  | Mensagens de erro/aviso amigáveis (ex.: "Cole o link do modelo...") |


> Você também pode adicionar **novos elementos** no HTML (logos, ícones, instruções, créditos, etc.) - fique à vontade!

---

## Dicas para o desafio

1. **Qualidade do modelo importa muito.** Quanto mais amostras diferentes você capturar por classe, melhor o reconhecimento. Vale a pena gastar tempo aqui!
2. **Pense na experiência da usuária.** O que acontece antes de clicar em "Iniciar"? E enquanto carrega? E quando o modelo identifica algo? Use o CSS para deixar isso claro e divertido.
3. **Acessibilidade conta pontos!** Pense em contraste, foco visível no botão, tamanho de fonte adequado e textos descritivos.
4. **Use os IDs e elementos que já existem** no JS - a lógica preenche o `#label-container` automaticamente com uma `<div>` para cada classe. Você pode estilizar essas divs internas com `#label-container div { ... }`.
5. **Seja criativa com o tema!** Um modelo que reconhece emoções pode virar um detector de humor com emojis. Um modelo de palmas pode controlar uma luz que liga/desliga na tela. Um modelo de poses pode virar um app de exercícios.
6. **Mostre a porcentagem de um jeito visual** - barras de progresso, cores que mudam, animações... a criatividade é o limite!

---

## Problemas comuns


| Sintoma                                              | Possível causa                                           | Solução                                                                           |
| ---------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------- |
| "Não foi possível carregar o modelo"                 | Link colado errado                                       | Verifique se a URL termina com `/` e foi copiada inteira do Teachable Machine     |
| "Não foi possível acessar sua câmera/microfone"      | Permissão negada no navegador                            | Clique no cadeado ao lado da URL e libere a permissão                             |
| Câmera/microfone não funcionam abrindo o HTML direto | Navegador bloqueia em `file://`                          | Use `python -m http.server 5500` ou a extensão **Live Server**                    |
| Página em branco, nada acontece                      | Faltou colar a URL no `script.js`                        | Abra `script.js` e cole a URL dentro de `const URL_DO_MODELO = "..."`             |
| Reconhecimento muito ruim                            | Poucas amostras ou muito parecidas                       | Volte ao Teachable Machine e capture mais amostras em ângulos/luzes diferentes    |
| Áudio detecta tudo como "background noise"           | `probabilityThreshold` alto demais                       | No `script.js` do projeto de áudio, diminua o `probabilityThreshold` (ex.: `0.5`) |
| Funciona no Chrome mas não no Safari                 | Safari tem restrições com `getUserMedia` e TensorFlow.js | Recomende usar **Chrome** ou **Edge** durante o desafio                           |


---

Boa sorte, equipe! 💜

> Girls Code 2026 - CEU / Unifei

