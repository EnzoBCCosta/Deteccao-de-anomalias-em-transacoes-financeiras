class ErroNegocio(Exception):
    """Erro de regra de negócio. Por padrão vira HTTP 400 (requisição inválida)."""

    def __init__(self, mensagem: str, status: int = 400):
        super().__init__(mensagem)
        self._mensagem = mensagem
        self._status = status

    # Encapsulamento: atributos "privados" expostos somente para leitura
    @property
    def mensagem(self) -> str:
        return self._mensagem

    @property
    def status(self) -> int:
        return self._status


class NaoEncontrado(ErroNegocio):
    """Registro inexistente (HTTP 404)."""

    def __init__(self, mensagem: str):
        super().__init__(mensagem, 404)


class Conflito(ErroNegocio):
    """Operação proibida pelo estado atual dos dados (HTTP 409)."""

    def __init__(self, mensagem: str):
        super().__init__(mensagem, 409)
