def test_get_user_404(client):

    # Teste de Recuperação
    get_response = client.get(f"/users/1")
    assert get_response.status_code == 404 

def test_create_and_get_user_and_delete_user(client):

    #criando o usuário
    payload = {
        "name": "Carlos",
        "email": "carlos@gmail.com"
    }

    response = client.post("/users", json=payload)
    assert response.status_code == 201
    user_id = response.json["id"]

    #pegando o usuário criado
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200

    #deletando o usuário criado     
    del_response = client.delete(f"/users/{user_id}")
    assert del_response.status_code == 204
    

def test_create_and_delete_user(client):
    payload = {
        "name": "Felipe",
        "email": "felipe@gmail.com"
        }
    
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    user_id = response.json["id"]

    #deletando o usuário 
    del_response = client.delete(f"/users/{user_id}")
    assert del_response.status_code == 204

    

def test_create_two_users_and_list_and_delete_both_users(client):
    payload1 = {
        "name": "Carlos",
        "email": "carlos@gamil.com"
    }

    payload2 = {
        "name": "Felipe",
        "email": "felipe@gmail.com"
    }

    response1 = client.post("/users", json=payload1)
    assert response1.status_code == 201

    response2 = client.post("/users", json=payload2)
    assert response2.status_code == 201

    #listando os usuários criados
    list_response = client.get("/users")
    assert list_response.status_code == 200
    assert len(list_response.json) == 2

    #deletando os dois usuários
    user_id1 = response1.json["id"]
    user_id2 = response2.json["id"] 

    del_response1 = client.delete(f"/users/{user_id1}")
    assert del_response1.status_code == 204

    del_response2 = client.delete(f"/users/{user_id2}")
    assert del_response2.status_code == 204