"""Regras de negócio, um módulo por assunto (ex.: contas.py para cadastro e login).

As rotas validam a entrada com os esquemas e chamam os serviços; os serviços usam app.db
para falar com o banco. Assim a regra fica testável sem passar pelo HTTP.
"""
