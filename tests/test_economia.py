import pytest
from backend.economia import calcular_orcamento, centavos, RegraDeNegocio


def test_precos_fracionarios_sem_erros_float():
    assert centavos(0.5)==50
    assert centavos(0.8)==80
    o=calcular_orcamento('flechas', 3, 'vila')
    assert o.subtotal_centavos==150
    assert o.total_centavos==650


def test_acentos_sao_normalizados():
    assert calcular_orcamento('Poção de força',1,'Pântano').total_centavos == 7500


def test_booleano_nao_e_quantidade():
    with pytest.raises(RegraDeNegocio):
        calcular_orcamento('espada',True,'vila')
