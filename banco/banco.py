import os
import psycopg2

import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():

    if not DATABASE_URL:
        raise Exception(
            "DATABASE_URL não configurada."
        )

    return psycopg2.connect(
        DATABASE_URL
    )


def criar_tabelas():

    conn = conectar()

    cur = conn.cursor()

    # =====================
    # USUÁRIOS
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (

        id SERIAL PRIMARY KEY,

        nome VARCHAR(100) NOT NULL,

        usuario VARCHAR(50) UNIQUE NOT NULL,

        email VARCHAR(150) UNIQUE NOT NULL,

        senha VARCHAR(255) NOT NULL,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """)

    # =====================
    # CATEGORIAS
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS categorias (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        nome VARCHAR(100) NOT NULL,

        tipo VARCHAR(20),

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # SALÁRIOS
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS salarios (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        salario_bruto NUMERIC(10,2),

        salario_liquido NUMERIC(10,2),

        data_inicio DATE,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # VALE REFEIÇÃO
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vale_refeicao (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        valor_recebido NUMERIC(10,2),

        saldo_atual NUMERIC(10,2),

        data_recebimento DATE,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # GASTOS ALIMENTAÇÃO
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS gastos_refeicao (

        id SERIAL PRIMARY KEY,

        vale_id INTEGER NOT NULL,

        descricao VARCHAR(255),

        valor NUMERIC(10,2),

        data_gasto DATE,

        FOREIGN KEY(vale_id)
        REFERENCES vale_refeicao(id)

    );
    """)

    # =====================
    # VALE TRANSPORTE
    # =====================    

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vale_transporte (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        valor_recebido NUMERIC(10,2),

        saldo_atual NUMERIC(10,2),

        data_recebimento DATE,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # GASTOS TRANSPORTE
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS gastos_transporte (

        id SERIAL PRIMARY KEY,

        transporte_id INTEGER NOT NULL,

        descricao VARCHAR(255),

        valor NUMERIC(10,2),

        data_gasto DATE,

        FOREIGN KEY(transporte_id)
        REFERENCES vale_transporte(id)

    );
    """)

    # =====================
    # TRANSAÇÕES
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        categoria_id INTEGER,

        descricao VARCHAR(255),

        valor NUMERIC(10,2),

        tipo VARCHAR(20),

        data_transacao DATE,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id),

        FOREIGN KEY(categoria_id)
        REFERENCES categorias(id)

    );
    """)

    # =====================
    # CONTAS FIXAS
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contas_fixas (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        descricao VARCHAR(255),

        valor NUMERIC(10,2),

        vencimento INTEGER,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # CARTÕES
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cartoes (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        nome VARCHAR(100),

        limite NUMERIC(10,2),

        fechamento INTEGER,

        vencimento INTEGER,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # METAS
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS metas (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        descricao VARCHAR(255),

        valor_meta NUMERIC(10,2),

        valor_guardado NUMERIC(10,2),

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # RECUPERAÇÃO SENHA
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS recuperacao_senha (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        codigo VARCHAR(10),

        expira_em TIMESTAMP,

        utilizado BOOLEAN DEFAULT FALSE,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # PREVISÕES
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS previsoes (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        tipo VARCHAR(50),

        valor_medio NUMERIC(10,2),

        dias_estimados INTEGER,
        
        observacao TEXT,

        data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)

    # =====================
    # NOTIFICAÇÕES
    # =====================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notificacoes (

        id SERIAL PRIMARY KEY,

        usuario_id INTEGER NOT NULL,

        titulo VARCHAR(255),

        mensagem TEXT,

        lida BOOLEAN DEFAULT FALSE,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)

    );
    """)    

    conn.commit()

    cur.close()

    conn.close()