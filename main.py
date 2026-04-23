from flask import Flask, request, jsonify
from db import db
from models import User
import os
import jwt
from functools import wraps

def create_app():
    app = Flask(__name__)
    
    postgres_user = os.environ.get('POSTGRES_USER', 'appuser')
    postgres_password = os.environ.get('POSTGRES_PASSWORD', 'apppass')
    postgres_url = os.environ.get('POSTGRES_URL', 'localhost')
    
    # Define o padrão, mas permite que o Pytest sobrescreva depois
    db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", db_uri)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)

    #fazendo o decorator para a autenticação do token
    def validate_token(f):
        @wraps(f)

        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization") #aqui ele esperar bearer token, então o token deve ser enviado no formato "Bearer <token>"

            if not token:
                return jsonify({"message": "Token ausente!"}), 401

            try:
                token_puro = token.replace("Bearer ", "")
                data = jwt.decode(token_puro, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id_atual = data["user_id"]
                
            except Exception as e:
                return jsonify({"message": "Token inválido ou expirado!"}), 401

            return f(user_id_atual, *args, **kwargs)
        
        return decorated
    
    @app.route("/login", methods=["POST"])
    def login():
        data = request.json
        email = data.get("email")

        user = User.query.filter_by(email=email).first()

        if user:

            payload = {
                "user_id": str(user.id),
                "exp": jwt.datetime.datetime.utcnow() + jwt.timedelta(hours=1) #token expira em 1 hora
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({"token": token}), 200
        
        return jsonify({"message": "Credenciais inválidas"}), 401


    @app.route("/users", methods=["POST"])
    @validate_token
    def create_user(user_id_atual):
        usuario_operador = User.query.get(user_id_atual)

        if usuario_operador != 'admin':
            return jsonify({"message": "Acesso negado: apenas administradores podem criar usuários."}), 403
        
        data = request.json

        user = User(
            name=data["name"],
            email=data["email"]
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "criado_por": user_id_atual
        }), 201

    @app.route("/users/<uuid:user_id>", methods=["GET"])
    @validate_token
    def get_user(user_id_atual, user_id):

        if str(user_id_atual) != str(user_id):
            return jsonify({"message": "Acesso negado: você só pode acessar seus próprios dados."}), 403

        user = User.query.get_or_404(user_id)

        return jsonify({
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }), 200

    @app.route("/users/<uuid:user_id>", methods=["DELETE"])
    @validate_token
    def delete_user(user_id_atual, user_id):

        if str(user_id_atual) != str(user_id):
            return jsonify({"message": "Acesso negado: você não tem acesso para deletar este usuário."}), 403

        user = User.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return "", 204

    @app.route("/users", methods=["GET"])
    def list_users(user_id_atual):

        if str(user_id_atual) != 'admin':
            return jsonify({"message": "Acesso negado: apenas administradores podem listar usuários."}), 403

        users = User.query.all()

        return [
            {
                "id": str(user.id),
                "name": user.name,
                "email": user.email
            }
            for user in users
        ], 200

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
