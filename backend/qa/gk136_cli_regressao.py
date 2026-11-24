"""Prova do parser do CLI real com HTTP loopback e credenciais fictícias.

Não consulta Vercel, Neon ou qualquer endpoint remoto. O bypass é só uma fixture.
"""

import json
import os
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

SHA = "a" * 40
TOKEN = "gk136fixturetoken"
BYPASS = "gk136fixturebypass"


def main():
    cli = shutil.which("vercel")
    if not cli:
        raise SystemExit("Instale o CLI fixado vercel@65.2.0 para executar esta regressão.")
    comando = [cli]
    if os.name == "nt":
        # Não passar a quebra de linha de --write-out por um wrapper .CMD.
        pasta = Path(cli).parent
        entradas = (
            pasta.parent / "vercel/dist/index.js",
            pasta / "node_modules/vercel/dist/index.js",
        )
        entrada = next((p for p in entradas if p.is_file()), None)
        node = shutil.which("node")
        if not entrada or not node:
            raise RuntimeError("Não foi possível localizar a entrada Node do CLI no Windows.")
        comando = [node, str(entrada)]
    chamadas = []

    class Resposta(BaseHTTPRequestHandler):
        def do_GET(self):
            assert self.path == "/saude/versao"
            assert self.headers.get("x-vercel-protection-bypass") == BYPASS
            assert TOKEN not in str(self.headers)
            chamadas.append(self.path)
            corpo = json.dumps({"commit": SHA}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, *_):
            pass

    ambiente = os.environ.copy()
    for nome in (
        "VERCEL_ORG_ID",
        "VERCEL_PROJECT_ID",
        "VERCEL_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DATABASE_URL",
        "DATABASE_URL_UNPOOLED",
        "TEST_DATABASE_URL",
        "HOMOLOGACAO_DATABASE_URL_UNPOOLED",
        "JWT_SECRET",
        "PGPASSWORD",
    ):
        ambiente.pop(nome, None)
    ambiente.update(
        VERCEL_TOKEN=TOKEN,
        VERCEL_AUTOMATION_BYPASS_SECRET=BYPASS,
        VERCEL_TELEMETRY_DISABLED="1",
        NO_COLOR="1",
    )
    servidor = HTTPServer(("127.0.0.1", 0), Resposta)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{servidor.server_port}/saude/versao"
        flags = [
            "--",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            "5",
            "--write-out",
            "\n%{http_code}",
        ]
        legado = subprocess.run(
            [*comando, "curl", url, "--token", TOKEN, *flags],
            env=ambiente,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        if legado.returncode != 2 or "option --token: is unknown" not in legado.stderr:
            raise RuntimeError("O controle negativo não reproduziu o erro do parser fixado.")
        if chamadas:
            raise RuntimeError("O comando legado não deveria alcançar a fixture HTTP.")
        correto = subprocess.run(
            [*comando, "curl", url, *flags],
            env=ambiente,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        corpo, _, status = correto.stdout.rpartition("\n")
        if correto.returncode or status != "200" or json.loads(corpo) != {"commit": SHA}:
            raise RuntimeError("A chamada com autenticação no ambiente não passou.")
        if len(chamadas) != 1:
            raise RuntimeError("Quantidade inesperada de chamadas HTTP.")
        resultado = {
            "experimento": "GK-136 CLI 65.2.0",
            "ambiente": "HTTP loopback; dados fictícios",
            "controle_negativo": "erro do parser reproduzido; zero chamadas HTTP",
            "autenticacao_no_ambiente": "aprovada",
            "http": 200,
            "chamadas": 1,
            "token_enviado_ao_servidor": False,
        }
        destino = Path("relatorios/vercel-cli-gk136.json")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(resultado, ensure_ascii=False))
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
