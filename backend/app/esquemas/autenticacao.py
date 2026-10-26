"""Contratos públicos de login e sessão (GK-8)."""

from pydantic import BaseModel, field_validator

from app.esquemas.clientes import FORMATO_EMAIL, ClienteCadastrado


class Credenciais(BaseModel):
    email: str
    senha: str

    @field_validator("email")
    @classmethod
    def validar_email(cls, email: str) -> str:
        email = email.strip().lower()
        if len(email) > 254 or not FORMATO_EMAIL.fullmatch(email):
            raise ValueError("Informe um e-mail válido.")
        return email


class SessaoCriada(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: ClienteCadastrado
