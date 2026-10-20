import os

# URL de conexão com o PostgreSQL.
# No Docker a variável DATABASE_URL é definida no docker-compose.yml (host = "db").
# Rodando localmente (sem Docker) usa o valor padrão abaixo.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/anomalias",
)

# Prefixo de todas as rotas da API (igual ao prefix="/academico" da Aula 5)
PREFIXO_API = "/financeiro"
