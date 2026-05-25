// ============================================================
// PROJETO MODELO DE ÁUDIO - TEACHABLE MACHINE
// Girls Code 2026 - CEU/Unifei
// ============================================================

// COLE AQUI o link do seu modelo de áudio do Teachable Machine.
// Copie a URL gerada e cole entre as aspas abaixo.
const URL_DO_MODELO = "";

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

// Função que cria e carrega o modelo de áudio treinado no Teachable Machine.
// "BROWSER_FFT" significa que o reconhecimento de som vai usar a FFT
// (Transformada Rápida de Fourier) que já existe dentro do navegador.
async function criarModelo() {
    const urlDoModelJson = URL_DO_MODELO + "model.json";
    const urlDoMetadataJson = URL_DO_MODELO + "metadata.json";

    const reconhecedor = speechCommands.create(
        "BROWSER_FFT",
        undefined,
        urlDoModelJson,
        urlDoMetadataJson
    );

    // Espera o modelo terminar de carregar antes de devolver ele.
    await reconhecedor.ensureModelLoaded();
    return reconhecedor;
}

// Função principal: carrega o modelo, liga o microfone e começa a escutar.
async function iniciar() {

    // Primeira verificação: a participante já colou o link do modelo?
    if (URL_DO_MODELO === "") {
        mostrarMensagem("Ops! Cole o link do seu modelo do Teachable Machine na variável URL_DO_MODELO dentro do arquivo script.js.");
        return;
    }

    // Tenta carregar o modelo de áudio treinado.
    let reconhecedor;
    try {
        reconhecedor = await criarModelo();
    } catch (erro) {
        mostrarMensagem("Não foi possível carregar o modelo. Verifique se o link colado na variável URL_DO_MODELO está correto.");
        return;
    }

    // Pega a lista de nomes das classes que o modelo aprendeu
    // (por exemplo: "palma", "assobio", "ruído de fundo"...).
    const nomesDasClasses = reconhecedor.wordLabels();

    // Cria uma linha de texto vazia para cada classe.
    // É nessas linhas que vamos mostrar a porcentagem de cada som detectado.
    const containerDeRotulos = document.getElementById("label-container");
    for (let i = 0; i < nomesDasClasses.length; i++) {
        containerDeRotulos.appendChild(document.createElement("div"));
    }

    // Liga o microfone e começa a escutar.
    // Pode falhar se a participante negar a permissão de microfone.
    try {
        reconhecedor.listen(
            (resultado) => {
                // Para cada classe, mostra o nome dela e a chance (probabilidade)
                // de o som atual ser daquela classe.
                for (let i = 0; i < nomesDasClasses.length; i++) {
                    const nomeDaClasse = nomesDasClasses[i];
                    const probabilidade = resultado.scores[i].toFixed(2);
                    const textoFinal = nomeDaClasse + ": " + probabilidade;
                    containerDeRotulos.childNodes[i].innerHTML = textoFinal;
                }
            },
            {
                // Inclui o espectrograma (gráfico do som) no resultado.
                includeSpectrogram: true,
                // Só considera uma classe "detectada" se a chance for maior que 75%.
                probabilityThreshold: 0.75,
                // Também avisa quando o som é só barulho de fundo ou desconhecido.
                invokeCallbackOnNoiseAndUnknown: true,
                // Sobreposição entre uma escuta e outra (50% = mais reativo).
                overlapFactor: 0.50
            }
        );
    } catch (erro) {
        mostrarMensagem("Não foi possível acessar seu microfone. Verifique se você deu permissão no navegador.");
    }
}
