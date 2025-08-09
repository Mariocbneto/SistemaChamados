from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Carregar senha do banco da variável de ambiente
DB_PASSWORD = os.getenv("DB_PASSWORD", "MarioNeto2005")

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="chamados",
        user="postgres",
        password=DB_PASSWORD
    )
    return conn

@app.route('/')
def home():
    return "API do sistema de chamados funcionando!"

@app.route('/chamados', methods=['POST'])
def criar_chamado():
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao')
    requerente = data.get('requerente')
    catalogo = data.get('catalogo')

    if not all([nome, descricao, requerente, catalogo]):
        return jsonify({"error": "Faltam dados obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO chamados (nome, descricao, status, data_abertura, data_ultima_atualizacao, requerente, catalogo)
            VALUES (%s, %s, %s, now(), now(), %s, %s)
        """, (nome, descricao, 'Aberto', requerente, catalogo))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Chamado criado com sucesso!"}), 201


@app.route('/chamados', methods=['GET'])
def listar_chamados():
    status = request.args.get('status')  # parâmetro opcional na URL

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if status:
        cursor.execute("SELECT * FROM chamados WHERE status = %s", (status,))
    else:
        cursor.execute("SELECT * FROM chamados")

    chamados = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(chamados)


if __name__ == '__main__':
    app.run(debug=True)
