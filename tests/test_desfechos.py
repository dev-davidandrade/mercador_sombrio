from pathlib import Path

import pytest

from backend.desfechos import resolver_desfecho


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ('esperado', 'itens'),
    [
        ('o-heroi-que-recomecou', {'elixir da juventude', 'tocha'}),
        (
            'alem-do-veu',
            {'pergaminho de teleporte', 'grimorio proibido', 'olho de dragao'},
        ),
        (
            'o-novo-rei-demonio',
            {'foice amaldicoada', 'amuleto sombrio', 'grimorio proibido'},
        ),
        (
            'a-lamina-invisivel',
            {
                'adaga', 'capa das sombras', 'pocao de invisibilidade',
                'veneno paralisante',
            },
        ),
        (
            'arquimago-do-ultimo-portal',
            {'cajado', 'pocao de mana', 'anel de protecao', 'amuleto sombrio'},
        ),
        (
            'a-flecha-antes-da-aurora',
            {'arco', 'flechas', 'mapa antigo', 'flechas de fogo'},
        ),
        (
            'o-bastiao-do-reino',
            {'armadura', 'escudo', 'espada', 'pocao de vida'},
        ),
        (
            'vitoria-do-amanhecer',
            {'espada', 'escudo', 'pocao de vida', 'tocha'},
        ),
        ('vitoria-postuma', {'espada longa', 'pocao de forca'}),
        ('sobrevivente-nao-salvador', {'pergaminho de teleporte'}),
        ('a-batalha-sem-profecia', {'corda', 'botas', 'lanterna'}),
    ],
)
def test_todos_os_desfechos_possuem_cronica_completa(esperado, itens):
    estado = {
        'inventario': [
            {'item': item, 'quantidade': 1}
            for item in itens
        ]
    }
    resultado = resolver_desfecho(estado)
    assert resultado['id'] == esperado
    assert len(resultado['texto']) >= 6
    assert all(len(paragrafo) >= 80 for paragrafo in resultado['texto'])
    assert len(resultado['slides']) == 4
    assert '/static/assets/scenes/endings/' in resultado['slides'][-1]
    asset = ROOT / 'frontend' / resultado['slides'][-1].removeprefix('/static/')
    assert asset.is_file()
