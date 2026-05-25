// ============================================================
// PROJETO MODELO DE IMAGEM - TEACHABLE MACHINE
// Girls Code 2026 - CEU/Unifei
// ============================================================

// COLE AQUI o link do seu modelo de imagem do Teachable Machine.
// Copie a URL gerada e cole entre as aspas abaixo.
const URL_DO_MODELO = "";

// Variáveis que vamos usar durante todo o programa.
// Elas começam vazias e serão preenchidas quando o botão Iniciar for clicado.
let modelo;
let webcam;
let containerDeRotulos;
let totalDeClasses;

// Pega o botão "Iniciar" do HTML e diz para ele executar a função iniciar()
// quando a participante clicar nele.
const botaoIniciar = document.getElementById("botao-iniciar");
botaoIniciar.addEventListener("click", iniciar);

// Função que mostra mensagens amigáveis na tela.
// Sempre que algo der errado, chamamos essa função em vez de usar alert().
function mostrarMensagem(texto) {
    const divMensagem = document.getElementById("mensagem");
    divMensagem.innerHTML = texto;
}

// Função principal: carrega o modelo, liga a câmera e começa o reconhecimento.
async function iniciar() {

    // Primeira verificação: a participante já colou o link do modelo?
    if (URL_DO_MODELO === "") {
        mostrarMensagem("Ops! Cole o link do seu modelo do Teachable Machine na variável URL_DO_MODELO dentro do arquivo script.js.");
        return;
    }

    // Monta os caminhos completos para os arquivos do modelo.
    const urlDoModelJson = URL_DO_MODELO + "model.json";
    const urlDoMetadataJson = URL_DO_MODELO + "metadata.json";

    // Tenta carregar o modelo treinado no Teachable Machine.
    try {
        modelo = await tmImage.load(urlDoModelJson, urlDoMetadataJson);
        totalDeClasses = modelo.getTotalClasses();
    } catch (erro) {
        mostrarMensagem("Não foi possível carregar o modelo. Verifique se o link colado na variável URL_DO_MODELO está correto.");
        return;
    }

    // Configura a webcam.
    // O parâmetro "espelhar" inverte a imagem (igual a um espelho de verdade).
    const espelhar = true;
    webcam = new tmImage.Webcam(200, 200, espelhar);

    // Tenta ligar a câmera. Pode falhar se a participante negar a permissão
    // ou se o computador não tiver câmera.
    try {
        await webcam.setup();
        await webcam.play();
    } catch (erro) {
        mostrarMensagem("Não foi possível acessar sua câmera. Verifique se você deu permissão no navegador.");
        return;
    }

    // Coloca o vídeo da webcam dentro do nosso container no HTML.
    document.getElementById("webcam-container").appendChild(webcam.canvas);

    // Cria uma linha de texto vazia para cada classe que o modelo reconhece.
    // É nessas linhas que vamos mostrar a porcentagem de cada classe.
    containerDeRotulos = document.getElementById("label-container");
    for (let i = 0; i < totalDeClasses; i++) {
        containerDeRotulos.appendChild(document.createElement("div"));
    }

    // Inicia o loop de reconhecimento (chama a função "loop" várias vezes por segundo).
    window.requestAnimationFrame(loop);
}

// Função "loop": fica rodando o tempo todo enquanto a câmera estiver ligada.
// A cada quadro (frame), ela atualiza a imagem da webcam e faz uma nova predição.
async function loop() {
    webcam.update();
    await prever();
    window.requestAnimationFrame(loop);
}

// Função que pega o frame atual da webcam e pergunta ao modelo:
// "O que você está vendo agora?". Depois mostra o resultado na tela.
async function prever() {
    const predicao = await modelo.predict(webcam.canvas);

    for (let i = 0; i < totalDeClasses; i++) {
        const nomeDaClasse = predicao[i].className;
        const probabilidade = predicao[i].probability.toFixed(2);
        const textoFinal = nomeDaClasse + ": " + probabilidade;
        containerDeRotulos.childNodes[i].innerHTML = textoFinal;
    }
}
