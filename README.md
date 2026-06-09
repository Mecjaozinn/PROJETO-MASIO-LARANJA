# PROJETO-MAIO-LARANJA
Projeto sobre o Maio Laranja onde tem um quiz com raking e um sitede disque denuncia
# 🟠 Documentação — Site Maio Laranja

**Versão:** 1.0  
**Tema:** Combate ao Abuso e Exploração Sexual de Crianças e Adolescentes  
**Stack:** Python (Flask) + HTML + CSS + JavaScript + SQLite

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Estrutura de Arquivos](#2-estrutura-de-arquivos)
3. [Como Rodar Localmente](#3-como-rodar-localmente)
4. [Backend — app.py](#4-backend--apppy)
5. [Frontend — index.html](#5-frontend--indexhtml)
6. [Frontend — quiz.html](#6-frontend--quizhtml)
7. [Frontend — ranking.html](#7-frontend--rankinghtml)
8. [CSS — style.css](#8-css--stylecss)
9. [JavaScript — main.js](#9-javascript--mainjs)
10. [JavaScript — quiz.js](#10-javascript--quizjs)
11. [API — Tabela de Rotas](#11-api--tabela-de-rotas)
12. [Banco de Dados](#12-banco-de-dados)
13. [Deploy no Render (gratuito)](#13-deploy-no-render-gratuito)
14. [Gerar QR Code](#14-gerar-qr-code)

---

## 1. Visão Geral

O site tem **3 páginas** e **4 endpoints de API**:

| Página | URL | Função |
|--------|-----|--------|
| Principal | `/` | Conscientização, história da Araceli e formulário de denúncia |
| Quiz | `/quiz` | Quiz interativo com 5 perguntas e cronômetro |
| Ranking | `/ranking` | Top 20 melhores pontuações |

**Fluxo do usuário:**
```
Acessa o site → Lê sobre o Maio Laranja → Faz uma denúncia (anônima)
                                         → Entra no Quiz → Vê seu resultado → Vê o Ranking
```

---

## 2. Estrutura de Arquivos

```
maio-laranja/
│
├── app.py                  ← Servidor Python (toda a lógica do backend)
├── requirements.txt        ← Dependências Python
├── Procfile                ← Instrução de inicialização para o servidor
├── render.yaml             ← Configuração automática do Render
├── dados.db                ← Banco de dados (criado automaticamente)
│
├── templates/              ← Páginas HTML (renderizadas pelo Flask)
│   ├── index.html          ← Página principal
│   ├── quiz.html           ← Página do quiz
│   └── ranking.html        ← Página do ranking
│
└── static/                 ← Arquivos estáticos (CSS e JS)
    ├── css/
    │   └── style.css       ← Todo o visual do site
    └── js/
        ├── main.js         ← Lógica do formulário de denúncia
        └── quiz.js         ← Lógica completa do quiz
```

---

## 3. Como Rodar Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado
- Terminal (Prompt de Comando, PowerShell ou Terminal do Mac/Linux)

### Passo a passo

```bash
# 1. Entre na pasta do projeto
cd maio-laranja

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor
python app.py

# 4. Abra no navegador
# http://localhost:5000
```

O banco de dados `dados.db` é criado automaticamente na primeira vez que você rodar.

---

## 4. Backend — `app.py`

Este é o **coração do projeto**. Ele usa o framework **Flask** para:
- Servir as páginas HTML
- Receber e salvar denúncias
- Gerar perguntas aleatórias do quiz
- Corrigir respostas e salvar no ranking
- Retornar o ranking para a página

### Importações

```python
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3   # Banco de dados leve, sem instalação extra
import json
import random    # Para embaralhar as perguntas
import os        # Para ler variáveis de ambiente (porta do servidor)
import time
```

### Inicialização do Flask

```python
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
```

- `template_folder="templates"` → Flask vai procurar os HTMLs na pasta `templates/`
- `static_folder="static"` → Flask vai servir CSS e JS da pasta `static/`
- `CORS(app)` → Permite que o site seja acessado de qualquer domínio (necessário para funcionar no celular via QR Code)

### Banco de Dados

```python
DB_PATH = "dados.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)      # Cria/abre o arquivo do banco
    cur = conn.cursor()                  # Cursor = ferramenta para executar SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID automático
            tipo TEXT NOT NULL,                    -- Tipo de violação (obrigatório)
            descricao TEXT NOT NULL,               -- Descrição (obrigatório)
            local TEXT,                            -- Local aproximado (opcional)
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Data/hora automática
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,     -- Nome do jogador
            nota INTEGER NOT NULL,  -- Quantas acertou (0 a 5)
            tempo REAL NOT NULL,    -- Tempo em segundos
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()   # Salva as mudanças
    conn.close()    # Fecha a conexão

init_db()  # Roda ao iniciar o servidor
```

**`CREATE TABLE IF NOT EXISTS`** → Só cria a tabela se ela ainda não existir.  
Isso garante que o banco não seja apagado toda vez que o servidor reiniciar.

### Dicionário de Perguntas

```python
perguntas = {
    "perg_facil": [
        {
            "texto": "Em que data acontece o Dia Nacional...",
            "opcoes": ["18 de maio", "12 de outubro", "7 de setembro", "25 de dezembro"],
            "resp": "A"   # ← A resposta correta é sempre uma letra: A, B, C ou D
        },
        # ... mais 9 perguntas fáceis
    ],
    "perg_media": [ ... ],   # 10 perguntas médias
    "perg_dificil": [ ... ], # 5 perguntas difíceis
}
```

Cada pergunta é um **dicionário Python** com 3 chaves:
- `"texto"` → O enunciado da pergunta
- `"opcoes"` → Lista com as 4 alternativas (A, B, C, D)
- `"resp"` → Letra da resposta correta

### Rotas de Páginas

```python
@app.route("/")           # Quando alguém acessa o site raiz
def index():
    return render_template("index.html")   # Mostra a página principal

@app.route("/quiz")       # Quando alguém acessa /quiz
def quiz_page():
    return render_template("quiz.html")

@app.route("/ranking")    # Quando alguém acessa /ranking
def ranking_page():
    return render_template("ranking.html")
```

O `@app.route(...)` é um **decorador** — ele diz ao Flask qual função chamar quando alguém acessar aquela URL.

### API — Receber Denúncia

```python
@app.route("/api/denuncia", methods=["POST"])
def receber_denuncia():
    data = request.get_json()             # Lê o JSON enviado pelo formulário
    tipo      = data.get("tipo", "").strip()
    descricao = data.get("descricao", "").strip()
    local     = data.get("local", "").strip()

    # Validação: campos obrigatórios
    if not tipo or not descricao:
        return jsonify({"erro": "Preencha os campos obrigatórios."}), 400

    # Salva no banco
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO denuncias (tipo, descricao, local) VALUES (?, ?, ?)",
        (tipo, descricao, local)       # Os ? evitam SQL Injection (ataque hacker)
    )
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Denúncia registrada com sucesso!"}), 201
```

**Por que `?` e não f-string?**  
Usar `f"INSERT ... VALUES ('{tipo}')"` é perigoso — um usuário mal-intencionado pode digitar SQL no campo e manipular o banco. Os `?` protegem contra isso (chamado de **SQL Injection**).

### API — Iniciar Quiz (Gerar Perguntas Aleatórias)

```python
@app.route("/api/quiz/iniciar", methods=["GET"])
def iniciar_quiz():
    niveis = [1, 1, 2, 2, 3]   # 2 fáceis, 2 médias, 1 difícil
    random.shuffle(niveis)       # Embaralha a ordem

    # Sorteia índices únicos para cada nível
    idx_f = random.sample(range(len(perguntas["perg_facil"])), 2)   # 2 de 10 fáceis
    idx_m = random.sample(range(len(perguntas["perg_media"])), 2)   # 2 de 10 médias
    idx_d = random.sample(range(len(perguntas["perg_dificil"])), 1) # 1 de 5 difíceis

    pool = {1: iter(idx_f), 2: iter(idx_m), 3: iter(idx_d)}

    sessao = []
    for nivel in niveis:
        chave = ["perg_facil", "perg_media", "perg_dificil"][nivel - 1]
        idx = next(pool[nivel])
        p = perguntas[chave][idx]
        sessao.append({
            "nivel": nivel,    # 1, 2 ou 3 (fácil, médio, difícil)
            "chave": chave,    # Nome do grupo de perguntas
            "idx": idx,        # Índice da pergunta no dicionário
            "texto": p["texto"],
            "opcoes": p["opcoes"],
            # ⚠️ A resposta correta NÃO é enviada aqui (ficaria visível no navegador)
        })

    return jsonify(sessao)   # Envia as 5 perguntas para o JavaScript
```

**Segurança importante:** A resposta correta (`"resp"`) não é enviada ao navegador. A correção só acontece no servidor, impedindo que alguém "cole" no quiz inspecionando o código.

### API — Resultado do Quiz

```python
@app.route("/api/quiz/resultado", methods=["POST"])
def resultado_quiz():
    data      = request.get_json()
    nome      = data.get("nome", "Anônimo").strip() or "Anônimo"
    tempo     = float(data.get("tempo", 0))
    respostas = data.get("respostas", [])

    nota = 0
    detalhes = []

    for r in respostas:
        chave    = r["chave"]          # Ex: "perg_facil"
        idx      = r["idx"]            # Ex: 3 (índice da pergunta)
        resp_usr = r["resposta"].upper()               # Resposta do jogador: "A", "B"...
        correta  = perguntas[chave][idx]["resp"]       # Resposta correta no servidor

        acertou = resp_usr == correta
        if acertou:
            nota += 1

        detalhes.append({
            "texto": perguntas[chave][idx]["texto"],
            "resposta_usuario": resp_usr,
            "resposta_correta": correta,
            "acertou": acertou,
        })

    # Salva no ranking
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO ranking (nome, nota, tempo) VALUES (?, ?, ?)",
        (nome, nota, tempo)
    )
    conn.commit()
    conn.close()

    return jsonify({"nota": nota, "total": len(respostas), "tempo": round(tempo, 2), "detalhes": detalhes})
```

### API — Ranking

```python
@app.route("/api/ranking", methods=["GET"])
def get_ranking():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        "SELECT nome, nota, tempo FROM ranking ORDER BY nota DESC, tempo ASC LIMIT 20"
        # ORDER BY nota DESC → Quem acertou mais aparece primeiro
        # tempo ASC         → Em caso de empate, quem foi mais rápido aparece primeiro
        # LIMIT 20          → Só mostra os top 20
    )
    rows = cur.fetchall()
    conn.close()

    resultado = [{"nome": r[0], "nota": r[1], "tempo": r[2]} for r in rows]
    return jsonify(resultado)
```

### Inicialização do Servidor

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Se existir a variável de ambiente PORT (definida pelo Render), usa ela
    # Caso contrário, usa a porta 5000 (local)
    app.run(host="0.0.0.0", port=port, debug=False)
    # host="0.0.0.0" → Aceita conexões de qualquer IP (necessário para celular na mesma rede)
```

---

## 5. Frontend — `index.html`

Página principal com 5 seções:

### Seções da Página

| Seção | ID | Descrição |
|-------|----|-----------|
| Hero | — | Título principal, botões de ação e números de referência (100, 18/05, ECA) |
| Sobre | `#sobre` | Explicação do Maio Laranja e 3 cards informativos |
| Araceli | `#araceli` | História de Araceli Crespo com fundo escuro |
| Denúncia | `#denuncia` | Formulário anônimo de denúncia |
| Quiz CTA | — | Seção laranja chamando para o quiz |

### Estrutura do Formulário de Denúncia

```html
<!-- Formulário principal -->
<div class="form-card" id="form-area">

  <!-- Campo obrigatório: tipo de violação -->
  <select id="tipo">
    <option value="abuso_sexual">Abuso sexual</option>
    <option value="exploracao_sexual">Exploração sexual</option>
    <!-- ... -->
  </select>

  <!-- Campo opcional: localização -->
  <input type="text" id="local" />

  <!-- Campo obrigatório: descrição -->
  <textarea id="descricao"></textarea>

  <!-- Botão que chama a função enviarDenuncia() do main.js -->
  <button onclick="enviarDenuncia()">Enviar denúncia</button>
</div>

<!-- Mensagem de sucesso (escondida por padrão, aparece após envio) -->
<div class="form-sucesso hidden" id="form-sucesso">
  <h3>Denúncia registrada!</h3>
  <!-- Botão que chama novaDenuncia() para limpar e mostrar o form de novo -->
  <button onclick="novaDenuncia()">Fazer outra denúncia</button>
</div>
```

**Como o `hidden` funciona:** A classe `hidden` tem `display: none` no CSS. O JavaScript adiciona/remove essa classe para mostrar/esconder as divs.

---

## 6. Frontend — `quiz.html`

A página do quiz funciona como um **aplicativo de tela única** — há 3 "telas" dentro do mesmo HTML, e o JavaScript mostra/esconde cada uma conforme o progresso:

```html
<!-- TELA 1: Entrada do nome -->
<div class="quiz-screen" id="screen-nome">
  <input id="nome-jogador" />
  <button onclick="iniciarQuiz()">Começar</button>
</div>

<!-- TELA 2: Perguntas (começa escondida) -->
<div class="quiz-screen hidden" id="screen-quiz">
  <div id="progress-fill"></div>   <!-- Barra de progresso -->
  <div id="quiz-nivel"></div>       <!-- Badge: Fácil / Médio / Difícil -->
  <h2 id="quiz-pergunta"></h2>      <!-- Texto da pergunta -->
  <div id="quiz-opcoes"></div>       <!-- Botões das alternativas (gerados pelo JS) -->
</div>

<!-- TELA 3: Resultado (começa escondida) -->
<div class="quiz-screen hidden" id="screen-resultado">
  <div id="resultado-emoji"></div>
  <div id="resultado-nota"></div>
  <div id="resultado-detalhes"></div>  <!-- Lista de acertos/erros -->
</div>
```

O JavaScript preenche todos os elementos `id="..."` dinamicamente.

---

## 7. Frontend — `ranking.html`

Página simples que carrega e exibe o ranking ao ser aberta:

```html
<div id="ranking-lista">
  <p class="loading">Carregando...</p>   <!-- Mostrado enquanto busca os dados -->
</div>

<script>
  async function carregarRanking() {
    const res   = await fetch("/api/ranking");    // Busca os dados da API
    const dados = await res.json();               // Converte para array JavaScript

    const medalhas = ["🥇", "🥈", "🥉"];

    // Gera o HTML de cada linha do ranking dinamicamente
    lista.innerHTML = dados.map((jogador, posicao) => `
      <div class="ranking-row">
        <span>${medalhas[posicao] || posicao + 1 + "º"}</span>
        <span>${jogador.nome}</span>
        <span>${jogador.nota}/5</span>
        <span>${jogador.tempo.toFixed(2)}s</span>
      </div>
    `).join("");
  }

  carregarRanking();  // Roda ao carregar a página
</script>
```

---

## 8. CSS — `style.css`

### Paleta de Cores (Variáveis CSS)

```css
:root {
  --orange:      #E8650A;   /* Laranja principal — botões e destaques */
  --orange-deep: #C24F00;   /* Laranja escuro — hover dos botões */
  --orange-glow: #FF8533;   /* Laranja claro — texto em itálico */
  --brown:       #5C2D00;   /* Marrom terra — fundos escuros, nav do quiz */
  --cream:       #FFF8F0;   /* Creme — fundo geral do site */
  --dark:        #1A0A00;   /* Quase preto — textos principais */
  --white:       #FFFFFF;
  --gray:        #6B5C50;   /* Cinza quente — textos secundários */
  --gray-light:  #F5EDE6;   /* Cinza clarinho — fundo dos cards */
}
```

### Fontes

```css
--font-display: 'Oswald', sans-serif;      /* Títulos — bold, compacto */
--font-body:    'Source Sans 3', sans-serif; /* Texto corrido — legível */
```

### Sistema de Botões

```css
.btn           /* Base: padding, border-radius, transições */
.btn-primary   /* Laranja sólido — ação principal */
.btn-ghost     /* Transparente com borda branca — sobre fundos coloridos */
.btn-white     /* Branco sólido — sobre fundo laranja */
.btn-full      /* width: 100% — ocupa toda a largura do container */
```

### Responsividade

```css
@media (max-width: 768px) {
  /* No celular:
     - Menu de navegação some (links demais para caber)
     - Grid de 2 colunas vira 1 coluna
     - Tempo do ranking some (economiza espaço)
     - Botões ficam em coluna vertical
  */
}
```

---

## 9. JavaScript — `main.js`

Responsável pela **denúncia** na página principal.

### `enviarDenuncia()`

```javascript
async function enviarDenuncia() {
  // 1. Pega os valores dos campos
  const tipo      = document.getElementById("tipo").value;
  const local     = document.getElementById("local").value;
  const descricao = document.getElementById("descricao").value.trim();
  const btn       = document.getElementById("btn-enviar");

  // 2. Valida campos obrigatórios
  if (!tipo)      { alert("Selecione o tipo de violação."); return; }
  if (!descricao) { alert("Descreva o que você viu."); return; }

  // 3. Desabilita o botão para evitar envio duplo
  btn.disabled = true;
  btn.textContent = "Enviando...";

  // 4. Envia para o backend via fetch (requisição HTTP assíncrona)
  try {
    const res = await fetch("/api/denuncia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo, local, descricao }),
    });
    const data = await res.json();

    if (res.ok) {
      // 5. Sucesso: esconde o form e mostra a mensagem de confirmação
      document.getElementById("form-area").classList.add("hidden");
      document.getElementById("form-sucesso").classList.remove("hidden");
    } else {
      alert(data.erro || "Erro ao enviar.");
      btn.disabled = false;
      btn.textContent = "Enviar denúncia";
    }
  } catch (err) {
    // 6. Erro de rede (sem internet)
    alert("Sem conexão. Verifique sua internet.");
    btn.disabled = false;
    btn.textContent = "Enviar denúncia";
  }
}
```

### `novaDenuncia()`

```javascript
function novaDenuncia() {
  // Limpa todos os campos
  document.getElementById("tipo").value = "";
  document.getElementById("local").value = "";
  document.getElementById("descricao").value = "";

  // Esconde o sucesso e mostra o form novamente
  document.getElementById("form-area").classList.remove("hidden");
  document.getElementById("form-sucesso").classList.add("hidden");
}
```

---

## 10. JavaScript — `quiz.js`

Controla toda a lógica do quiz.

### Variáveis Globais

```javascript
let sessao     = [];   // Array com as 5 perguntas vindas da API
let atual      = 0;    // Índice da pergunta atual (0 a 4)
let respostas  = [];   // Respostas do jogador [{chave, idx, resposta}, ...]
let nomeJog    = "";   // Nome digitado pelo jogador
let inicioTime = null; // Momento em que o quiz começou (para cronômetro)
```

### `iniciarQuiz()`

```javascript
async function iniciarQuiz() {
  nomeJog = document.getElementById("nome-jogador").value.trim() || "Anônimo";
  mostrarTela("screen-quiz");   // Vai para a tela de perguntas

  const res  = await fetch("/api/quiz/iniciar");  // Pede 5 perguntas ao servidor
  sessao     = await res.json();
  atual      = 0;
  respostas  = [];
  inicioTime = performance.now();   // Inicia o cronômetro

  mostrarPergunta();
}
```

### `mostrarPergunta()`

```javascript
function mostrarPergunta() {
  const p     = sessao[atual];      // Pergunta atual
  const total = sessao.length;      // Total (sempre 5)

  // Atualiza a barra de progresso
  document.getElementById("progress-fill").style.width = `${(atual / total) * 100}%`;

  // Atualiza o badge de dificuldade
  const nivelMap = { 1: ["Fácil", "nivel-1"], 2: ["Média", "nivel-2"], 3: ["Difícil", "nivel-3"] };
  const [texto, cls] = nivelMap[p.nivel];
  const nivelEl = document.getElementById("quiz-nivel");
  nivelEl.textContent = texto;
  nivelEl.className = `quiz-nivel ${cls}`;

  // Exibe o texto da pergunta
  document.getElementById("quiz-pergunta").textContent = p.texto;

  // Gera os botões das alternativas dinamicamente
  const letras = ["A", "B", "C", "D"];
  document.getElementById("quiz-opcoes").innerHTML = p.opcoes.map((op, i) => `
    <button class="opcao-btn" onclick="responder('${letras[i]}')">
      <span class="letra">${letras[i]}</span>
      <span>${op}</span>
    </button>
  `).join("");
}
```

### `responder(letra)`

```javascript
function responder(letra) {
  const p = sessao[atual];

  // Registra a resposta
  respostas.push({ chave: p.chave, idx: p.idx, resposta: letra });

  // Desabilita todos os botões (impede clicar duas vezes)
  const btns   = document.querySelectorAll(".opcao-btn");
  const letras = ["A", "B", "C", "D"];
  btns.forEach(btn => btn.disabled = true);

  // Feedback visual: verde para correta, vermelho para a errada (se errou)
  btns.forEach((btn, i) => {
    if (letras[i] === p.resp)               btn.classList.add("opcao-correta");  // Verde
    if (letras[i] === letra && letra !== p.resp) btn.classList.add("opcao-errada");   // Vermelho
  });

  // Espera 1 segundo e vai para a próxima pergunta (ou resultado)
  setTimeout(() => {
    atual++;
    if (atual < sessao.length) {
      mostrarPergunta();
    } else {
      finalizarQuiz();
    }
  }, 1000);
}
```

### `finalizarQuiz()`

```javascript
async function finalizarQuiz() {
  const tempo = (performance.now() - inicioTime) / 1000;  // Converte ms → segundos

  const res  = await fetch("/api/quiz/resultado", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome: nomeJog, tempo, respostas }),
    // Envia as respostas para o servidor corrigir e salvar no ranking
  });
  const data = await res.json();
  mostrarResultado(data);
}
```

### `mostrarResultado(data)`

```javascript
function mostrarResultado(data) {
  mostrarTela("screen-resultado");

  // Emoji e mensagem baseados na nota
  const emojis = { 5: "🏆", 4: "🌟", 3: "👍", 2: "📚", 1: "💡", 0: "🔍" };
  const msgs   = {
    5: "Parabéns! Você é um guardião da proteção infantil!",
    4: "Muito bem! Você está bem informado.",
    // ...
  };

  document.getElementById("resultado-emoji").textContent = emojis[data.nota];
  document.getElementById("resultado-nota").textContent  = `${data.nota} / ${data.total}`;

  // Lista cada pergunta com ✅ ou ❌
  document.getElementById("resultado-detalhes").innerHTML = data.detalhes.map(d => `
    <div class="detalhe-item">
      <span>${d.acertou ? "✅" : "❌"}</span>
      <span>${d.texto}</span>
    </div>
  `).join("");
}
```

### `mostrarTela(id)`

```javascript
// Utilitário: esconde todas as telas e mostra só a solicitada
function mostrarTela(id) {
  document.querySelectorAll(".quiz-screen").forEach(el => el.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}
```

---

## 11. API — Tabela de Rotas

| Método | Rota | Body (JSON) | Resposta | Descrição |
|--------|------|-------------|----------|-----------|
| `GET` | `/` | — | HTML | Página principal |
| `GET` | `/quiz` | — | HTML | Página do quiz |
| `GET` | `/ranking` | — | HTML | Página do ranking |
| `POST` | `/api/denuncia` | `{tipo, descricao, local}` | `{mensagem}` ou `{erro}` | Salva denúncia anônima |
| `GET` | `/api/quiz/iniciar` | — | Array de 5 perguntas | Sorteia e retorna as perguntas |
| `POST` | `/api/quiz/resultado` | `{nome, tempo, respostas}` | `{nota, total, tempo, detalhes}` | Corrige e salva no ranking |
| `GET` | `/api/ranking` | — | Array de jogadores | Retorna top 20 do ranking |

### Exemplo de resposta — `/api/quiz/iniciar`

```json
[
  {
    "nivel": 1,
    "chave": "perg_facil",
    "idx": 3,
    "texto": "Qual documento garante os direitos das crianças...",
    "opcoes": ["Código Civil", "ECA", "Código Penal", "CLT"]
  },
  { ... },
  { ... },
  { ... },
  { ... }
]
```

### Exemplo de body — `/api/quiz/resultado`

```json
{
  "nome": "Maria",
  "tempo": 45.23,
  "respostas": [
    { "chave": "perg_facil", "idx": 3, "resposta": "B" },
    { "chave": "perg_media", "idx": 1, "resposta": "A" },
    ...
  ]
}
```

---

## 12. Banco de Dados

O SQLite salva tudo em um único arquivo `dados.db`. Não precisa instalar nada extra.

### Tabela `denuncias`

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER | Auto | Identificador único |
| `tipo` | TEXT | ✅ | Categoria da violação |
| `descricao` | TEXT | ✅ | Relato detalhado |
| `local` | TEXT | ❌ | Cidade/bairro (opcional) |
| `data_hora` | TIMESTAMP | Auto | Data e hora do registro |

### Tabela `ranking`

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER | Auto | Identificador único |
| `nome` | TEXT | ✅ | Nome do jogador |
| `nota` | INTEGER | ✅ | Pontuação (0 a 5) |
| `tempo` | REAL | ✅ | Tempo em segundos |
| `data_hora` | TIMESTAMP | Auto | Data e hora da partida |

---

## 13. Deploy no Render (gratuito)

### `requirements.txt`
```
flask==3.0.3
flask-cors==4.0.1
gunicorn==22.0.0
```

- `flask` → O framework web
- `flask-cors` → Permite acesso de qualquer domínio/dispositivo
- `gunicorn` → Servidor de produção (mais robusto que o servidor de desenvolvimento do Flask)

### `Procfile`
```
web: gunicorn app:app
```

Diz ao Render: "Para iniciar o site, rode o comando `gunicorn app:app`".

### `render.yaml`
```yaml
services:
  - type: web
    name: maio-laranja
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

### Passo a passo no Render

1. Crie conta em **render.com** (gratuito)
2. Vá em **New → Web Service**
3. Conecte seu GitHub e selecione o repositório com o projeto
4. O Render detecta o `render.yaml` automaticamente
5. Clique em **Create Web Service**
6. Aguarde ~2 minutos
7. Sua URL será algo como: `https://maio-laranja.onrender.com`

> ⚠️ No plano gratuito do Render, o servidor "dorme" após 15 minutos sem uso. O primeiro acesso após esse período pode demorar ~30 segundos para acordar.

---

## 14. Gerar QR Code

Após ter o site no ar, gere o QR Code gratuitamente:

1. Acesse **qr.io** ou **qrcode-monkey.com**
2. Cole a URL do seu site
3. Escolha a cor `#E8650A` (laranja da campanha) para o QR
4. Baixe em PNG ou SVG
5. Coloque em cartazes, slides e materiais impressos

---

*Documentação gerada para o projeto Maio Laranja — 18 de Maio, Dia Nacional de Combate ao Abuso e à Exploração Sexual de Crianças e Adolescentes.*
