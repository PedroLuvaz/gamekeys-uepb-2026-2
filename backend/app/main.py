from fastapi import FastAPI

app = FastAPI(title="GameKeys API", version="0.1.0")


@app.get("/saude")
def saude() -> dict[str, str]:
    """Verificação de saúde usada pelo CI e, depois, pelo deploy."""
    return {"status": "ok"}
