import re

from django.contrib.auth import get_user_model
from django.core import mail
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

    def _registrar_e_obter_token(self):
        response = self.client.post(
            "/auth/register",
            json={
                "nome": "Loja Teste",
                "cnpj": "11222333000181",
                "username": "lojateste",
                "email": "contato@lojateste.com.br",
                "password": "senha-segura-123",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json()["token"]

    def test_atualizar_empresa(self):
        token = self._registrar_e_obter_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put(
            "/auth/empresa",
            json={
                "nome": "Loja Renomeada",
                "cnpj": "04252011000110",
                "username": "lojarenomeada",
                "email": "novo@lojateste.com.br",
            },
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "lojarenomeada")
        self.assertEqual(data["email"], "novo@lojateste.com.br")
        self.assertEqual(data["empresa"]["nome"], "Loja Renomeada")
        self.assertEqual(data["empresa"]["cnpj"], "04252011000110")

        # Manter o mesmo username (sem mudança) continua válido.
        response = self.client.put(
            "/auth/empresa",
            json={
                "nome": "Loja Renomeada",
                "cnpj": "04252011000110",
                "username": "lojarenomeada",
                "email": "novo@lojateste.com.br",
            },
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_atualizar_empresa_recusa_username_de_outra_conta(self):
        token = self._registrar_e_obter_token()
        response = self.client.put(
            "/auth/empresa",
            json={
                "nome": "Loja Teste",
                "cnpj": "11222333000181",
                "username": "admin",
                "email": "contato@lojateste.com.br",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 409)

    def test_alterar_senha(self):
        token = self._registrar_e_obter_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.post(
            "/auth/alterar-senha",
            json={"senha_atual": "errada", "nova_senha": "nova-senha-123"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/auth/alterar-senha",
            json={"senha_atual": "senha-segura-123", "nova_senha": "nova-senha-123"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/auth/login",
            json={"username": "lojateste", "password": "nova-senha-123"},
        )
        self.assertEqual(response.status_code, 200)

    def test_esqueci_senha_envia_email_com_link(self):
        response = self.client.post(
            "/auth/esqueci-senha", json={"email": "admin@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/redefinir-senha?uid=", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])

    def test_esqueci_senha_nao_revela_email_desconhecido(self):
        response = self.client.post(
            "/auth/esqueci-senha", json={"email": "naoexiste@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_redefinir_senha_com_link_do_email(self):
        self.client.post("/auth/esqueci-senha", json={"email": "admin@example.com"})
        match = re.search(
            r"/redefinir-senha\?uid=([^&\s]+)&token=([^\s]+)", mail.outbox[0].body
        )
        self.assertIsNotNone(match)
        uid, token = match.group(1), match.group(2)

        response = self.client.post(
            "/auth/redefinir-senha",
            json={"uid": uid, "token": token, "nova_senha": "senha-nova-456"},
        )
        self.assertEqual(response.status_code, 200)

        # Senha antiga deixa de valer; a nova funciona.
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "senha-segura-123"},
        )
        self.assertEqual(response.status_code, 401)
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "senha-nova-456"},
        )
        self.assertEqual(response.status_code, 200)

        # O mesmo token não pode ser reutilizado.
        response = self.client.post(
            "/auth/redefinir-senha",
            json={"uid": uid, "token": token, "nova_senha": "outra-senha-789"},
        )
        self.assertEqual(response.status_code, 400)

    def test_redefinir_senha_recusa_token_invalido(self):
        response = self.client.post(
            "/auth/redefinir-senha",
            json={"uid": "abc", "token": "invalido", "nova_senha": "senha-nova-456"},
        )
        self.assertEqual(response.status_code, 400)

    def test_me_exige_token(self):
        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_rota_catalogo_exige_token(self):
        response = self.client.get("/catalog/produtos/")
        self.assertEqual(response.status_code, 401)
