from flask import Flask, jsonify, request
import psycopg2
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)


# Conexão com o banco PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="AtividadeA3",
    user="postgres",
    password="rosa3011"
)
pg_cursor = pg_conn.cursor()

# Conexão com o banco MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['base_2']
mongo_collection = mongo_db['clientes']

@app.route('/clientes', methods=['GET'])
def get_clientes():
    # Consulta no banco PostgreSQL
    pg_cursor.execute("SELECT * FROM Cliente;")
    clientes_pg = pg_cursor.fetchall()

    #Aonde consulta no banco MongoDB
    clientes_mongo = mongo_collection.find()

        # Convertendo ObjectId para strings
    clientes_mongo_serializable = [
        {**dict(cliente), '_id': str(cliente['_id'])} for cliente in clientes_mongo
    ]

    # Combina os resultados
    result = {
        'clientes_postgres': [dict(zip(['id', 'cpf', 'nome', 'endereco', 'cidade', 'uf', 'email'], cliente)) for cliente in clientes_pg],
        'clientes_mongo': clientes_mongo_serializable
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)