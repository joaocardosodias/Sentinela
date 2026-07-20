import os
from flask import Flask, abort, send_from_directory
from app.config import Config
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.db import init_pool, release_connection

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    database_url = app.config.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurado. Crie um arquivo .env na raiz do "
            "repositório a partir de .env.example e preencha a conexão real "
            "do PostgreSQL/Supabase antes de iniciar o backend."
        )

    # Inicializa o pool de conexões com o banco (mínimo 2, máximo 10 conexões simultâneas)
    init_pool(database_url)

    # Registra a devolução automática da conexão ao pool ao final de cada requisição
    app.teardown_appcontext(release_connection)

    # Inicializa a extensão de JWT no nosso App
    jwt = JWTManager(app)

    # Configuração do template do Swagger (para suportar o botão de JWT "Authorize")
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Documentação da API - Projeto g03",
            "description": "Documentação automática das rotas do sistema com arquitetura DDD e SQL Puro.",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Insira o token JWT no formato: Bearer {seu_token}"
            }
        }
    }
    # Inicializa o Swagger na aplicação
    swagger = Swagger(app, template=swagger_template)

    # Registra as rotas (blueprints)
    from app.routes.auth_route import auth_bp
    from app.routes.user_route import users_bp
    from app.routes.veiculo_route import veiculos_bp
    from app.routes.operacao_route import operacoes_bp
    from app.routes.drone_route import drones_bp
    from app.routes.scan_route import scans_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(veiculos_bp)
    app.register_blueprint(operacoes_bp)
    app.register_blueprint(drones_bp)
    app.register_blueprint(scans_bp)

    @app.route('/uploaded_frames/<path:filename>')
    def serve_uploaded_frame(filename):
        directory = app.config['UPLOADED_FRAMES_DIR']
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            abort(404)
        return send_from_directory(directory, filename)

    return app
