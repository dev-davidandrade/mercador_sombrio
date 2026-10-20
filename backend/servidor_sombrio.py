"""Servidor MCP original, separado do agente e do banco de dados.

Iniciado pelo cliente MCP usando transporte stdio. Não execute manualmente em um terminal
para interagir com ele: o processo fica esperando mensagens do protocolo.
"""
import math
from typing import Any
from mcp.server.fastmcp import FastMCP
from pydantic import StrictInt, StrictFloat

from backend.catalogo import LOJA, TAXAS, normalizar

mcp = FastMCP('Vendedor Sombrio')


@mcp.tool()
def listar_loja() -> dict[str, Any]:
    """Lista todos os itens à venda e os locais de entrega, com preços.
    Use quando o aventureiro perguntar o que há na loja ou não souber o nome exato de um item ou local.
    """
    return {'itens': LOJA, 'locais de entrega': TAXAS}


@mcp.tool()
def consultar_item(nome_item: str) -> dict[str, Any]:
    """Consulta o preço de um item. Use o nome do item; se não souber, use listar_loja."""
    if not nome_item.strip():
        raise ValueError('Informe o nome de um item')
    nome = normalizar(nome_item)
    if nome not in LOJA:
        return {'encontrado': False, 'item': nome}
    return {'encontrado': True, 'item': nome, 'preco': LOJA[nome]}


@mcp.tool()
def consultar_taxa(nome_local: str) -> dict[str, Any]:
    """Consulta a taxa de entrega de um local. Se não souber, use listar_loja."""
    if not nome_local.strip():
        raise ValueError('Informe o nome de um local')
    local = normalizar(nome_local)
    if local not in TAXAS:
        return {'encontrado': False, 'local': local}
    return {'encontrado': True, 'local': local, 'taxa': TAXAS[local]}


@mcp.tool()
def calcular_total(quantidade: StrictInt, preco: StrictFloat, frete: StrictFloat) -> float:
    """Calcula quantidade (1 a 1000) vezes preço unitário (0 a 5000), mais taxa de entrega (0 a 1000)."""
    if type(quantidade) is not int or not 1 <= quantidade <= 1000:
        raise ValueError('Quantidade inválida')
    for valor, teto in [(preco, 5000), (frete, 1000)]:
        if type(valor) not in (int, float) or not math.isfinite(valor) or not 0 <= valor <= teto:
            raise ValueError('Preço ou taxa inválida')
    return round(quantidade * preco + frete, 2)


if __name__ == '__main__':
    mcp.run(transport='stdio')
