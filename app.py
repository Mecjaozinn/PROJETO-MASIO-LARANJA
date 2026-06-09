from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import random
import os
import time

# Caminho absoluto da pasta onde está o app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
CORS(app)

DB_PATH = "dados.db"

# ───────────────────────────────────────────
# BANCO DE DADOS
# ───────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            local TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nota INTEGER NOT NULL,
            tempo REAL NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ───────────────────────────────────────────
# PERGUNTAS DO QUIZ
# ───────────────────────────────────────────
perguntas = {
    "perg_facil": [
        {"texto": "Em que data acontece o Dia Nacional de Combate ao Abuso e à Exploração Sexual de Crianças e Adolescentes?", "opcoes": ["18 de maio", "12 de outubro", "7 de setembro", "25 de dezembro"], "resp": "A"},
        {"texto": "Qual campanha brasileira promove conscientização sobre proteção infantil em maio?", "opcoes": ["Maio Azul", "Maio Verde", "Maio Laranja", "Maio Branco"], "resp": "C"},
        {"texto": "Qual é o número do Disque Direitos Humanos?", "opcoes": ["190", "100", "193", "192"], "resp": "B"},
        {"texto": "Qual documento garante os direitos das crianças e adolescentes no Brasil?", "opcoes": ["Código Civil", "ECA", "Código Penal", "CLT"], "resp": "B"},
        {"texto": "Qual órgão ajuda a proteger crianças e adolescentes em situação de risco?", "opcoes": ["Receita Federal", "Detran", "Conselho Tutelar", "Correios"], "resp": "C"},
        {"texto": "Crianças e adolescentes têm direito à educação?", "opcoes": ["Sim", "Não", "Apenas até os 10 anos", "Apenas se trabalharem"], "resp": "A"},
        {"texto": "Qual cor representa a campanha Maio Laranja?", "opcoes": ["Azul", "Verde", "Vermelho", "Laranja"], "resp": "D"},
        {"texto": "O trabalho infantil é permitido para menores de 14 anos?", "opcoes": ["Sim", "Não", "Apenas aos fins de semana", "Apenas nas férias"], "resp": "B"},
        {"texto": "Crianças devem ser protegidas contra qualquer tipo de violência?", "opcoes": ["Não", "Apenas violência física", "Sim", "Apenas violência verbal"], "resp": "C"},
        {"texto": "Denunciar uma suspeita de violência pode ajudar a proteger uma criança?", "opcoes": ["Não", "Sim", "Apenas se houver processo judicial", "Apenas se a família autorizar"], "resp": "B"},
    ],
    "perg_media": [
        {"texto": "Em qual cidade ocorreu o caso Araceli Cabrera?", "opcoes": ["Vitória", "Belo Horizonte", "Salvador", "Recife"], "resp": "A"},
        {"texto": "Em qual estado fica a cidade de Altamira?", "opcoes": ["Amazonas", "Pará", "Maranhão", "Tocantins"], "resp": "B"},
        {"texto": "A partir de qual idade uma pessoa pode trabalhar como aprendiz no Brasil?", "opcoes": ["12 anos", "13 anos", "14 anos", "16 anos"], "resp": "C"},
        {"texto": "O que significa a sigla ECA?", "opcoes": ["Estatuto da Criança e do Adolescente", "Escola da Criança Assistida", "Entidade de Controle Adolescente", "Estatuto do Cidadão Ativo"], "resp": "A"},
        {"texto": "O que é revitimização?", "opcoes": ["Receber atendimento médico", "Sofrer novos danos durante atendimentos ou investigações", "Mudar de cidade", "Encerrar um processo"], "resp": "B"},
        {"texto": "Qual é o principal objetivo do Maio Laranja?", "opcoes": ["Incentivar esportes", "Promover turismo", "Conscientizar sobre a proteção de crianças e adolescentes", "Combater o analfabetismo"], "resp": "C"},
        {"texto": "O Programa de Erradicação do Trabalho Infantil é conhecido pela sigla:", "opcoes": ["SUS", "PETI", "CRAS", "MEC"], "resp": "B"},
        {"texto": "Qual destes pode ser um sinal de alerta em uma criança?", "opcoes": ["Mudança brusca de comportamento", "Comprar material escolar", "Trocar de mochila", "Aprender um esporte novo"], "resp": "A"},
        {"texto": "A escola pode ajudar na prevenção da violência infantil?", "opcoes": ["Não", "Apenas em casos graves", "Sim", "Apenas com autorização judicial"], "resp": "C"},
        {"texto": "Quem pode denunciar suspeitas de violação dos direitos de uma criança?", "opcoes": ["Apenas policiais", "Apenas familiares", "Apenas professores", "Qualquer cidadão"], "resp": "D"},
    ],
    "perg_dificil": [
        {"texto": "Qual lei instituiu oficialmente o Dia Nacional de Combate ao Abuso e à Exploração Sexual de Crianças e Adolescentes?", "opcoes": ["Lei nº 9.970/2000", "Lei nº 8.069/1990", "Lei nº 13.431/2017", "Lei nº 10.406/2002"], "resp": "A"},
        {"texto": "O princípio da proteção integral previsto no ECA determina que:", "opcoes": ["Apenas a família é responsável pela criança", "Crianças e adolescentes têm prioridade na garantia de seus direitos", "Apenas o Estado deve protegê-los", "Seus direitos dependem da renda familiar"], "resp": "B"},
        {"texto": "A Lei nº 13.431/2017 trata principalmente de:", "opcoes": ["Trânsito escolar", "Adoção internacional", "Direitos de crianças e adolescentes vítimas ou testemunhas de violência", "Trabalho de aprendizes"], "resp": "C"},
        {"texto": "Qual é a principal função da rede de proteção à infância?", "opcoes": ["Aplicar punições", "Integrar serviços para prevenir e enfrentar violações de direitos", "Substituir a família", "Administrar escolas"], "resp": "B"},
        {"texto": "Qual atitude é mais adequada ao suspeitar que uma criança esteja sofrendo violência?", "opcoes": ["Ignorar a situação", "Espalhar informações em redes sociais", "Aguardar outra pessoa agir", "Acolher e denunciar pelos canais oficiais"], "resp": "D"},
    ],
}

# ───────────────────────────────────────────
# ROTAS FRONTEND
# ───────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/ranking")
def ranking_page():
    return render_template("ranking.html")

# ───────────────────────────────────────────
# API — DENÚNCIA
# ───────────────────────────────────────────
@app.route("/api/denuncia", methods=["POST"])
def receber_denuncia():
    data = request.get_json()
    tipo = data.get("tipo", "").strip()
    descricao = data.get("descricao", "").strip()
    local = data.get("local", "").strip()

    if not tipo or not descricao:
        return jsonify({"erro": "Preencha os campos obrigatórios."}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO denuncias (tipo, descricao, local) VALUES (?, ?, ?)", (tipo, descricao, local))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Denúncia registrada com sucesso. Obrigado por agir!"}), 201

# ───────────────────────────────────────────
# API — QUIZ: gerar sessão de perguntas
# ───────────────────────────────────────────
@app.route("/api/quiz/iniciar", methods=["GET"])
def iniciar_quiz():
    niveis = [1, 1, 2, 2, 3]  # 2 fáceis, 2 médias, 1 difícil
    random.shuffle(niveis)

    sessao = []
    idx_f = random.sample(range(len(perguntas["perg_facil"])), 2)
    idx_m = random.sample(range(len(perguntas["perg_media"])), 2)
    idx_d = random.sample(range(len(perguntas["perg_dificil"])), 1)

    pool = {1: iter(idx_f), 2: iter(idx_m), 3: iter(idx_d)}

    for nivel in niveis:
        chave = ["perg_facil", "perg_media", "perg_dificil"][nivel - 1]
        idx = next(pool[nivel])
        p = perguntas[chave][idx]
        sessao.append({
            "nivel": nivel,
            "chave": chave,
            "idx": idx,
            "texto": p["texto"],
            "opcoes": p["opcoes"],
        })

    return jsonify(sessao)

# ───────────────────────────────────────────
# API — QUIZ: corrigir e salvar resultado
# ───────────────────────────────────────────
@app.route("/api/quiz/resultado", methods=["POST"])
def resultado_quiz():
    data = request.get_json()
    nome = data.get("nome", "Anônimo").strip() or "Anônimo"
    tempo = float(data.get("tempo", 0))
    respostas = data.get("respostas", [])

    nota = 0
    detalhes = []
    for r in respostas:
        chave = r["chave"]
        idx = r["idx"]
        resp_user = r["resposta"].upper()
        correta = perguntas[chave][idx]["resp"]
        acertou = resp_user == correta
        if acertou:
            nota += 1
        detalhes.append({
            "texto": perguntas[chave][idx]["texto"],
            "resposta_usuario": resp_user,
            "resposta_correta": correta,
            "acertou": acertou,
        })

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO ranking (nome, nota, tempo) VALUES (?, ?, ?)", (nome, nota, tempo))
    conn.commit()
    conn.close()

    return jsonify({"nota": nota, "total": len(respostas), "tempo": round(tempo, 2), "detalhes": detalhes})

# ───────────────────────────────────────────
# API — RANKING
# ───────────────────────────────────────────
@app.route("/api/ranking", methods=["GET"])
def get_ranking():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT nome, nota, tempo FROM ranking ORDER BY nota DESC, tempo ASC LIMIT 20")
    rows = cur.fetchall()
    conn.close()
    resultado = [{"nome": r[0], "nota": r[1], "tempo": r[2]} for r in rows]
    return jsonify(resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
