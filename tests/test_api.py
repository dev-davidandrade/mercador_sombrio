def test_loja_reutiliza_catalogo_original(client):
    r=client.get('/api/loja')
    assert r.status_code == 200
    data=r.json()
    assert len(data['itens']) == 47
    assert len(data['destinos']) == 11
    espada=next(i for i in data['itens'] if i['id']=='espada')
    assert espada['preco_centavos']==12000
    flechas=next(i for i in data['itens'] if i['id']=='flechas')
    assert flechas['preco_centavos']==50


def test_compra_reduz_ouro_e_persiste_inventario(client):
    assert client.get('/api/estado').json()['ouro_centavos'] == 100000
    pedido={'item':'Poção de Vida', 'quantidade':2,'local':'Vila'}
    orc=client.post('/api/orcamentos',json=pedido)
    assert orc.status_code == 200
    assert orc.json()['total_centavos'] == 2500 # 2*10 + 5
    resposta=client.post('/api/compras',json=pedido)
    assert resposta.status_code == 201
    assert resposta.json()['compra_id'] == 1
    novo=client.get('/api/estado').json()
    assert novo['ouro_centavos'] == 97500
    assert novo['inventario'] == [{'item':'pocao de vida','nome':'Poção de Vida','quantidade':2}]
    assert novo['compras_realizadas'] == 1
    client.post('/api/compras',json={'item':'pocao de vida','quantidade':3,'local':'vila'})
    novo=client.get('/api/estado').json()
    assert novo['ouro_centavos'] == 94000
    assert novo['inventario'][0]['quantidade']==5


def test_nao_comprar_sem_ouro_e_nao_altera_estado(client):
    antes=client.get('/api/estado').json()
    r=client.post('/api/compras',json={'item':'alma engarrafada','quantidade':1,'local':'vila'})
    assert r.status_code==409
    assert 'Ouro insuficiente' in r.json()['detail']
    assert client.get('/api/estado').json()==antes


def test_nao_aceita_precos_vindos_do_cliente(client):
    pedido={'item':'espada','quantidade':1,'local':'vila','total_centavos':1,'preco_unitario_centavos':0}
    r=client.post('/api/compras',json=pedido)
    assert r.status_code==201
    assert r.json()['orcamento']['total_centavos']==12500
    assert r.json()['estado']['ouro_centavos']==87500


def test_recusa_destino_item_quantidade_invalidos(client):
    cases=[({'item':'dragao voador','quantidade':1,'local':'vila'},400),
           ({'item':'espada','quantidade':1,'local':'lua'},400),
           ({'item':'espada','quantidade':0,'local':'vila'},422),
           ({'item':'espada','quantidade':-2,'local':'vila'},422),
           ({'item':'espada','quantidade':1001,'local':'vila'},422)]
    for payload,status in cases:
        r=client.post('/api/compras',json=payload)
        assert r.status_code==status, (payload,r.text)
    assert client.get('/api/estado').json()['ouro_centavos']==100000


def test_reiniciar_restabelece_dados(client):
    client.post('/api/compras',json={'item':'tocha','quantidade':2,'local':'taverna'})
    novo=client.post('/api/reiniciar')
    assert novo.status_code==200
    assert novo.json()['ouro_centavos']==100000
    assert novo.json()['inventario']==[]
    assert novo.json()['compras_realizadas']==0


def test_modo_basico_identificado(client):
    status=client.get('/api/saude').json()
    assert status['modo_ia']=='demonstracao'
    assert status['ferramentas_mcp']==['listar_loja','consultar_item','consultar_taxa','calcular_total']
    r=client.post('/api/chat',json={'mensagem':'Quanto custa uma poção de vida?'})
    assert r.status_code==200
    assert r.json()['modo']=='demonstracao'
    assert '10,00' in r.json()['fala']


def test_pagina_e_js_existem(client):
    assert 'MERCADOR' in client.get('/').text
    assert client.get('/static/app.js').status_code==200
    assert client.get('/static/style.css').status_code==200
