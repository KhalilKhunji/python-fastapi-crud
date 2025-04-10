# tests/test_teas.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.user import UserModel
from models.tea import TeaModel
from tests.lib import login
from main import app

def test_get_teas(test_app: TestClient, override_get_db):
    response = test_app.get("/api/teas")
    assert response.status_code == 200
    teas = response.json()
    assert isinstance(teas, list)
    assert len(teas) >= 2  # Ensure there are at least two teas in the test database
    for tea in teas:
        assert 'id' in tea
        assert 'name' in tea
        assert 'in_stock' in tea
        assert 'rating' in tea
        assert 'user' in tea
        assert 'email' in tea['user']
        assert 'username' in tea['user']

def test_get_single_tea(test_app: TestClient, test_db: Session, override_get_db):
    tea = test_db.query(TeaModel).first()
    assert tea is not None
    response = test_app.get(f"/api/teas/{tea.id}")
    assert response.status_code == 200
    tea = response.json()
    assert isinstance(tea, dict)
    assert 'id' in tea
    assert 'name' in tea
    assert 'in_stock' in tea
    assert 'rating' in tea
    assert 'user' in tea
    assert 'email' in tea['user']
    assert 'username' in tea['user']
    assert 'comments' in tea
    for comment in tea['comments']:
        assert 'content' in comment
        assert 'id' in comment

def test_get_tea_not_found(test_app: TestClient, test_db: Session, override_get_db):
    max_tea_id = test_db.query(TeaModel.id).order_by(TeaModel.id.desc()).first()
    if max_tea_id is None:
        invalid_tea_id = 1
    else:
        invalid_tea_id = max_tea_id[0] + 1

    response = test_app.get(f"/api/teas/{invalid_tea_id}")
    assert response.status_code == 404
    response_data = response.json()
    assert response_data['detail'] == 'Tea not found'


def test_create_tea(test_app: TestClient, test_db: Session):

    # Create a new mock user in the test database
    user = UserModel(username='testUser123', email='hello@example.com')
    user.set_password('mys3cretp2ssw0rd')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Use the login helper to generate authentication headers for the new mock user
    headers = login(test_app, 'testUser123', 'mys3cretp2ssw0rd')

    # Data for creating a new tea
    tea_data = {
        "name": "Test Tea",
        "in_stock": True,
        "rating": 4
    }

    # Send a POST request to create a new tea
    response = test_app.post("/api/teas", headers=headers, json=tea_data)

    # Verify that the response is successful
    assert response.status_code == 200
    assert response.json()["name"] == tea_data["name"]
    assert response.json()["in_stock"] == tea_data["in_stock"]
    assert response.json()["rating"] == tea_data["rating"]
    assert "id" in response.json()  # Ensure an ID is returned
    assert "user" in response.json()  # Ensure user data is included
    assert response.json()['user']["username"] == 'testUser123'

    # Verify the tea was created in the database
    tea_id = response.json()["id"]
    tea = test_db.query(TeaModel).filter(TeaModel.id == tea_id).first()
    assert tea is not None
    assert tea.name == tea_data["name"]
    assert tea.in_stock == tea_data["in_stock"]
    assert tea.rating == tea_data["rating"]

def test_update_tea(test_app: TestClient, test_db: Session, override_get_db):
    user = UserModel(username='anotherTestUser321', email='goodbye@example.com')
    user.set_password('passw0rd')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    headers = login(test_app, 'anotherTestUser321', 'passw0rd')

    tea = TeaModel(name="Another Test Tea", in_stock=True, rating=65, user_id=user.id)
    test_db.add(tea)
    test_db.commit()

    updated_data = {
        "name": "Another Updated Tea Name",
        "in_stock": not tea.in_stock,
        "rating": 55
    }

    response = test_app.put(f"/api/teas/{tea.id}", headers=headers, json=updated_data)
    assert response.status_code == 200
    updated_tea = response.json()
    assert updated_tea['id'] == tea.id
    assert updated_tea['name'] == updated_data['name']
    assert updated_tea['in_stock'] == updated_data['in_stock']
    assert updated_tea['rating'] == updated_data['rating']

def test_update_tea_not_found(test_app: TestClient, test_db: Session, override_get_db):
    user = UserModel(username='someguy', email='someperson@example.com')
    user.set_password('bestpassword')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    headers = login(test_app, 'someguy', 'bestpassword')
    max_tea_id = test_db.query(TeaModel.id).order_by(TeaModel.id.desc()).first()
    if max_tea_id is None:
        invalid_tea_id = 1
    else:
        invalid_tea_id = max_tea_id[0] + 1

    updated_data = {
        "name": "Updated Tea Name",
        "in_stock": True,
        "rating": 90
    }

    response = test_app.put(f"/api/teas/{invalid_tea_id}", headers=headers, json=updated_data)
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Tea not found"


def test_unauthorized_update_tea(test_app: TestClient, test_db: Session, override_get_db):
    user1 = UserModel(username='user1', email='user1@example.com')
    user1.set_password('password1')
    test_db.add(user1)
    test_db.commit()

    user2 = UserModel(username='user2', email='user2@example.com')
    user2.set_password('password2')
    test_db.add(user2)
    test_db.commit()

    # Create a tea belonging to user1
    tea = TeaModel(name="Chamomile (Yum)", in_stock=True, rating=100, user_id=user1.id)
    test_db.add(tea)
    test_db.commit()

    # Log in as user2 (who does not own the tea)
    headers = login(test_app, 'user2', 'password2')

    updated_data = {
        "name": "Chamomile (Yuck)",
        "in_stock": False,
        "rating": 0
    }

    # Attempt to update tea that belongs to user1, while logged in as user2
    response = test_app.put(f"/api/teas/{tea.id}", headers=headers, json=updated_data)
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Operation forbidden"

def test_delete_tea(test_app: TestClient, test_db: Session, override_get_db):
    user = UserModel(username='deleter', email='remover@example.com')
    user.set_password('del')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    headers = login(test_app, 'deleter', 'del')

    tea = TeaModel(name="Not Long For This World Tea", in_stock=True, rating=6, user_id=user.id)
    test_db.add(tea)
    test_db.commit()

    response = test_app.delete(f"/api/teas/{tea.id}", headers=headers)
    assert response.status_code == 200
    # Try to retrieve the deleted tea
    response = test_app.get(f"/api/teas/{tea.id}", headers=headers)
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Tea not found"

def test_tea_not_found_for_deletion(test_app: TestClient, test_db: Session, override_get_db):
    user = UserModel(username='remover', email='deleter@example.com')
    user.set_password('swingandamiss')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    headers = login(test_app, 'remover', 'swingandamiss')

    max_tea_id = test_db.query(TeaModel.id).order_by(TeaModel.id.desc()).first()
    if max_tea_id is None:
        invalid_tea_id = 1
    else:
        invalid_tea_id = max_tea_id[0] + 1

    response = test_app.delete(f"/api/teas/{invalid_tea_id}", headers=headers)
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Tea not found"

def test_unauthorized_deletion(test_app: TestClient, test_db: Session, override_get_db):
    user_a= UserModel(username='usera', email='usera@example.com')
    user_a.set_password('passworda')
    test_db.add(user_a)
    test_db.commit()

    user_b = UserModel(username='userb', email='userb@example.com')
    user_b.set_password('passwordb')
    test_db.add(user_b)
    test_db.commit()

    tea = TeaModel(name="What is a Tea?", in_stock=True, rating=100, user_id=user_a.id)
    test_db.add(tea)
    test_db.commit()

    # Log in as user2 (who does not own the tea)
    headers = login(test_app, 'userb', 'passwordb')

    response = test_app.delete(f"/api/teas/{tea.id}", headers=headers)
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Operation forbidden"
