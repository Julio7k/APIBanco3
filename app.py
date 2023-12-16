from flask import Flask, jsonify
from decouple import config 
import psycopg2
from pymongo import MongoClient
from bson import ObjectId
import redis
import json

app = Flask(__name__)

# Leitura de variáveis de ambiente
POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_DB = config('POSTGRES_DB')
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')

# Conexão com o PostgreSQL
pg_conn = psycopg2.connect(
    host=POSTGRES_HOST,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)
pg_cursor = pg_conn.cursor()

# Conexão com o MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['base_2']
mongo_collection = mongo_db['clientes']

# Conexão com o Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

@app.route('/', methods=['GET'])
def index():
    return "Página inicial"


@app.route('/clientes', methods=['GET'])
def get_clientes():
    # Consulta no banco PostgreSQL
    pg_cursor.execute("SELECT * FROM Cliente;")
    clientes_pg = pg_cursor.fetchall()

    # Consulta no banco MongoDB
    clientes_mongo = mongo_collection.find()

    # Combina os resultados
    result = {
        'clientes_postgres': [dict(zip(['id', 'cpf', 'nome', 'endereco', 'cidade', 'uf', 'email'], cliente)) for cliente in clientes_pg],
        'clientes_mongo': [dict(nome) if not isinstance(nome['_id'], ObjectId) else {**nome, '_id': str(nome['_id'])} for nome in clientes_mongo]
    }

    # Armazena os resultados no Redis
    redis_key = 'chave_cache'
    redis_client.set(redis_key, json.dumps(result))

    return jsonify(result)

@app.route('/clientes_cache', methods=['GET'])
def get_clientes_cache():
    # Recupera os resultados do Redis
    redis_key = 'chave_cache'
    cached_result = redis_client.get(redis_key)

    if cached_result:
        return jsonify(json.loads(cached_result))
    else:
        return jsonify({"message": "Nenhum dado na cache"})

if __name__ == '__main__':
    app.run(debug=True)