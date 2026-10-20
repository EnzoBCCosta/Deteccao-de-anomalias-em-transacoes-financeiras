# Como a API está organizada (mesmo padrão da Aula 5):
# entities/      -> classes que mapeiam as tabelas do banco (SQLAlchemy)
# repositories/  -> acesso ao banco: Save, Update, Delete, Select (1 por entidade)
# services/      -> regras de negócio (1 por entidade + detecção de anomalias)
# controllers/   -> recebem as requisições HTTP (GET, POST, PUT, DELETE) e devolvem JSON
# routes/        -> URLs que a API responde
# config/        -> conexão com o banco e exceções da aplicação
#
# Executar localmente:  flask --app app run --host=0.0.0.0 --port=8000
# (no Docker o comando já está no Dockerfile)

from flask import Flask
from flask_restful import Api

from config.database import DATABASE_URL, PREFIXO_API
from entities.Base import db
from routes.endpoints import initialize_endpoints


# Função que cria a API
def create_app() -> Flask:
    app = Flask(__name__)
    # Definindo qual é o banco de dados
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["RESTFUL_JSON"] = {"ensure_ascii": False}  # acentos legíveis no JSON

    db.init_app(app)

    # Flask API - Controllers/Endpoints - URL
    api = Api(app, prefix=PREFIXO_API)
    initialize_endpoints(api)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
