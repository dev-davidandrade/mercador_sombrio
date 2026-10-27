"""Smoke test da integração MCP por stdio."""
import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip('mcp', reason='SDK MCP não instalado neste ambiente')
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def _dados(resultado):
    if resultado.structuredContent is not None:
        return resultado.structuredContent
    return json.loads(resultado.content[0].text)


async def _teste(database_path: Path):
    ambiente = os.environ.copy()
    ambiente.update({
        'PYTHONPATH': str(ROOT),
        'DATABASE_PATH': str(database_path),
    })
    parametros = StdioServerParameters(
        command=sys.executable,
        args=['-m', 'backend.servidor_sombrio'],
        env=ambiente,
    )
    async with stdio_client(parametros) as (read, write):
        async with ClientSession(read, write) as sessao:
            await sessao.initialize()
            lista = await sessao.list_tools()
            nomes = {f.name for f in lista.tools}
            assert nomes == {
                'listar_mercadorias',
                'consultar_item',
                'comprar_item',
            }

            pocoes = await sessao.call_tool(
                'listar_mercadorias',
                {'categoria': 'pocoes'},
            )
            assert not pocoes.isError
            dados_pocoes = _dados(pocoes)
            assert dados_pocoes['quantidade'] == 8
            assert {
                item['id'] for item in dados_pocoes['mercadorias']
            } == {
                'pocao de vida', 'pocao de mana', 'pocao de forca',
                'pocao de invisibilidade', 'antidoto', 'veneno',
                'veneno paralisante', 'elixir da juventude',
            }
            assert 'locais' not in dados_pocoes
            assert 'destinos' not in dados_pocoes

            item = await sessao.call_tool(
                'consultar_item',
                {'nome_item': 'pocao de vida'},
            )
            assert not item.isError
            dados_item = _dados(item)
            assert dados_item['encontrado'] is True
            assert dados_item['preco_ouros'] == 10
            assert dados_item['categoria'] == 'pocoes'

            compra = await sessao.call_tool(
                'comprar_item',
                {'nome_item': 'pocao de vida', 'quantidade': 2},
            )
            assert not compra.isError
            dados_compra = _dados(compra)
            assert dados_compra['sucesso'] is True
            assert dados_compra['estado']['ouro_centavos'] == 98000
            assert dados_compra['estado']['inventario'][0]['item'] == 'pocao de vida'

            sem_saldo = await sessao.call_tool(
                'comprar_item',
                {'nome_item': 'alma engarrafada', 'quantidade': 4},
            )
            dados_sem_saldo = _dados(sem_saldo)
            assert dados_sem_saldo['sucesso'] is False
            assert dados_sem_saldo['estado']['ouro_centavos'] == 98000


def test_mcp_stdio_lista_e_chama_ferramentas(tmp_path):
    asyncio.run(_teste(tmp_path / 'mcp.db'))
