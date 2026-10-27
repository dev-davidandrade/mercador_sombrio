def test_loja_expoe_catalogo_completo_sem_entrega(client):
    resposta = client.get('/api/loja')
    assert resposta.status_code == 200
    dados = resposta.json()
    assert 'destinos' not in dados
    assert len(dados['itens']) == 47
    categorias = {categoria['id'] for categoria in dados['categorias']}
    assert categorias == {
        'armas', 'municoes', 'armaduras', 'pocoes', 'magia', 'utilidades'
    }
    assert {item['categoria'] for item in dados['itens']} == categorias
    assert next(
        item for item in dados['itens'] if item['id'] == 'espada'
    )['preco_centavos'] == 12000
    assert next(
        item for item in dados['itens'] if item['id'] == 'pocao de vida'
    )['preco_centavos'] == 1000
    assert next(
        item for item in dados['itens'] if item['id'] == 'armadura'
    )['nome'] == 'Armadura Pesada'


def test_compra_reduz_ouro_e_persiste_mercadoria_no_inventario(client):
    assert client.get('/api/estado').json()['ouro_centavos'] == 100000
    pedido = {'item': 'Pocao de vida', 'quantidade': 2}
    orcamento = client.post('/api/orcamentos', json=pedido)
    assert orcamento.status_code == 200
    assert orcamento.json()['total_centavos'] == 2000
    assert 'taxa_centavos' not in orcamento.json()

    resposta = client.post('/api/compras', json=pedido)
    assert resposta.status_code == 201
    assert resposta.json()['compra_id'] == 1
    estado = client.get('/api/estado').json()
    assert estado['ouro_centavos'] == 98000
    assert estado['inventario'] == [
        {'item': 'pocao de vida', 'nome': 'Poção de Vida', 'quantidade': 2}
    ]
    assert estado['compras_realizadas'] == 1


def test_nao_compra_sem_ouro_e_nao_altera_estado(client):
    antes = client.get('/api/estado').json()
    resposta = client.post(
        '/api/compras',
        json={'item': 'alma engarrafada', 'quantidade': 4},
    )
    assert resposta.status_code == 409
    assert 'Ouro insuficiente' in resposta.json()['detail']
    assert client.get('/api/estado').json() == antes


def test_preco_enviado_pelo_cliente_e_ignorado(client):
    pedido = {
        'item': 'espada',
        'quantidade': 1,
        'total_centavos': 1,
        'preco_unitario_centavos': 0,
        'frete': 0,
        'destino': 'qualquer lugar',
    }
    resposta = client.post('/api/compras', json=pedido)
    assert resposta.status_code == 201
    assert resposta.json()['orcamento']['total_centavos'] == 12000
    assert resposta.json()['estado']['ouro_centavos'] == 88000


def test_recusa_mercadoria_e_quantidades_invalidas(client):
    casos = [
        ({'item': 'dragao voador', 'quantidade': 1}, 400),
        ({'item': 'espada', 'quantidade': 0}, 422),
        ({'item': 'espada', 'quantidade': -2}, 422),
        ({'item': 'espada', 'quantidade': 1001}, 422),
    ]
    for payload, status in casos:
        resposta = client.post('/api/compras', json=payload)
        assert resposta.status_code == status, (payload, resposta.text)
    assert client.get('/api/estado').json()['ouro_centavos'] == 100000


def test_chat_compra_item_nao_armamento_automaticamente(client):
    resposta = client.post(
        '/api/chat',
        json={'mensagem': 'Quero comprar duas pocoes de vida'},
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados['modo'] == 'demonstracao'
    assert dados['compra_realizada'] is True
    assert dados['estado']['ouro_centavos'] == 98000
    assert dados['estado']['inventario'] == [
        {'item': 'pocao de vida', 'nome': 'Poção de Vida', 'quantidade': 2}
    ]
    assert 'ouros' in dados['fala'].lower()
    assert 'oros' not in dados['fala'].lower()


def test_chat_consulta_e_categoria_nao_compram(client):
    preco = client.post(
        '/api/chat',
        json={'mensagem': 'Quanto custa uma armadura de couro?'},
    )
    assert preco.status_code == 200
    assert preco.json()['compra_realizada'] is False
    assert '70 ouros' in preco.json()['fala']

    categoria = client.post(
        '/api/chat',
        json={'mensagem': 'Quais pocoes voce tem?'},
    )
    assert categoria.status_code == 200
    assert 'Poção de Vida' in categoria.json()['fala']
    assert client.get('/api/estado').json()['compras_realizadas'] == 0


def test_chat_recusa_entrega_sem_remover_catalogo(client):
    resposta = client.post(
        '/api/chat',
        json={'mensagem': 'Voce entrega uma espada no castelo?'},
    )
    dados = resposta.json()
    assert dados['compra_realizada'] is False
    assert 'não faço entregas' in dados['fala'].lower()
    assert dados['estado']['ouro_centavos'] == 100000


def test_chat_recusa_compra_sem_saldo(client):
    resposta = client.post(
        '/api/chat',
        json={'mensagem': 'Quero comprar quatro almas engarrafadas'},
    )
    dados = resposta.json()
    assert dados['compra_realizada'] is False
    assert dados['estado']['ouro_centavos'] == 100000
    assert dados['estado']['inventario'] == []
    assert 'insuficiente' in dados['fala'].lower()


def test_chat_compra_varias_pecas_e_soma_o_total_atomicamente(client):
    resposta = client.post(
        '/api/chat',
        json={
            'mensagem': (
                'Quero comprar armadura pesada, capacete, manoplas e botas'
            )
        },
    )
    dados = resposta.json()
    assert dados['compra_realizada'] is True
    assert dados['estado']['ouro_centavos'] == 70500
    assert {item['item'] for item in dados['estado']['inventario']} == {
        'armadura', 'capacete', 'manoplas', 'botas'
    }
    assert '295 ouros' in dados['fala']


def test_reiniciar_restabelece_dados(client):
    client.post('/api/compras', json={'item': 'tocha', 'quantidade': 2})
    novo = client.post('/api/reiniciar')
    assert novo.status_code == 200
    assert novo.json()['ouro_centavos'] == 100000
    assert novo.json()['inventario'] == []
    assert novo.json()['compras_realizadas'] == 0


def test_modo_basico_e_ferramentas_exclusivas_de_comercio(client):
    status = client.get('/api/saude').json()
    assert status['modo_ia'] == 'demonstracao'
    assert set(status['ferramentas_mcp']) == {
        'listar_mercadorias', 'consultar_item', 'comprar_item'
    }


def test_pagina_e_arquivos_estaticos_sem_entrega(client):
    pagina = client.get('/').text
    assert 'MERCADOR' in pagina
    assert 'EXPLORAR MERCADORIAS' in pagina
    assert 'DESTINO DE ENTREGA' not in pagina.upper()
    assert 'FRETE' not in pagina.upper()
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200


def test_sprite_sheets_de_todas_as_categorias_existem(client):
    for categoria in (
        'armas', 'municoes', 'armaduras', 'pocoes', 'magia', 'utilidades'
    ):
        resposta = client.get(f'/static/assets/items/{categoria}.png')
        assert resposta.status_code == 200
        assert resposta.headers['content-type'] == 'image/png'
        assert len(resposta.content) > 10_000


def test_mercadora_animada_e_chuva_possuem_assets(client):
    pagina = client.get('/').text
    script = client.get('/static/app.js').text
    assert 'id="rainScene"' in pagina
    assert 'mercadora-sombria-sprites-v2.png' in script

    sprite = client.get(
        '/static/assets/merchant/mercadora-sombria-sprites-v2.png'
    )
    assert sprite.status_code == 200
    assert sprite.headers['content-type'] == 'image/png'
    assert len(sprite.content) > 100_000

    for cena in (
        'castelo-remaster-v1.png', 'duelo-final-v1.png',
        'lamina-invisivel-v1.png', 'alem-do-veu-v1.png',
        'amanhecer-v1.png',
    ):
        resposta = client.get(f'/static/assets/scenes/{cena}')
        assert resposta.status_code == 200
        assert resposta.headers['content-type'] == 'image/png'
        assert len(resposta.content) > 100_000


def test_desfecho_generico_cobre_combinacao_nao_especifica(client):
    itens = (
        'tocha', 'corda', 'mochila', 'mapa antigo', 'racao de viagem',
        'lanterna', 'gazua', 'adaga',
    )
    assert client.get('/api/desfecho').status_code == 409
    for item in itens:
        resposta = client.post(
            '/api/compras', json={'item': item, 'quantidade': 1}
        )
        assert resposta.status_code == 201

    estado = client.get('/api/estado').json()
    assert estado['desfecho']['disponivel'] is True
    assert estado['desfecho']['tipos_escolhidos'] == 8
    final = client.get('/api/desfecho').json()
    assert final['id'] == 'a-batalha-sem-profecia'
    assert final['generico'] is True
    assert len(final['slides']) == 4


def test_lamina_invisivel_tem_prioridade_sobre_final_generico(client):
    itens = (
        'adaga', 'capa das sombras', 'pocao de invisibilidade',
        'veneno paralisante', 'tocha', 'corda', 'mapa antigo',
        'racao de viagem',
    )
    for item in itens:
        client.post('/api/compras', json={'item': item, 'quantidade': 1})
    final = client.get('/api/desfecho').json()
    assert final['id'] == 'a-lamina-invisivel'
    assert final['generico'] is False


def test_ouro_esgotado_libera_final_secreto_antes_de_oito_tipos(client):
    client.post(
        '/api/compras',
        json={'item': 'elixir da juventude', 'quantidade': 1},
    )
    client.post('/api/compras', json={'item': 'tocha', 'quantidade': 1})
    estado = client.get('/api/estado').json()
    assert estado['ouro_centavos'] == 0
    assert estado['desfecho']['motivo'] == 'ouro_esgotado'
    final = client.get('/api/desfecho').json()
    assert final['id'] == 'o-heroi-que-recomecou'
