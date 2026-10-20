"""Popula a API com um cenario de demonstracao e mostra as anomalias detectadas.

Uso (com a API rodando):  python scripts/popular_demo.py [URL_BASE]
Usa so a biblioteca padrao do Python (nao precisa instalar nada).

Cenario (conta 1 - Joao Silva):
  1) 15 compras normais, sempre ~14h e valores entre 100 e 129
  2) uma compra de R$ 5000 as 03:15   -> valor elevado + horario atipico
  3) tres compras em 4 minutos        -> rajada de transacoes
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/financeiro").rstrip("/")


def chamar(metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read())


def lancar(valor, quando, categoria=1, descricao=None):
    status, resp = chamar("POST", "/transacoes", {
        "contaId": 1, "categoriaId": categoria, "valor": valor,
        "dataHora": quando.isoformat(), "descricao": descricao,
    })
    marca = "  <-- ANÔMALA" if resp.get("status") == "anomala" else ""
    print(f"  {quando:%d/%m %H:%M}  R$ {valor:>8}  -> {status}{marca}")
    for alerta in resp.get("alertas", []):
        print(f"       [{alerta['severidade']}] {alerta['tipo']}: {alerta['descricao']}")


print("1) Histórico normal")
inicio = datetime(2026, 9, 1, 14, 0)
for g in range(15):
    lancar(100 + (g * 7) % 30, inicio + timedelta(days=g), 1 + g % 2)

print("\n2) Compra atípica (valor e horário)")
lancar(5000, datetime(2026, 9, 20, 3, 15), 3, "Compra suspeita")

print("\n3) Rajada de transações")
for minuto, valor in ((0, 110), (2, 112), (4, 108)):
    lancar(valor, datetime(2026, 9, 21, 14, minuto))

print("\n4) Anomalias da conta 1 em setembro/2026 (regra 9)")
_, lista = chamar("GET", "/contas/1/anomalias?inicio=2026-09-01&fim=2026-09-30")
for a in lista:
    print(f"  {a['dataHora']}  {a['categoria']:<12} R$ {a['valor']:>8}  [{a['severidade']}] {a['tipo']}")

print("\n5) Estatísticas por categoria (regra 10)")
_, stats = chamar("GET", "/estatisticas/anomalias-por-categoria?inicio=2026-09-01&fim=2026-09-30")
for s in stats:
    print(f"  {s['categoria']:<12} alertas={s['totalAlertas']}  baixa={s['qtdBaixa']}  "
          f"média={s['qtdMedia']}  alta={s['qtdAlta']}")

print("\n6) Perfil atual da conta 1 (regra 7)")
_, perfil = chamar("GET", "/perfis-conta/1")
print(f"  {perfil['qtdTransacoes']} transações | média {perfil['media']:.2f} | desvio {perfil['desvioPadrao']:.2f}")
