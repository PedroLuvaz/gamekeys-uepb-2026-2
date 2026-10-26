"""Contratos públicos do cadastro de clientes (GK-7)."""

import re
from datetime import date

from pydantic import BaseModel, field_validator

FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CadastroDeCliente(BaseModel):
    nome: str
    email: str
    data_nascimento: date
    senha: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome: str) -> str:
        nome = nome.strip()
        if not 2 <= len(nome) <= 120:
            raise ValueError("Informe um nome entre 2 e 120 caracteres.")
        return nome

    @field_validator("email")
    @classmethod
    def validar_email(cls, email: str) -> str:
        email = email.strip().lower()
        if len(email) > 254 or not FORMATO_EMAIL.fullmatch(email):
            raise ValueError("Informe um e-mail válido.")
        return email

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, data_nascimento: date) -> date:
        if data_nascimento < date(1900, 1, 1) or data_nascimento > date.today():
            raise ValueError("Informe uma data de nascimento válida.")
        return data_nascimento

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, senha: str) -> str:
        if len(senha) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if len(senha.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes.")
        return senha


class ClienteCadastrado(BaseModel):
    id: int
    nome: str
    email: str
    data_nascimento: date
    perfil: str
