from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)
import random
from flask_mail import Mail, Message

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from banco.banco import (
    conectar,
    criar_tabelas
)

import os

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "smartfinance_dev"
)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = os.getenv(
    "EMAIL_USER"
)

app.config["MAIL_PASSWORD"] = os.getenv(
    "EMAIL_PASSWORD"
)

app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "EMAIL_USER"
)

mail = Mail(app)

# Cria as tabelas ao iniciar
criar_tabelas()


# ==========================
# HOME
# ==========================

@app.route("/")
def home():

    if session.get("usuario_id"):
        return redirect("/dashboard")

    return render_template("login.html")


# ==========================
# CADASTRO
# ==========================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]

        usuario = request.form["usuario"]

        email = request.form["email"]

        senha = request.form["senha"]

        confirmar = request.form["confirmar"]

        if senha != confirmar:

            flash("As senhas não coincidem.")

            return redirect("/cadastro")

        conn = conectar()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario=%s
            """,
            (usuario,)
        )

        existe = cur.fetchone()

        if existe:

            conn.close()

            flash("Usuário já existe.")

            return redirect("/cadastro")

        senha_hash = generate_password_hash(
            senha
        )

        cur.execute(
            """
            INSERT INTO usuarios
            (
                nome,
                usuario,
                email,
                senha
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                nome,
                usuario,
                email,
                senha_hash
            )
        )

        conn.commit()

        conn.close()

        flash("Cadastro realizado!")

        return redirect("/")

    return render_template(
        "cadastro.html"
    )


# ==========================
# LOGIN
# ==========================

@app.route("/entrar", methods=["POST"])
def entrar():

    usuario = request.form["usuario"]

    senha = request.form["senha"]

    conn = conectar()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            nome,
            senha
        FROM usuarios
        WHERE usuario=%s
        """,
        (usuario,)
    )

    usuario_banco = cur.fetchone()

    conn.close()

    if usuario_banco:

        if check_password_hash(
            usuario_banco[2],
            senha
        ):

            session["usuario_id"] = usuario_banco[0]

            session["nome"] = usuario_banco[1]

            return redirect("/dashboard")

    flash("Usuário ou senha inválidos.")

    return redirect("/")

# ==========================
# RECUPERAR SENHA
# ==========================

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":

        usuario = request.form["usuario"]

        conn = conectar()

        cur = conn.cursor()

        # Procura o usuário no banco
        cur.execute("""
            SELECT id, email
            FROM usuarios
            WHERE usuario = %s
        """, (usuario,))

        usuario_banco = cur.fetchone()

        if usuario_banco:

            codigo = str(random.randint(100000, 999999))

            session["codigo"] = codigo

            session["usuario_recuperacao"] = usuario_banco[0]

            print("Código:", codigo)

            conn.close()

            return redirect("/nova_senha")

        conn.close()

    return render_template("recuperar_senha.html")

# ==========================
# NOVA SENHA
# ==========================

@app.route("/nova_senha", methods=["GET", "POST"])
def nova_senha():

    if request.method == "POST":

        codigo = request.form["codigo"]

        senha = request.form["senha"]

        confirmar = request.form["confirmar"]

        if senha != confirmar:

            return redirect(
                "/nova_senha"
            )

        if codigo == session.get("codigo"):

            senha_hash = generate_password_hash(
                senha
            )

            conn = conectar()

            cur = conn.cursor()

            cur.execute("""
            UPDATE usuarios
            SET senha=%s
            WHERE id=%s
            """,
            (
                senha_hash,
                session["usuario_recuperacao"]
            ))

            conn.commit()

            conn.close()

            session.pop(
                "codigo",
                None
            )

            session.pop(
                "usuario_recuperacao",
                None
            )

            return redirect("/")

    return render_template(
        "nova_senha.html"
    )

# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if not session.get(
        "usuario_id"
    ):

        return redirect("/")

    return render_template(
        "dashboard.html",
        nome=session["nome"]
    )


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================
# EXECUTAR
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )