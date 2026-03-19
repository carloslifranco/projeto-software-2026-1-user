from flask import Flask, request, jsonify
from db import db
from models import User
import os 
import redis 
import json

postgres_user = os.environ.get('POSTGRES_USER', 'appuser')
postgres_password = os.environ.get('POSTGRES_PASSWORD', 'apppass')
postgres_url = os.environ.get('POSTGRES_URL', 'localhost')

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#conectando com o redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

db.init_app(app)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    user = User(
        name=data["name"],
        email=data["email"]
    )

    db.session.add(user)
    db.session.commit()

    mensagem_payload = {
        "type": "USER_CREATED",
        "source": "users-api",
        "description": user.name
    }

    redis_client.publish("fila_usuarios", json.dumps(mensagem_payload))

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email
    }), 201

@app.route("/users/<uuid:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email
    }), 201

@app.route("/users/<uuid:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    mensagem_payload = {
        "type": "USER_DELETED",
        "source": "users-api",
        "description": user.name
    }

    redis_client.publish("fila_usuarios", json.dumps(mensagem_payload))

    return "", 204

@app.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()

    return [
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }
        for user in users
    ], 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
