from pydantic import BaseModel


class Saude(BaseModel):
    status: str


class SaudeBanco(Saude):
    banco: str
    versao: str
