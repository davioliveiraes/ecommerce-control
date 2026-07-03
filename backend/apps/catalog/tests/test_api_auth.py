from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from config.api import api


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="senha-segura-123",
            email="admin@example.com",
        )

    def test_login_retorna_token(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "senha-segura-123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"])
        self.assertEqual(data["token_type"], "Bearer")
        self.assertEqual(data["user"]["username"], "admin")

    def test_login_por_email(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "admin@example.com", "password": "senha-segura-123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "admin")

    def test_register_cria_empresa_com_username(self):
        payload = {
            "nome": "Loja Teste",
            "cnpj": "11222333000181",
            "username": "lojateste",
            "email": "contato@lojateste.com.br",
            "password": "senha-segura-123",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["user"]["username"], "lojateste")
        self.assertEqual(data["user"]["empresa"]["nome"], "Loja Teste")

        # Login pelo username escolhido e pelo e-mail.
        for identificador in ("lojateste", "contato@lojateste.com.br"):
            response = self.client.post(
                "/auth/login",
                json={"username": identificador, "password": "senha-segura-123"},
            )
            self.assertEqual(response.status_code, 200, identificador)

    def test_register_recusa_username_duplicado(self):
        payload = {
            "nome": "Loja Teste",
            "cnpj": "11222333000181",
            "username": "admin",
            "email": "contato@lojateste.com.br",
            "password": "senha-segura-123",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 409)

    def test_register_recusa_username_invalido(self):
        payload = {
            "nome": "Loja Teste",
            "cnpj": "11222333000181",
            "username": "a b@c",
            "email": "contato@lojateste.com.br",
            "password": "senha-segura-123",
        }
        response = self.client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_me_exige_token(self):
        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_rota_catalogo_exige_token(self):
        response = self.client.get("/catalog/produtos/")
        self.assertEqual(response.status_code, 401)
