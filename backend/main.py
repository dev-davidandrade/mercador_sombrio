"""API FastAPI do Mercador Sombrio e hospedagem do frontend estático."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from backend import agente, banco
from backend.catalogo import LOJA, TAXAS, CATEGORIA_POR_ITEM, nome_bonito
from backend.economia import RegraDeNegocio, centavos, calcular_orcamento

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except ImportError:
    pass  # Apenas para testes de desenvolvimento sem dependências opcionais instaladas.
LOGGER = logging.getLogger(__name__)


class Pedido(BaseModel):
    item: str = Field(min_length=1, max_length=100)
    quantidade: int = Field(ge=1, le=1000)
    local: str = Field(min_length=1, max_length=100)


class EntradaHistorico(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(max_length=1800)


class PedidoChat(BaseModel):
    mensagem: str = Field(min_length=1, max_length=1000)
    historico: list[EntradaHistorico] = Field(default_factory=list, max_length=10)

    @field_validator('mensagem')
    @classmethod
    def nao_vazia(cls, value: str):
        if not value.strip():
            raise ValueError('Mensagem em branco')
        return value.strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    banco.inicializar()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title='Mercador Sombrio', version='0.1.0', lifespan=lifespan)
    app.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')

    @app.get('/', include_in_schema=False)
    async def inicio():
        return FileResponse(ROOT / 'frontend' / 'index.html')

    @app.get('/api/saude')
    async def saude():
        return {'status': 'online', 'versao': '0.1.0', 'modo_ia': agente.modo_ia(),
                'ferramentas_mcp': ['listar_loja', 'consultar_item', 'consultar_taxa', 'calcular_total']}

    @app.get('/api/loja')
    async def loja():
        return {
            'itens': [{'id': nome, 'nome': nome_bonito(nome),
                       'preco_centavos': centavos(preco),
                       'categoria': CATEGORIA_POR_ITEM[nome]} for nome, preco in LOJA.items()],
            'destinos': [{'id': destino, 'nome': nome_bonito(destino),
                          'taxa_centavos': centavos(taxa)} for destino, taxa in TAXAS.items()],
        }

    @app.get('/api/estado')
    async def estado():
        return banco.estado()

    @app.post('/api/orcamentos')
    async def orcamentos(pedido: Pedido):
        try:
            return calcular_orcamento(**pedido.model_dump()).como_dict()
        except RegraDeNegocio as erro:
            raise HTTPException(status_code=400, detail=str(erro)) from erro

    @app.post('/api/compras', status_code=201)
    async def compras(pedido: Pedido):
        try:
            orcamento = calcular_orcamento(**pedido.model_dump())
            return banco.comprar(orcamento)
        except RegraDeNegocio as erro:
            status = 409 if 'insuficiente' in str(erro) else 400
            raise HTTPException(status_code=status, detail=str(erro)) from erro

    @app.post('/api/reiniciar')
    async def reiniciar():
        # Apenas para projeto acadêmico single-player; sem autenticação. Não publicar abertamente.
        return banco.reiniciar()

    @app.post('/api/chat')
    async def chat(pedido: PedidoChat):
        resultado = await agente.responder(pedido.mensagem, [h.model_dump() for h in pedido.historico])
        if resultado.get('aviso'):
            LOGGER.warning('Modo básico ativado no chat: %s', resultado['aviso'])
        return resultado

    return app


app = create_app()
