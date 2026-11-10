"""Mensagens públicas e estáveis para erros de entrada da API."""

from typing import Any

MENSAGENS_POR_CAMPO = {
    "nome": "Informe um nome entre 2 e 120 caracteres.",
    "email": "Informe um e-mail válido.",
    "data_nascimento": "Informe uma data de nascimento válida.",
    "senha": "Informe sua senha.",
    "jogo_id": "Informe um jogo válido.",
    "quantidade": "Informe uma quantidade inteira maior que zero.",
    "chave_idempotencia": "Informe um identificador de reserva válido.",
}


def traduzir_erro(erro: dict[str, Any]) -> dict[str, Any]:
    """Preserva a estrutura 422 do FastAPI e troca apenas a mensagem pública."""
    mensagem = str(erro.get("msg", ""))
    if mensagem.startswith("Value error, "):
        traduzida = mensagem.removeprefix("Value error, ")
    elif erro.get("type") == "extra_forbidden":
        traduzida = "Este campo não é aceito."
    else:
        localizacao = erro.get("loc", ())
        campo = next(
            (parte for parte in reversed(localizacao) if isinstance(parte, str)),
            None,
        )
        traduzida = MENSAGENS_POR_CAMPO.get(campo, "")
        if not traduzida:
            traduzida = (
                "Preencha os campos obrigatórios."
                if erro.get("type") == "missing"
                else "Revise os dados informados."
            )
    return {**erro, "msg": traduzida}
