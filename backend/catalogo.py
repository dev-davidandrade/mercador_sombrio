"""Fonte única dos preços e destinos do Mercador Sombrio.

Catálogo extraído do servidor MCP original; valores fictícios em moedas de ouro.
"""
import unicodedata

LOJA = {
    # Armas
    'espada': 120.0, 'espada longa': 180.0, 'adaga': 40.0, 'machado': 140.0,
    'lanca': 95.0, 'martelo de guerra': 210.0, 'arco': 90.0, 'besta': 150.0,
    'cajado': 110.0, 'foice amaldicoada': 666.0,
    # Munição e arremessáveis
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
    'amuleto sombrio': 400.0, 'grimorio proibido': 1200.0,
    'olho de dragao': 1500.0, 'alma engarrafada': 2000.0,
    # Utilidades de aventura
    'tocha': 1.0, 'corda': 3.0, 'mochila': 12.0, 'mapa antigo': 45.0,
    'racao de viagem': 2.0, 'lanterna': 8.0, 'gazua': 18.0,
}

TAXAS = {
    'vila': 5.0, 'taverna': 3.0, 'floresta': 15.0, 'porto': 12.0,
    'castelo': 20.0, 'masmorra': 80.0, 'pantano': 40.0,
    'montanha gelada': 120.0, 'ruinas antigas': 150.0,
    'covil do dragao': 350.0, 'castelo do rei demonio': 500.0,
}

def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, com espaços externos removidos."""
    texto = texto.strip().lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

CATEGORIAS = {
    'armas': ['espada','espada longa','adaga','machado','lanca','martelo de guerra','arco','besta','cajado','foice amaldicoada'],
    'municoes': ['flechas','flechas de fogo','virotes','facas de arremesso','bomba','bomba de fumaca'],
    'armaduras': ['escudo','escudo de torre','capacete','espaldeiras','armadura','armadura de couro','cota de malha','manoplas','botas','capa das sombras'],
    'pocoes': ['pocao de vida','pocao de mana','pocao de forca','pocao de invisibilidade','antidoto','veneno','veneno paralisante','elixir da juventude'],
    'magia': ['pergaminho de teleporte','anel de protecao','amuleto sombrio','grimorio proibido','olho de dragao','alma engarrafada'],
    'utilidades': ['tocha','corda','mochila','mapa antigo','racao de viagem','lanterna','gazua'],
}
CATEGORIA_POR_ITEM = {nome: categoria for categoria, nomes in CATEGORIAS.items() for nome in nomes}

def nome_bonito(nome: str) -> str:
    correcoes = {'pocao': 'Poção', 'pocoes': 'Poções', 'lanca': 'Lança', 'fumaca': 'Fumaça', 'amaldicoada': 'Amaldiçoada', 'antidoto': 'Antídoto', 'protecao': 'Proteção', 'grimorio': 'Grimório', 'dragao': 'Dragão', 'racao': 'Ração', 'gazua': 'Gazua', 'de': 'de', 'do': 'do', 'da': 'da', 'das': 'das', 'dos': 'dos', 'pantano': 'Pântano', 'ruinas': 'Ruínas'}
    return ' '.join(correcoes.get(p, p.capitalize()) for p in nome.split())
