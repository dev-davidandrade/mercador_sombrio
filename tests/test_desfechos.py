from pathlib import Path

import pytest

from backend.catalogo import LOJA
from backend.desfechos import progresso_desfecho, resolver_desfecho


ROOT = Path(__file__).resolve().parents[1]

ROTAS_JOGAVEIS = [
    ('o-ultimo-menino', {'elixir da juventude', 'flechas'}),
    (
        'alem-do-veu',
        {
            'pergaminho de teleporte', 'grimorio proibido', 'olho de dragao',
            'flechas', 'virotes', 'tocha', 'racao de viagem', 'corda',
        },
    ),
    (
        'o-novo-rei-demonio',
        {
            'foice amaldicoada', 'amuleto sombrio', 'grimorio proibido',
            'flechas', 'virotes', 'tocha', 'racao de viagem', 'corda',
        },
    ),
    (
        'a-lamina-invisivel',
        {
            'adaga', 'capa das sombras', 'pocao de invisibilidade',
            'veneno paralisante', 'flechas', 'virotes', 'tocha',
            'racao de viagem',
        },
    ),
    (
        'arquimago-do-ultimo-portal',
        {
            'cajado', 'pocao de mana', 'anel de protecao', 'amuleto sombrio',
            'flechas', 'virotes', 'tocha', 'racao de viagem',
        },
    ),
    (
        'a-flecha-antes-da-aurora',
        {
            'arco', 'flechas', 'mapa antigo', 'flechas de fogo', 'virotes',
            'tocha', 'racao de viagem', 'corda',
        },
    ),
    (
        'o-bastiao-do-reino',
        {
            'armadura', 'escudo', 'espada', 'pocao de vida', 'flechas',
            'virotes', 'tocha', 'racao de viagem',
        },
    ),
    (
        'vitoria-do-amanhecer',
        {
            'espada', 'escudo', 'pocao de vida', 'tocha', 'flechas',
            'virotes', 'racao de viagem', 'corda',
        },
    ),
    (
        'vitoria-postuma',
        {
            'espada longa', 'pocao de forca', 'flechas', 'virotes', 'tocha',
            'racao de viagem', 'corda', 'bomba',
        },
    ),
    (
        'sobrevivente-nao-salvador',
        {
            'pergaminho de teleporte', 'flechas', 'virotes', 'tocha',
            'racao de viagem', 'corda', 'bomba', 'facas de arremesso',
        },
    ),
    (
        'a-batalha-sem-profecia',
        {
            'flechas', 'virotes', 'tocha', 'racao de viagem', 'corda',
            'bomba', 'facas de arremesso', 'lanterna',
        },
    ),
]


@pytest.mark.parametrize(
    ('esperado', 'itens'),
    ROTAS_JOGAVEIS,
)
def test_todos_os_desfechos_sao_jogaveis_e_possuem_cronica(esperado, itens):
    custo_centavos = round(sum(LOJA[item] for item in itens) * 100)
    estado = {
        'ouro_centavos': 100_000 - custo_centavos,
        'inventario': [
            {'item': item, 'quantidade': 1}
            for item in itens
        ]
    }
    progresso = progresso_desfecho(
        estado['inventario'], estado['ouro_centavos']
    )
    resultado = resolver_desfecho(estado)
    assert custo_centavos <= 100_000
    assert progresso['disponivel'] is True
    assert resultado['id'] == esperado
    assert len(resultado['texto']) >= 6
    assert all(len(paragrafo) >= 80 for paragrafo in resultado['texto'])
    assert len(resultado['slides']) == 4
    assert '/static/assets/scenes/endings/' in resultado['slides'][-1]
    asset = ROOT / 'frontend' / resultado['slides'][-1].removeprefix('/static/')
    assert asset.is_file()


def test_segredo_do_ultimo_menino_esgota_exatamente_mil_ouros():
    assert LOJA['elixir da juventude'] + LOJA['flechas'] == 1000
