from fastapi import status
from fastapi.testclient import TestClient

class TestAuth:

    def test_register(self, client: TestClient):
        response = client.post(
            "/api/auth/register",
            json = {
                "email": "example@example.com",
                "full_name": "john doe",
                "password": "12345678"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.json().keys()

    def test_login(self, client: TestClient):
        response = client.post(
            "/api/auth/login",
            json = {
                "email": "example@example.com",
                "password": "12345678"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json().keys()
