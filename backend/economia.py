"""Regras de negócio independentes do agente. Valores armazenados em centésimos de ouro."""
from dataclasses import dataclass
from decimal import Decimal
from backend.catalogo import LOJA, TAXAS, normalizar


class RegraDeNegocio(ValueError):
    """Falha esperada de validação comercial."""


def centavos(valor: int | float) -> int:
    return int(Decimal(str(valor)) * 100)


@dataclass(frozen=True)
class Orcamento:
    item: str
    quantidade: int
    local: str
    preco_unitario_centavos: int
    subtotal_centavos: int
    taxa_centavos: int
    total_centavos: int

    def como_dict(self) -> dict:
        return vars(self).copy()


def calcular_orcamento(item: str, quantidade: int, local: str) -> Orcamento:
    item, local = normalizar(item), normalizar(local)
    if item not in LOJA:
        raise RegraDeNegocio('Mercadoria desconhecida. Consulte a loja.')
    if local not in TAXAS:
        raise RegraDeNegocio('Destino de entrega desconhecido.')
    if type(quantidade) is not int or not 1 <= quantidade <= 1000:
        raise RegraDeNegocio('A quantidade deve ficar entre 1 e 1000.')
    preco = centavos(LOJA[item])
    taxa = centavos(TAXAS[local])
    subtotal = preco * quantidade
    return Orcamento(item, quantidade, local, preco, subtotal, taxa, subtotal + taxa)
