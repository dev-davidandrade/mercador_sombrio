import pytest

from backend.economia import RegraDeNegocio, calcular_orcamento, centavos


def test_precos_fracionarios_sem_erros_float_e_sem_frete():
    assert centavos(1.0) == 100
    assert centavos(0.8) == 80
    orcamento = calcular_orcamento('flechas', 3)
    assert orcamento.preco_unitario_centavos == 100
    assert orcamento.subtotal_centavos == 300
    assert orcamento.total_centavos == 300
    assert 'taxa_centavos' not in orcamento.como_dict()


def test_acentos_sao_normalizados():
    assert calcular_orcamento('Pocao de forca', 1).total_centavos == 3500
    assert calcular_orcamento('Foice amaldicoada', 1).total_centavos == 33300


def test_mercadoria_desconhecida_e_recusada():
    with pytest.raises(RegraDeNegocio, match='Mercadoria desconhecida'):
        calcular_orcamento('dragao voador', 1)


def test_booleano_nao_e_quantidade():
    with pytest.raises(RegraDeNegocio):
        calcular_orcamento('espada', True)
