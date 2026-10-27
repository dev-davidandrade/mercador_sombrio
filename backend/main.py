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
from backend.catalogo import (
    CATEGORIA_POR_ITEM,
    LOJA,
    NOMES_CATEGORIAS,
    nome_bonito,
)
from backend.economia import RegraDeNegocio, calcular_orcamento, centavos
from backend.desfechos import resolver_desfecho

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except ImportError:
    pass
LOGGER = logging.getLogger(__name__)


class PedidoCompra(BaseModel):
    item: str = Field(min_length=1, max_length=100)
    quantidade: int = Field(ge=1, le=1000)


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
    app = FastAPI(title='Mercador Sombrio', version='0.5.0', lifespan=lifespan)
    app.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')

    @app.get('/', include_in_schema=False)
    async def inicio():
        return FileResponse(ROOT / 'frontend' / 'index.html')

    @app.get('/api/saude')
    async def saude():
        return {
            'status': 'online',
            'versao': '0.5.0',
            'modo_ia': agente.modo_ia(),
            'ferramentas_mcp': sorted(agente.PERMITIDAS),
        }

    @app.get('/api/loja')
    async def loja():
        return {
            'categorias': [
                {'id': categoria, 'nome': nome}
                for categoria, nome in NOMES_CATEGORIAS.items()
            ],
            'itens': [
                {
                    'id': item,
                    'nome': nome_bonito(item),
                    'preco_centavos': centavos(preco),
                    'categoria': CATEGORIA_POR_ITEM[item],
                }
                for item, preco in LOJA.items()
            ],
        }

    @app.get('/api/estado')
    async def estado():
        return banco.estado()

    @app.post('/api/orcamentos')
    async def orcamentos(pedido: PedidoCompra):
        try:
            return calcular_orcamento(**pedido.model_dump()).como_dict()
        except RegraDeNegocio as erro:
            raise HTTPException(status_code=400, detail=str(erro)) from erro

    @app.post('/api/compras', status_code=201)
    async def compras(pedido: PedidoCompra):
        try:
            orcamento = calcular_orcamento(**pedido.model_dump())
            return banco.comprar(orcamento)
        except RegraDeNegocio as erro:
            status = 409 if 'insuficiente' in str(erro) else 400
            raise HTTPException(status_code=status, detail=str(erro)) from erro

    @app.post('/api/reiniciar')
    async def reiniciar():
        return banco.reiniciar()

    @app.get('/api/desfecho')
    async def desfecho():
        atual = banco.estado()
        if not atual['desfecho']['disponivel']:
            faltam = atual['desfecho']['limite_tipos'] - atual['desfecho']['tipos_escolhidos']
            raise HTTPException(
                status_code=409,
                detail=f'Escolha mais {faltam} tipos de mercadoria antes de partir.',
            )
        return {
            **resolver_desfecho(atual),
            'progresso': atual['desfecho'],
        }

    @app.post('/api/chat')
    async def chat(pedido: PedidoChat):
        resultado = await agente.responder(
            pedido.mensagem,
            [entrada.model_dump() for entrada in pedido.historico],
        )
        if resultado.get('aviso'):
            LOGGER.warning('Modo básico ativado no chat: %s', resultado['aviso'])
        return resultado

    return app


app = create_app()
