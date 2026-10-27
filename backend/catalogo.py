"""Catálogo completo do Mercador Sombrio, sem serviço de entrega.

Os preços são fictícios e expressos em ouros. O backend converte os valores
para centésimos antes de qualquer débito.
"""
import unicodedata

LOJA = {
    # Armas
    'espada': 120.0, 'espada longa': 180.0, 'adaga': 40.0, 'machado': 140.0,
    'lanca': 95.0, 'martelo de guerra': 210.0, 'arco': 90.0, 'besta': 150.0,
    'cajado': 110.0, 'foice amaldicoada': 333.0,
    # Munições e arremessáveis
    'flechas': 0.5, 'flechas de fogo': 2.0, 'virotes': 0.8,
    'facas de arremesso': 6.0, 'bomba': 5.0, 'bomba de fumaca': 8.0,
    # Armaduras e equipamentos
    'escudo': 80.0, 'escudo de torre': 160.0, 'capacete': 50.0,
    'espaldeiras': 15.0, 'armadura': 200.0, 'armadura de couro': 70.0,
    'cota de malha': 130.0, 'manoplas': 25.0, 'botas': 20.0,
    'capa das sombras': 300.0,
    # Poções e venenos
    'pocao de vida': 10.0, 'pocao de mana': 12.0, 'pocao de forca': 35.0,
    'pocao de invisibilidade': 90.0, 'antidoto': 15.0, 'veneno': 50.0,
    'veneno paralisante': 85.0, 'elixir da juventude': 999.0,
    # Itens mágicos e raros
    'pergaminho de teleporte': 60.0, 'anel de protecao': 250.0,
    'amuleto sombrio': 220.0, 'grimorio proibido': 260.0,
    'olho de dragao': 310.0, 'alma engarrafada': 300.0,
    # Utilidades de aventura
    'tocha': 1.0, 'corda': 3.0, 'mochila': 12.0, 'mapa antigo': 45.0,
    'racao de viagem': 2.0, 'lanterna': 8.0, 'gazua': 18.0,
}

CATEGORIAS = {
    'armas': [
        'espada', 'espada longa', 'adaga', 'machado', 'lanca',
        'martelo de guerra', 'arco', 'besta', 'cajado', 'foice amaldicoada',
    ],
    'municoes': [
        'flechas', 'flechas de fogo', 'virotes', 'facas de arremesso',
        'bomba', 'bomba de fumaca',
    ],
    'armaduras': [
        'escudo', 'escudo de torre', 'capacete', 'espaldeiras', 'armadura',
        'armadura de couro', 'cota de malha', 'manoplas', 'botas',
        'capa das sombras',
    ],
    'pocoes': [
        'pocao de vida', 'pocao de mana', 'pocao de forca',
        'pocao de invisibilidade', 'antidoto', 'veneno',
        'veneno paralisante', 'elixir da juventude',
    ],
    'magia': [
        'pergaminho de teleporte', 'anel de protecao', 'amuleto sombrio',
        'grimorio proibido', 'olho de dragao', 'alma engarrafada',
    ],
    'utilidades': [
        'tocha', 'corda', 'mochila', 'mapa antigo', 'racao de viagem',
        'lanterna', 'gazua',
    ],
}

NOMES_CATEGORIAS = {
    'armas': 'Armas',
    'municoes': 'Munições',
    'armaduras': 'Armaduras',
    'pocoes': 'Poções e Venenos',
    'magia': 'Magia e Raridades',
    'utilidades': 'Utilidades',
}

CATEGORIA_POR_ITEM = {
    nome: categoria
    for categoria, nomes in CATEGORIAS.items()
    for nome in nomes
}

assert set(CATEGORIA_POR_ITEM) == set(LOJA), 'Todo item deve pertencer a uma categoria'


def normalizar(texto: str) -> str:
    texto = " ".join(texto.strip().lower().split())
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    )


def nome_bonito(nome: str) -> str:
    nomes_completos = {
        'armadura': 'Armadura Pesada',
    }
    if nome in nomes_completos:
        return nomes_completos[nome]
    correcoes = {
        'pocao': 'Poção', 'pocoes': 'Poções', 'lanca': 'Lança', 'forca': 'Força',
        'fumaca': 'Fumaça', 'amaldicoada': 'Amaldiçoada',
        'antidoto': 'Antídoto', 'protecao': 'Proteção',
        'grimorio': 'Grimório', 'dragao': 'Dragão', 'racao': 'Ração',
        'de': 'de', 'do': 'do', 'da': 'da', 'das': 'das', 'dos': 'dos',
    }
    return ' '.join(
        correcoes.get(parte, parte.capitalize())
        for parte in nome.split()
    )
