/* ============================================================
   script.js - Lógica do chat (envia pergunta para o backend)
   ------------------------------------------------------------
   Este arquivo conecta o formulário HTML ao servidor Python.
   Você pode estudá-lo para entender o fluxo e estilizá-lo
   no style.css usando as classes que ele cria.
   ============================================================ */

// Endereço do backend FastAPI rodando na sua máquina.
// Se você mudar a porta do uvicorn, mude aqui também.
const API_URL = "http://localhost:8000/perguntar";

const form = document.getElementById("form-chat");
const campoPergunta = document.getElementById("campo-pergunta");
const botaoEnviar = document.getElementById("botao-enviar");
const containerMensagens = document.getElementById("mensagens");

/**
 * Cria uma nova bolha de mensagem na tela.
 *
 * @param {string} texto   - Conteúdo a ser exibido.
 * @param {"usuario"|"bot"|"erro"} autor - Quem mandou a mensagem.
 */
function adicionarMensagem(texto, autor) {
  const div = document.createElement("div");
  div.classList.add("mensagem", `mensagem-${autor}`);
  div.textContent = texto;

  containerMensagens.appendChild(div);
  containerMensagens.scrollTop = containerMensagens.scrollHeight;
  return div;
}

/**
 * Liga/desliga o formulário enquanto a IA está pensando.
 */
function definirEstadoCarregando(carregando) {
  campoPergunta.disabled = carregando;
  botaoEnviar.disabled = carregando;
  botaoEnviar.textContent = carregando ? "Enviando..." : "Enviar";
}

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const pergunta = campoPergunta.value.trim();
  if (!pergunta) {
    return;
  }

  adicionarMensagem(pergunta, "usuario");
  campoPergunta.value = "";

  const aguardando = adicionarMensagem("Pensando...", "bot");
  definirEstadoCarregando(true);

  try {
    const resposta = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pergunta }),
    });

    if (!resposta.ok) {
      aguardando.remove();
      adicionarMensagem(
        "Ops! O servidor respondeu com um erro. Tente novamente em alguns instantes.",
        "erro"
      );
      return;
    }

    const dados = await resposta.json();
    aguardando.remove();
    adicionarMensagem(
      dados.resposta || "A IA não retornou nenhum texto.",
      "bot"
    );
  } catch (erro) {
    // Esse catch é acionado, por exemplo, quando o backend não está no ar.
    // A mensagem fica em português para não confundir as participantes.
    aguardando.remove();
    adicionarMensagem(
      "Ops! Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 8000.",
      "erro"
    );
    console.error("[Girls Code RAG] Erro ao chamar a API:", erro);
  } finally {
    definirEstadoCarregando(false);
    campoPergunta.focus();
  }
});
