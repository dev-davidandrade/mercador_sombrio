"""Smoke test de integração real: executado quando SDK MCP estiver instalado.

CI instala requirements-dev.txt. No ambiente offline de autoria, o teste é marcado skip.
"""
import asyncio
import json
import sys
from pathlib import Path

import pytest

mcp = pytest.importorskip('mcp', reason='SDK MCP não instalado neste ambiente')
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def _teste():
    parametros = StdioServerParameters(command=sys.executable,
                                     args=['-m', 'backend.servidor_sombrio'],
                                     env={'PYTHONPATH': str(ROOT)})
    async with stdio_client(parametros) as (read, write):
        async with ClientSession(read, write) as sessao:
            await sessao.initialize()
            lista = await sessao.list_tools()
            nomes = {f.name for f in lista.tools}
            assert nomes == {
                'listar_loja',
                'listar_itens',
                'listar_locais_entrega',
                'consultar_item',
                'consultar_taxa',
                'calcular_total',
            }

            grupo = await sessao.call_tool(
                'listar_itens',
                {'tipo': 'armas curtas'},
            )
            assert not grupo.isError

            dados_grupo = grupo.structuredContent
            if dados_grupo is None:
                dados_grupo = json.loads(grupo.content[0].text)

            assert {
                item['id'] for item in dados_grupo['itens']
            } == {'adaga', 'machado'}

            laminas = await sessao.call_tool(
                'listar_itens',
                {'tipo': 'lâminas'},
            )
            assert not laminas.isError

            dados_laminas = laminas.structuredContent
            if dados_laminas is None:
                dados_laminas = json.loads(laminas.content[0].text)

            assert {
                item['id'] for item in dados_laminas['itens']
            } == {
                'espada', 'espada longa', 'adaga',
                'machado', 'foice amaldicoada',
            }

            loja = await sessao.call_tool('listar_loja', {})
            assert not loja.isError

            dados_loja = loja.structuredContent
            if dados_loja is None:
                dados_loja = json.loads(loja.content[0].text)

            assert dados_loja['categorias'] == [
                'armas', 'municoes', 'armaduras',
                'pocoes', 'magia', 'utilidades',
            ]

            item = await sessao.call_tool('consultar_item', {'nome_item': 'poção de vida'})
            assert not item.isError
            dados = item.structuredContent
            if dados is None:
                dados = json.loads(item.content[0].text)
            assert dados['encontrado'] is True
            assert dados['preco'] == 10.0
            total = await sessao.call_tool('calcular_total',
                                           {'quantidade': 2, 'preco': 10.0, 'frete': 5.0})
            assert not total.isError


def test_mcp_stdio_lista_e_chama_ferramentas():
    asyncio.run(_teste())
