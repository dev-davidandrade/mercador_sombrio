"""Servidor MCP original, separado do agente e do banco de dados.

Iniciado pelo cliente MCP usando transporte stdio. Não execute manualmente em um terminal
para interagir com ele: o processo fica esperando mensagens do protocolo.
"""
import math
from typing import Any
from mcp.server.fastmcp import FastMCP
from pydantic import StrictInt, StrictFloat

from backend.catalogo import LOJA, TAXAS, normalizar, CATEGORIA_POR_ITEM, nome_bonito

mcp = FastMCP('Vendedor Sombrio')


@mcp.tool()
def listar_loja() -> dict[str, Any]:
    """Lista todos os itens à venda.
    """
    return {'itens': LOJA, 'locais de entrega': TAXAS}


@mcp.tool()
def listar_itens(tipo: str = "") -> dict[str, Any]:
    """Lista mercadorias disponíveis e seus preços.
    
    Se tipo estiver vazio, retorna todos os itens.
    Exemplos de filtro:
    - 'armas': todas as armas
    - 'armas curtas': adaga e machado
    - 'armas longas': lança e martelo de guerra
    - 'armas de longo alcance': arco, besta
    - 'armas magicas': cajado, foice amaldicoada
    - 'espadas': itens com espada no nome
    - 'laminas': espada, espada longa, adaga, machado e foice amaldicoada
    - 'municao': flechas, flechas de fogo, virotes, facas de arremesso
    - 'bombas': bomba, bomba de fumaca
    - 'pocoes': todas as poções
    - 'armaduras': equipamentos defensivos
    - 'pergaminhos': pergaminhos disponíveis
    - 'outros itens': itens que não se encaixam nas categorias acima
     mas existem na loja como por exemplo: gazua ou lanterna, tocha ou
     mapa_antigo
    """

    categorias = {
        'arma': 'armas',
        'armas': 'armas',
        'armadura': 'armaduras',
        'armaduras': 'armaduras',
        'equipamentos': 'armaduras',
        'pocao': 'pocoes',
        'pocoes': 'pocoes',
        'magia': 'magia',
        'magicos': 'magia',
        'municao': 'municoes',
        'municoes': 'municoes',
        'utilidade': 'utilidades',
        'utilidades': 'utilidades',
    }

    filtro = normalizar(tipo)

    if not filtro:
        encontrados = list(LOJA)

    elif filtro in categorias:
        categoria = categorias[filtro]
        encontrados = [
            nome for nome in LOJA
            if CATEGORIA_POR_ITEM[nome] == categoria
        ]

    else:
        # Espadas -> espada
        # Pergaminhos -> pergaminho
        termo = filtro [:-1] if filtro.endswith('s') else filtro

        encontrados = [
            nome for nome in LOJA
            if termo in nome
        ]

    itens = [
        {
            'id': nome,
            'nome': nome_bonito(nome),
            'categoria': CATEGORIA_POR_ITEM[nome],
            'preco_ouro': LOJA[nome]
        }
        for nome in encontrados
    ]

    return {
        'filtro': tipo or 'todos',
        'quantidade': len(itens),
        'itens': itens
    }


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
def listar_locais_entrega() -> dict[str, Any]:
    """Lista todos os destinos de entrega disponíveis.

    Retorna cada local e sua respectiva taxa em ouro.
    Use quando o jogador perguntar para onde o
    mercador entrega, quais destinos existem ou
    quais são os preços de entrega.
    """

    locais = [
        {
            'id': nome,
            'nome': nome_bonito(nome),
            'taxa_ouro': taxa
        }
        for nome, taxa in TAXAS.items()
    ]

    return {
        'quantidade': len(locais),
        'locais': locais
    }


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