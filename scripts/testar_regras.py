"""Teste automatizado das 10 regras de negócio e do CRUD, via HTTP.

Uso (com a API rodando):  python scripts/testar_regras.py [URL_BASE]
Usa só a biblioteca padrão. Cria uma conta e uma categoria próprias ("[TESTE]")
e remove tudo no final, então não atrapalha os dados da demonstração.
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/financeiro").rstrip("/")
resultados = []


def chamar(metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read())


def verificar(descricao, condicao, detalhe=""):
    resultados.append(bool(condicao))
    print(f"  [{'OK' if condicao else 'FALHOU'}] {descricao}" + (f"  -> {detalhe}" if not condicao else ""))


def titulo(texto):
    print(f"\n{texto}")


def lancar(conta, categoria, valor, quando):
    return chamar("POST", "/transacoes", {"contaId": conta, "categoriaId": categoria,
                                          "valor": valor, "dataHora": quando.isoformat()})


# ------------------------------------------------------------------ preparação
_, conta = chamar("POST", "/contas", {"titular": "[TESTE] Conta de regras"})
_, categoria = chamar("POST", "/categorias", {"nome": "[TESTE] Categoria"})
C, K = conta["id"], categoria["id"]
base = datetime(2026, 8, 1, 14, 0)
transacoes = []

titulo("Regras 1 e 2 - bloqueios no cadastro")
s, r = lancar(C, K, -10, base)
verificar("R1: valor negativo rejeitado (400)", s == 400 and "maior que zero" in r["message"], r)
s, r = lancar(C, K, 0, base)
verificar("R1: valor zero rejeitado (400)", s == 400, r)
s, r = lancar(999999, K, 50, base)
verificar("R2: conta inexistente rejeitada (400)", s == 400 and "não existe" in r["message"], r)

titulo("Regra 7 - perfil atualizado a cada transação")
for i in range(12):
    s, r = lancar(C, K, 100 + i, base + timedelta(days=i))
    transacoes.append(r["id"])
s, perfil = chamar("GET", f"/perfis-conta/{C}")
verificar("R7: perfil tem 12 transações", s == 200 and perfil["qtdTransacoes"] == 12, perfil)
verificar("R7: média correta (105,5)", abs(perfil["media"] - 105.5) < 0.01, perfil)

titulo("Regras 3, 4 e 8 - valor elevado, horário atípico e severidade")
s, r = lancar(C, K, 5000, datetime(2026, 8, 20, 3, 15))
transacoes.append(r["id"])
tipos = {a["tipo"]: a["severidade"] for a in r.get("alertas", [])}
verificar("R3: transação marcada como anômala", r.get("status") == "anomala", r)
verificar("R3/R8: valor elevado com severidade alta", tipos.get("valor_elevado") == "alta", tipos)
verificar("R4: horário atípico detectado", "horario_atipico" in tipos, tipos)
anomala_id = r["id"]
s, r = lancar(C, K, 105, datetime(2026, 8, 21, 14, 0))
transacoes.append(r["id"])
verificar("transação comum permanece normal", r.get("status") == "normal", r)

titulo("Regra 5 - rajada de transações")
for minuto in (0, 2, 4):
    s, r = lancar(C, K, 104 + minuto, datetime(2026, 8, 22, 14, minuto))
    transacoes.append(r["id"])
verificar("R5: 3ª transação em 4 minutos é anômala",
          r.get("status") == "anomala" and any(a["tipo"] == "rajada_transacoes" for a in r["alertas"]), r)

titulo("Regra 6 - exclusão bloqueada")
s, r = chamar("DELETE", f"/transacoes/{anomala_id}")
verificar("R6: transação com alerta não pode ser excluída (409)", s == 409, (s, r))

titulo("Regras 9 e 10 - consultas")
s, lista = chamar("GET", f"/contas/{C}/anomalias?inicio=2026-08-01&fim=2026-08-31")
verificar("R9: anomalias da conta no período (3 alertas)", s == 200 and len(lista) == 3, lista)
s, lista = chamar("GET", f"/contas/{C}/anomalias?inicio=2026-01-01&fim=2026-01-31")
verificar("R9: período sem anomalias retorna lista vazia", s == 200 and lista == [], lista)
s, stats = chamar("GET", "/estatisticas/anomalias-por-categoria?inicio=2026-08-01&fim=2026-08-31")
minha = [x for x in stats if x["categoria"] == "[TESTE] Categoria"]
verificar("R10: estatística da categoria (3 alertas, 2 transações anômalas)",
          minha and minha[0]["totalAlertas"] == 3 and minha[0]["transacoesAnomalas"] == 2, minha)

titulo("Validações e CRUD")
s, r = chamar("POST", "/transacoes", {"contaId": C})
verificar("campos obrigatórios ausentes (400)", s == 400 and "obrigatório" in r["message"], r)
s, r = chamar("GET", "/transacoes/99999999")
verificar("registro inexistente (404)", s == 404, r)
s, r = chamar("PUT", f"/transacoes/{transacoes[0]}", {"descricao": "editada", "valor": 9999})
verificar("editar valor de transação é proibido (400)", s == 400, r)
s, r = chamar("PUT", f"/transacoes/{transacoes[0]}", {"descricao": "editada"})
verificar("editar descrição é permitido (200)", s == 200 and r["descricao"] == "editada", r)
s, r = chamar("DELETE", f"/contas/{C}")
verificar("conta com transações não pode ser excluída (409)", s == 409, r)
s, r = chamar("DELETE", f"/categorias/{K}")
verificar("categoria em uso não pode ser excluída (409)", s == 409, r)

titulo("Limpeza (também exercita DELETE e a coerência do perfil)")
s, alertas = chamar("GET", "/alertas")
for a in [x for x in alertas if x["contaId"] == C]:
    chamar("DELETE", f"/alertas/{a['id']}")
for t in transacoes:
    s, _ = chamar("DELETE", f"/transacoes/{t}")
    if s != 200:
        verificar(f"excluir transação {t}", False, s)
s, _ = chamar("GET", f"/perfis-conta/{C}")
verificar("perfil removido junto com a última transação (404)", s == 404)
s1, _ = chamar("DELETE", f"/contas/{C}")
s2, _ = chamar("DELETE", f"/categorias/{K}")
verificar("conta e categoria de teste excluídas", s1 == 200 and s2 == 200, (s1, s2))

print(f"\n{sum(resultados)}/{len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
