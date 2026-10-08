# Detecção de Anomalias em Transações Financeiras

Sistema para registrar transações e identificar operações fora do padrão de cada conta.
Trabalho P1 - Python | API REST + Interface gráfica + Docker.

## Autores
- Enzo BC Costa
- João Vitor Ferraz

## Tecnologias
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker / Docker Compose

## Estrutura da API

```
projeto_API/
├── entities/        # modelos SQLAlchemy
├── controllers/     # recebem as requisições
├── services/        # regras de negócio e detectores
├── repositories/    # acesso ao banco
├── routes/          # definição dos endpoints
├── config/          # configuração e conexão
└── app.py
```

## Banco de dados

| Tabela | Descrição |
|---|---|
| `contas` | Contas e perfil médio de gastos |
| `categorias` | Categorias das transações |
| `transacoes` | Transações registradas |
| `alertas_anomalia` | Anomalias detectadas |

## Endpoints principais

Cada entidade possui `POST`, `GET`, `PUT` e `DELETE`:

- `/contas`
- `/categorias`
- `/transacoes`
- `/alertas`

## Regras de negócio

1. Não permite transação com valor negativo ou zero.
2. Não permite transação para conta inexistente.
3. Marca como anômala transação com valor muito acima da média da conta (desvio padrão).
4. Identifica transações em horários atípicos para a conta.
5. Identifica múltiplas transações em curto intervalo de tempo.
6. Não permite excluir transação que possui alerta vinculado.
7. Atualiza o perfil médio de gastos da conta a cada nova transação.
8. Classifica a severidade (baixa, média, alta) conforme a distância do padrão.
9. Permite consultar anomalias de uma conta por período.
10. Gera estatísticas de anomalias por categoria em um período.
