from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for
)

from io import BytesIO

from reportlab.pdfgen import canvas

from flask import send_file

from flask import Response, render_template
import json
import os
import sqlite3

from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)

BANCO ="financeiro.db"

app.secret_key = "7fK9xM2vL4qP8rN1bC6dZ3tW5yH8uJ"

PASTA_DADOS = "dados"

os.makedirs(PASTA_DADOS, exist_ok=True)

def criar_banco():

    conn = sqlite3.connect(BANCO)

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
    
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    conn.close()

criar_banco()

def criar_admin():
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario=?",
        ("admin",)
    )

    existe = cursor.fetchone()

    if not existe:

        senha_hash = generate_password_hash("123456")

        cursor.execute("""
            INSERT INTO usuarios (nome, usuario, senha)
            VALUES (?, ?, ?)
        """, (
            "Administrador",
            "admin",
            senha_hash
        ))

        conn.commit()

    conn.close()

criar_admin()


def arquivo_mes():

    usuario_id = session.get(
        "usuario_id",
        "anonimo"
    )

    nome_mes = datetime.now().strftime("%Y-%m")

    pasta_usuario = os.path.join(
        PASTA_DADOS,
        str(usuario_id)
    )

    os.makedirs(
        pasta_usuario,
        exist_ok=True
    )

    return os.path.join(
        pasta_usuario,
        f"{nome_mes}.json"
    )


def criar_json():


    arquivo = arquivo_mes()

    if not os.path.exists(arquivo):

        dados = {

            "salario": 0,

            "meta_reserva": 0,

            "valor_guardado": 0,

            "contas_fixas": [],

            "transacoes": []

        }

        with open(
            arquivo,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                dados,
                f,
                indent=4,
                ensure_ascii=False
            )


def carregar_dados():

    criar_json()

    with open(
        arquivo_mes(),
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def salvar_dados(dados):

    with open(
        arquivo_mes(),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )


def calcular_previsao():

    usuario_id = session.get(
        "usuario_id"
    )

    pasta_usuario = os.path.join(
        PASTA_DADOS,
        str(usuario_id)
    )

    gastos = []

    if not os.path.exists(
        pasta_usuario
    ):
        return 0

    for arquivo in os.listdir(
        pasta_usuario
    ):

        if arquivo.endswith(".json"):

            caminho = os.path.join(
                pasta_usuario,
                arquivo
            )

            with open(
                caminho,
                "r",
                encoding="utf-8"
            ) as f:

                dados = json.load(f)

                total = sum(
                    t["valor"]
                    for t in dados["transacoes"]
                )

                gastos.append(total)

    if len(gastos) == 0:
        return 0

    return round(
        sum(gastos) / len(gastos),
        2
    )


@app.route("/dados_dashboard.js")
def dados_dashboard_js():

    dados = carregar_dados()

    categorias = {}
    
    for item in dados["transacoes"]:
        categoria = item["categoria"]

        categorias[categoria] = (
            categorias.get(categoria, 0)
            + item["valor"]
        )

    meses = []
    gastos_mensais = []

    return Response(

        render_template(
            "dados_dashboard.js",
            categorias=categorias,
            meses=meses,
            gastos_mensais=gastos_mensais
        ),

        mimetype="application/javascript"
    )

@app.route("/")
def login():

    return render_template(
        "login.html"
    )


@app.route("/entrar", methods=["POST"])
def entrar():

    usuario = request.form["usuario"]

    senha = request.form["senha"]

    conn = sqlite3.connect(BANCO)

    cursor = conn.cursor()

    cursor.execute("""
                SELECT id, nome, senhaFROM usuarios
                WHERE usuario = ?
                """,
                (usuario,))

    usuario_encontrado = cursor.fetchone()

    if usuario_encontrado:
        senha_banco = usuario_encontrado[2]

    if check_password_hash(
        senha_banco,
        senha
    ):

        session["logado"] = True

        session["usuario_id"] = usuario_encontrado[0]

        session["nome"] = usuario_encontrado[1]

        return redirect("/dashboard")

    conn.close()

    if usuario_encontrado:

        session["logado"] = True

        session["usuario_id"] = usuario_encontrado[0]

        session["nome"] = usuario_encontrado[1]

        return redirect("/dashboard")

    return redirect("/")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")




@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome=request.form["nome"]
    usuario=request.form["usuario"]
    senha=request.form["senha"]
    senha_hash = generate_password_hash(
    senha
    )
    conn=sqlite3.connect(BANCO)
    cur=conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nome,usuario,senha) VALUES (?,?,?)",
            (nome,usuario,senha_hash)
            )
        conn.commit()
    except Exception as e:
        print(e)
    conn.close()
    return redirect("/")

@app.route("/dashboard")
def dashboard():

    if not session.get("logado"):

        return redirect("/")

    dados = carregar_dados()

    total_gastos = sum(
        item["valor"]
        for item in dados["transacoes"]
    )

    total_contas_fixas = sum(
        item["valor"]
        for item in dados["contas_fixas"]
    )

    saldo = (
        dados["salario"]
        - total_gastos
        - total_contas_fixas
    )

    previsao = calcular_previsao()

    return render_template(

        "dashboard.html",

        salario=dados["salario"],

        total_gastos=round(
            total_gastos,
            2
        ),

        total_contas_fixas=round(
            total_contas_fixas,
            2
        ),

        saldo=round(
            saldo,
            2
        ),

        previsao=previsao,

        valor_guardado=dados[
            "valor_guardado"
        ],

        transacoes=dados[
            "transacoes"
        ]
    )
     
    categorias = {}

    for item in dados["transacoes"]:
        categoria = item["categoria"]
        
        categorias[categoria] = (
        categorias.get(categoria, 0)
        + item["valor"]
    )
        meses = []
        gastos_mensais = []
        for arquivo in sorted(os.listdir(PASTA_DADOS)):
            if arquivo.endswith(".json"):
                caminho = os.path.join(
                    PASTA_DADOS,
                    arquivo
                    )
                with open(
                    caminho,
                    "r",
                    encoding="utf-8"
                    ) as f:
                    
                    d = json.load(f)
                    
                    total = sum(
                        t["valor"]
                        for t in d["transacoes"]
                        )
                    meses.append(
                        arquivo.replace(".json", "")
                        )
                    gastos_mensais.append(total)


@app.route("/contas_fixas")
def contas_fixas():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    return render_template(
        "contas_fixas.html",
        contas_fixas=dados["contas_fixas"]
    )


@app.route(
    "/salvar_salario",
    methods=["POST"]
)
def salvar_salario():

    dados = carregar_dados()

    dados["salario"] = float(
        request.form["salario"]
    )

    salvar_dados(dados)

    return redirect(
        "/dashboard"
    )


@app.route(
    "/novo_gasto",
    methods=["POST"]
)
def novo_gasto():

    dados = carregar_dados()

    dados["transacoes"].append({

        "data":
        request.form["data"],

        "categoria":
        request.form["categoria"],

        "valor":
        float(
            request.form["valor"]
        )

    })

    salvar_dados(dados)

    return redirect(
        "/dashboard"
    )


@app.route("/conta_fixa", methods=["POST"])
def conta_fixa():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    nome = request.form["nome"].strip()

    valor = float(
        request.form["valor"]
    )

    dados["contas_fixas"].append({

        "id": len(
            dados["contas_fixas"]
        ) + 1,

        "nome": nome,

        "valor": valor

    })

    salvar_dados(dados)

    return redirect(
        "/contas_fixas"
    )

@app.route(
    "/salvar_meta",
    methods=["POST"]
)
def salvar_meta():

    dados = carregar_dados()

    dados["meta_reserva"] = float(
        request.form["meta"]
    )

    dados["valor_guardado"] = float(
        request.form["guardado"]
    )

    salvar_dados(dados)

    return redirect(
        "/dashboard"
    )


@app.route("/previsao")
def previsao():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    previsao_valor = calcular_previsao()

    sobra_prevista = (
        dados["salario"]
        - previsao_valor
    )

    return render_template(

        "previsao.html",

        previsao=previsao_valor,

        salario=dados["salario"],

        sobra_prevista=round(
            sobra_prevista,
            2
        )

    )


@app.route("/relatorio")
def relatorio():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    gastos = sum(
        item["valor"]
        for item in dados["transacoes"]
    )

    contas = sum(
        item["valor"]
        for item in dados["contas_fixas"]
    )

    saldo = (
        dados["salario"]
        - gastos
        - contas
    )

    return render_template(

        "relatorio.html",

        salario=dados["salario"],

        gastos=round(gastos, 2),

        contas=round(contas, 2),

        saldo=round(saldo, 2)

    )

@app.route("/gerar_pdf")
def gerar_pdf():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    gastos = sum(
        item["valor"]
        for item in dados["transacoes"]
    )

    contas = sum(
        item["valor"]
        for item in dados["contas_fixas"]
    )

    saldo = (
        dados["salario"]
        - gastos
        - contas
    )

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.drawString(
        100,
        800,
        "Relatório Financeiro"
    )

    pdf.drawString(
        100,
        760,
        f"Salário: R$ {dados['salario']:.2f}"
    )

    pdf.drawString(
        100,
        740,
        f"Gastos: R$ {gastos:.2f}"
    )

    pdf.drawString(
        100,
        720,
        f"Contas Fixas: R$ {contas:.2f}"
    )

    pdf.drawString(
        100,
        700,
        f"Saldo: R$ {saldo:.2f}"
    )

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio_financeiro.pdf",
        mimetype="application/pdf"
    )

@app.route("/metas")
def metas():

    if not session.get("logado"):
        return redirect("/")

    dados = carregar_dados()

    meta = dados["meta_reserva"]

    guardado = dados["valor_guardado"]

    percentual = 0

    if meta > 0:

        percentual = round(
            (guardado / meta) * 100,
            1
        )

    falta = round(
        meta - guardado,
        2
    )

    return render_template(

        "metas.html",

        meta=meta,

        guardado=guardado,

        percentual=percentual,

        falta=falta

    )

if __name__ == "__main__":

    app.run(
        debug=True
    )