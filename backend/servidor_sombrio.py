"""Servidor MCP do Mercador Sombrio, sem ferramentas de entrega."""
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import StrictInt

from backend import banco
from backend.catalogo import (
    CATEGORIAS,
    CATEGORIA_POR_ITEM,
    LOJA,
    NOMES_CATEGORIAS,
    nome_bonito,
    normalizar,
)
from backend.economia import RegraDeNegocio, calcular_orcamento

mcp = FastMCP('Mercador Sombrio')

ALIASES_CATEGORIAS = {
    'arma': 'armas', 'armas': 'armas',
    'municao': 'municoes', 'municoes': 'municoes',
    'armadura': 'armaduras', 'armaduras': 'armaduras',
    'equipamento': 'armaduras', 'equipamentos': 'armaduras',
    'pocao': 'pocoes', 'pocoes': 'pocoes',
    'veneno': 'pocoes', 'venenos': 'pocoes',
    'magia': 'magia', 'magico': 'magia', 'magicos': 'magia',
    'raridade': 'magia', 'raridades': 'magia',
    'utilidade': 'utilidades', 'utilidades': 'utilidades',
}


def _dados_item(nome: str) -> dict[str, Any]:
    categoria = CATEGORIA_POR_ITEM[nome]
    return {
        'id': nome,
        'nome': nome_bonito(nome),
        'categoria': categoria,
        'categoria_nome': NOMES_CATEGORIAS[categoria],
        'preco_ouros': LOJA[nome],
    }


@mcp.tool()
def listar_mercadorias(categoria: str = "") -> dict[str, Any]:
    """Lista mercadorias e preços, opcionalmente filtrados por categoria.

    Categorias: armas, munições, armaduras, poções e venenos,
    magia e raridades, e utilidades.
    """
    filtro = normalizar(categoria)
    categoria_id = ALIASES_CATEGORIAS.get(filtro) if filtro else None
    if filtro and categoria_id is None:
        return {
            'encontrada': False,
            'erro': 'Categoria de mercadoria desconhecida.',
            'categorias': [
                {'id': chave, 'nome': titulo}
                for chave, titulo in NOMES_CATEGORIAS.items()
            ],
            'mercadorias': [],
        }

    nomes = CATEGORIAS[categoria_id] if categoria_id else list(LOJA)
    return {
        'encontrada': True,
        'filtro': categoria_id or 'todas',
        'categorias': [
            {'id': chave, 'nome': titulo}
            for chave, titulo in NOMES_CATEGORIAS.items()
        ],
        'quantidade': len(nomes),
        'mercadorias': [_dados_item(nome) for nome in nomes],
    }


@mcp.tool()
def consultar_item(nome_item: str) -> dict[str, Any]:
    """Consulta existência, categoria e preço oficial de uma mercadoria."""
    if not nome_item.strip():
        raise ValueError('Informe o nome de uma mercadoria')
    nome = normalizar(nome_item)
    if nome not in LOJA:
        return {'encontrado': False, 'item': nome}
    return {'encontrado': True, **_dados_item(nome)}


@mcp.tool()
def comprar_item(nome_item: str, quantidade: StrictInt = 1) -> dict[str, Any]:
    """Compra uma mercadoria imediatamente no balcão.

    O preço é sempre recalculado no servidor. A transação só debita os ouros
    e atualiza o inventário quando há saldo suficiente.
    """
    banco.inicializar()
    try:
        orcamento = calcular_orcamento(nome_item, quantidade)
        resultado = banco.comprar(orcamento)
        return {
            'sucesso': True,
            'mensagem': (
                f'{quantidade} × {nome_bonito(orcamento.item)} comprado por '
                f'{orcamento.total_centavos / 100:g} ouros.'
            ),
            **resultado,
        }
    except RegraDeNegocio as erro:
        return {
            'sucesso': False,
            'erro': str(erro),
            'estado': banco.estado(),
        }


if __name__ == '__main__':
    mcp.run(transport='stdio')
