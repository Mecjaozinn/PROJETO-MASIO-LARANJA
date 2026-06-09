let sessao = [], atual = 0, respostas = [], nomeJog = "", inicioTime = null;
const nivelMap = { 1: ["Fácil","nivel-1"], 2: ["Média","nivel-2"], 3: ["Difícil","nivel-3"] };

async function iniciarQuiz() {
  nomeJog = document.getElementById("nome-jogador").value.trim() || "Anônimo";
  mostrarTela("screen-quiz");
  try {
    const res = await fetch("/api/quiz/iniciar");
    sessao = await res.json();
    atual = 0; respostas = [];
    inicioTime = performance.now();
    mostrarPergunta();
  } catch(err) { alert("Erro ao carregar o quiz. Verifique sua conexão."); }
}

function mostrarPergunta() {
  const p = sessao[atual], total = sessao.length;
  document.getElementById("quiz-counter").textContent = `Pergunta ${atual+1} de ${total}`;
  document.getElementById("progress-fill").style.width = `${(atual/total)*100}%`;
  const [texto, cls] = nivelMap[p.nivel];
  const nivelEl = document.getElementById("quiz-nivel");
  nivelEl.textContent = texto; nivelEl.className = `quiz-nivel ${cls}`;
  document.getElementById("quiz-pergunta").textContent = p.texto;
  const letras = ["A","B","C","D"];
  document.getElementById("quiz-opcoes").innerHTML = p.opcoes.map((op,i) =>
    `<button class="opcao-btn" onclick="responder('${letras[i]}')">
       <span class="letra">${letras[i]}</span><span>${op}</span>
     </button>`
  ).join("");
}

function responder(letra) {
  const p = sessao[atual];
  respostas.push({ chave: p.chave, idx: p.idx, resposta: letra });
  const btns = document.querySelectorAll(".opcao-btn");
  const letras = ["A","B","C","D"];
  btns.forEach(btn => btn.disabled = true);
  btns.forEach((btn,i) => {
    if (letras[i] === p.resp)                btn.classList.add("opcao-correta");
    if (letras[i] === letra && letra!==p.resp) btn.classList.add("opcao-errada");
  });
  setTimeout(() => { atual++; atual < sessao.length ? mostrarPergunta() : finalizarQuiz(); }, 1000);
}

async function finalizarQuiz() {
  const tempo = (performance.now() - inicioTime) / 1000;
  try {
    const res = await fetch("/api/quiz/resultado", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome: nomeJog, tempo, respostas }),
    });
    mostrarResultado(await res.json());
  } catch(err) { alert("Erro ao salvar resultado."); }
}

function mostrarResultado(data) {
  mostrarTela("screen-resultado");
  const emojis = {5:"🏆",4:"🌟",3:"👍",2:"📚",1:"💡",0:"🔍"};
  const msgs   = {
    5:"Parabéns! Você é um guardião da proteção infantil!",
    4:"Muito bem! Você está bem informado.",
    3:"Bom trabalho! Continue aprendendo.",
    2:"Continue se informando — cada conhecimento protege!",
    1:"Valeu por jogar. Aprenda mais sobre o Maio Laranja!",
    0:"Vamos aprender mais sobre esse tema tão importante!"
  };
  document.getElementById("resultado-emoji").textContent  = emojis[data.nota] || "🎯";
  document.getElementById("resultado-titulo").textContent = msgs[data.nota]   || "";
  document.getElementById("resultado-nota").textContent   = `${data.nota} / ${data.total}`;
  document.getElementById("resultado-tempo").textContent  = `Tempo: ${data.tempo}s`;
  document.getElementById("resultado-detalhes").innerHTML = data.detalhes.map(d =>
    `<div class="detalhe-item"><span>${d.acertou?"✅":"❌"}</span><span>${d.texto}</span></div>`
  ).join("");
}

function mostrarTela(id) {
  document.querySelectorAll(".quiz-screen").forEach(el => el.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}
