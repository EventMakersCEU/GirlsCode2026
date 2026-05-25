// ============================================================
// PROJETO MODELO DE POSE - TEACHABLE MACHINE
// Girls Code 2026 - CEU/Unifei
// ============================================================

// COLE AQUI o link do seu modelo de pose do Teachable Machine.
// Copie a URL gerada e cole entre as aspas abaixo.
const URL_DO_MODELO = "";

// Variáveis que vamos usar durante todo o programa.
// Elas começam vazias e serão preenchidas quando o botão Iniciar for clicado.
let modelo;
let webcam;
let ctx;
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
    // O Teachable Machine usa por baixo dos panos uma rede chamada PoseNet,
    // que sabe encontrar pontos do corpo (mãos, ombros, joelhos...) na imagem.
    try {
        modelo = await tmPose.load(urlDoModelJson, urlDoMetadataJson);
        totalDeClasses = modelo.getTotalClasses();
    } catch (erro) {
        mostrarMensagem("Não foi possível carregar o modelo. Verifique se o link colado na variável URL_DO_MODELO está correto.");
        return;
    }

    // Configura o tamanho do quadrado da câmera e se a imagem fica espelhada.
    const tamanho = 200;
    const espelhar = true;
    webcam = new tmPose.Webcam(tamanho, tamanho, espelhar);

    // Tenta ligar a câmera. Pode falhar se a participante negar a permissão
    // ou se o computador não tiver câmera.
    try {
        await webcam.setup();
        await webcam.play();
    } catch (erro) {
        mostrarMensagem("Não foi possível acessar sua câmera. Verifique se você deu permissão no navegador.");
        return;
    }

    // Prepara o <canvas> do HTML para receber a imagem da câmera
    // junto com o esqueleto desenhado por cima.
    const canvas = document.getElementById("canvas");
    canvas.width = tamanho;
    canvas.height = tamanho;
    ctx = canvas.getContext("2d");

    // Cria uma linha de texto vazia para cada classe que o modelo reconhece.
    // É nessas linhas que vamos mostrar a porcentagem de cada pose detectada.
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

// Função que descobre a pose da pessoa na câmera e mostra o resultado na tela.
async function prever() {
    // "pose" contém os pontos do corpo encontrados (keypoints).
    // "posenetOutput" é o resultado bruto que será usado para classificar a pose.
    const { pose, posenetOutput } = await modelo.estimatePose(webcam.canvas);

    // Agora o modelo classifica entre as poses que você treinou.
    const predicao = await modelo.predict(posenetOutput);

    for (let i = 0; i < totalDeClasses; i++) {
        const nomeDaClasse = predicao[i].className;
        const probabilidade = predicao[i].probability.toFixed(2);
        const textoFinal = nomeDaClasse + ": " + probabilidade;
        containerDeRotulos.childNodes[i].innerHTML = textoFinal;
    }

    // Desenha a imagem da webcam e o esqueleto da pessoa no <canvas>.
    desenharPose(pose);
}

// Função que desenha no <canvas> a imagem da câmera + os pontos e linhas do corpo.
function desenharPose(pose) {
    if (webcam.canvas) {
        // Primeiro desenha a imagem da webcam.
        ctx.drawImage(webcam.canvas, 0, 0);

        // Depois, se uma pose foi detectada, desenha os pontos e o esqueleto por cima.
        if (pose) {
            // Só desenha pontos que o modelo tem pelo menos 50% de certeza.
            const confiancaMinima = 0.5;
            tmPose.drawKeypoints(pose.keypoints, confiancaMinima, ctx);
            tmPose.drawSkeleton(pose.keypoints, confiancaMinima, ctx);
        }
    }
}
