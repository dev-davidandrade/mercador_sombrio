"""Regras determinísticas para o destino do aventureiro.

As combinações especiais são avaliadas em ordem. A última regra é sempre um
desfecho genérico, portanto uma preparação válida nunca fica sem história.
"""

LIMITE_TIPOS = 8

CASTELO = "/static/assets/scenes/castelo-remaster-v1.png"
DUELO = "/static/assets/scenes/duelo-final-v1.png"
LAMINA = "/static/assets/scenes/lamina-invisivel-v1.png"
PORTAL = "/static/assets/scenes/alem-do-veu-v1.png"
AMANHECER = "/static/assets/scenes/amanhecer-v1.png"

ULTIMO_MENINO = "/static/assets/scenes/endings/ultimo-menino-v1.png"
ASCENSAO_VEU = "/static/assets/scenes/endings/ascensao-veu-v1.png"
NOVO_REI = "/static/assets/scenes/endings/novo-rei-demonio-v1.png"
HEROI_DESCONHECIDO = "/static/assets/scenes/endings/heroi-desconhecido-v1.png"
GUARDIAO_PORTAL = "/static/assets/scenes/endings/guardiao-portal-v1.png"
ARQUEIRO_REINO = "/static/assets/scenes/endings/arqueiro-reino-v1.png"
BASTIAO_REINO = "/static/assets/scenes/endings/bastiao-reino-v1.png"
VITORIA_RECONHECIDA = "/static/assets/scenes/endings/vitoria-amanhecer-reino-v1.png"
MEMORIAL_HEROI = "/static/assets/scenes/endings/memorial-heroi-v1.png"
SOBREVIVENTE_RUINAS = "/static/assets/scenes/endings/sobrevivente-ruinas-v1.png"
BATALHA_SEM_PROFECIA = "/static/assets/scenes/endings/batalha-sem-profecia-v1.png"


def progresso_desfecho(inventario: list[dict], ouro_centavos: int) -> dict:
    tipos = len({
        item["item"]
        for item in inventario
        if item.get("quantidade", 0) > 0
    })
    por_itens = tipos >= LIMITE_TIPOS
    por_ouro = ouro_centavos == 0
    return {
        "disponivel": por_itens or por_ouro,
        "tipos_escolhidos": tipos,
        "limite_tipos": LIMITE_TIPOS,
        "motivo": (
            "limite_itens" if por_itens
            else "ouro_esgotado" if por_ouro
            else None
        ),
    }


def _final(
    identificador: str,
    titulo: str,
    subtitulo: str,
    texto: list[str],
    slides: list[str],
    tom: str,
    *,
    generico: bool = False,
) -> dict:
    return {
        "id": identificador,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "texto": texto,
        "slides": slides,
        "tom": tom,
        "generico": generico,
    }


def resolver_desfecho(estado: dict) -> dict:
    itens = {
        item["item"]
        for item in estado.get("inventario", [])
        if item.get("quantidade", 0) > 0
    }

    if itens == {"elixir da juventude", "flechas"}:
        return _final(
            "o-ultimo-menino",
            "O Último Menino",
            "Ele venceu o Rei Demônio. Depois, sobreviveu a tudo.",
            [
                "O herói entregou novecentos e noventa e nove ouros pelo Elixir da Juventude. Com a única moeda restante, comprou as flechas mais simples do balcão. Ninguém compreendeu aquela escolha; talvez nem mesmo ele, até beber o frasco diante dos portões do castelo.",
                "As cicatrizes desapareceram, os anos recuaram e a armadura tornou-se grande demais. O processo só parou quando restou um garoto de olhos antigos, pequeno demais para a espada e incapaz de envelhecer, adoecer ou conservar qualquer ferimento.",
                "O Rei Demônio atravessou seu coração, queimou seus ossos e o lançou das muralhas. O menino voltou todas as vezes. Quando já não possuía força para erguer a lâmina, usou a última flecha; não para matar, mas para partir a joia que tornava o soberano invencível.",
                "O reino foi salvo e celebrou o jovem herói. Anos depois, os primeiros amigos morreram. Depois partiram seus filhos, seus netos e as dinastias que aprenderam a contar aquela vitória como lenda. O menino permaneceu exatamente igual.",
                "Ele viu o castelo virar ruína, novos impérios ocuparem o mundo e os mares cobrirem todos os seus nomes. Quando o sol escureceu e as estrelas começaram a desaparecer, ainda carregava o frasco vazio e o arco apodrecido de sua primeira jornada.",
                "No fim, a última luz do universo se apagou diante dele. Tudo conheceu a morte — reis, demônios, deuses e o próprio tempo. Tudo, menos o garoto. Sem ninguém para recordar sua vitória, o Último Menino continuou caminhando pelo escuro.",
            ],
            [CASTELO, DUELO, AMANHECER, ULTIMO_MENINO],
            "segredo",
        )

    if {
        "pergaminho de teleporte", "grimorio proibido", "olho de dragao"
    }.issubset(itens):
        return _final(
            "alem-do-veu",
            "Além do Véu",
            "O portal não levava a um lugar. Levava a algo.",
            [
                "O Olho de Dragão despertou assim que o herói cruzou os portões. Em sua pupila de cristal apareceram runas escondidas nas muralhas, linhas de uma prisão muito mais antiga que o próprio castelo.",
                "Diante do trono, o Grimório Proibido abriu-se sozinho. Suas páginas não ensinavam um feitiço de ataque, mas o verdadeiro nome do espaço entre os mundos. O Pergaminho de Teleporte queimou nas mãos do herói e rasgou o céu do salão.",
                "O Rei Demônio tentou fechar a passagem. Pela primeira vez em séculos, houve medo em seus olhos. Ele sabia que o portal não conduzia a outro reino, mas a uma camada da existência onde matéria, tempo e identidade eram apenas sugestões.",
                "Do outro lado surgiu o Vazio Coroado: uma consciência anterior a reis, deuses e demônios. Não possuía corpo; era um plano inteiro pensando através de uma coroa feita de estrelas mortas.",
                "A criatura apagou o Rei Demônio como tinta sob a chuva. Depois voltou sua atenção ao aventureiro, não como quem observa uma presa, mas como quem finalmente encontra alguém capaz de atravessar o Véu sem desaparecer.",
                "O herói ascendeu ao plano imaterial e tornou-se seu primeiro emissário humano. O reino chamou aquilo de vitória. Os sábios chamaram de transcendência. As estrelas, desde aquela noite, passaram a sussurrar seu nome.",
            ],
            [CASTELO, DUELO, PORTAL, ASCENSAO_VEU],
            "cosmico",
        )

    corrupcao = itens & {
        "amuleto sombrio", "grimorio proibido", "alma engarrafada"
    }
    if "foice amaldicoada" in itens and len(corrupcao) >= 2:
        return _final(
            "o-novo-rei-demonio",
            "O Novo Rei Demônio",
            "A coroa caiu. Alguém precisava erguê-la.",
            [
                "A Foice Amaldiçoada começou a sussurrar antes que o castelo surgisse no horizonte. Cada artefato sombrio dentro da bolsa respondia com a mesma promessa: poder suficiente para vencer, desde que o herói aceitasse carregá-lo para sempre.",
                "No salão do trono, a lâmina bebeu magia, memórias e medo. O Rei Demônio reconheceu a própria escuridão refletida no aventureiro e sorriu, certo de que já havia vencido mesmo antes do primeiro golpe.",
                "O combate foi breve e brutal. A foice atravessou a armadura demoníaca e arrancou do inimigo não apenas a vida, mas também o vínculo que mantinha seus exércitos obedientes.",
                "Quando a coroa caiu, os artefatos exigiram o pagamento. A essência do antigo soberano encontrou abrigo no coração daquele que o derrotara, misturando ambição humana e fome demoníaca até não existir fronteira entre ambas.",
                "O exército do reino chegou esperando encontrar um salvador. Encontrou os demônios ajoelhados e o herói sentado no trono, os olhos iluminados pela mesma chama violeta que antes pertencera ao inimigo.",
                "A guerra terminou, mas nenhuma bandeira de vitória foi erguida. O mundo não fora libertado; apenas ganhara um novo Rei Demônio, mais jovem, mais inteligente e perigosamente convencido de que governaria melhor.",
            ],
            [CASTELO, DUELO, PORTAL, NOVO_REI],
            "corrupcao",
        )

    if {
        "adaga", "capa das sombras", "pocao de invisibilidade",
        "veneno paralisante",
    }.issubset(itens):
        return _final(
            "a-lamina-invisivel",
            "A Lâmina Invisível",
            "A batalha terminou antes que alguém a visse começar.",
            [
                "O herói não marchou contra os portões. Esperou a tempestade cobrir a lua, bebeu a Poção de Invisibilidade e permitiu que a Capa das Sombras apagasse até mesmo o som de seus passos.",
                "Passou entre sentinelas, atravessou corredores ocupados por generais demoníacos e alcançou o salão do trono enquanto o inimigo ainda ensaiava o discurso que faria antes do grande duelo.",
                "Uma gota de Veneno Paralisante tocou a adaga. O Rei Demônio percebeu tarde demais que o frio em seu pescoço não vinha da chuva. Sua voz desapareceu antes que pudesse ordenar o fechamento das portas.",
                "A lâmina encontrou o coração e a batalha terminou sem clarins, testemunhas ou choque de exércitos. Quando os guardas entraram, encontraram apenas a coroa caída e uma janela aberta para a noite.",
                "Ao amanhecer, generais e nobres disputaram o direito de declarar a vitória. Estátuas foram erguidas para homens que jamais haviam entrado no castelo, enquanto o verdadeiro salvador caminhava por uma estrada sem aplausos.",
                "Nenhum bardo conheceu seu rosto ou seu nome. Ainda assim, em tavernas silenciosas, dizia-se que uma sombra havia salvado o mundo — e que ela continuava viajando, satisfeita por saber que ninguém mais precisaria fazê-lo.",
            ],
            [CASTELO, LAMINA, AMANHECER, HEROI_DESCONHECIDO],
            "sombras",
        )

    arcano = itens & {"grimorio proibido", "olho de dragao", "amuleto sombrio"}
    if {
        "cajado", "pocao de mana", "anel de protecao"
    }.issubset(itens) and arcano:
        return _final(
            "arquimago-do-ultimo-portal",
            "Arquimago do Último Portal",
            "Nem toda vitória exige a morte do inimigo.",
            [
                "O herói entrou no castelo contando cada passo. O cajado marcava o chão com runas quase invisíveis, e o Anel de Proteção absorvia as maldições lançadas das torres.",
                "Quando o duelo começou, o objetivo nunca foi matar. Cada feitiço desviava o Rei Demônio para uma posição determinada, construindo ao redor dele um círculo de contenção do tamanho do salão do trono.",
                "O inimigo percebeu a armadilha e rompeu três camadas do selo. O herói bebeu a Poção de Mana, abriu o artefato arcano e ofereceu ao círculo tudo o que ainda possuía de força e memória.",
                "As portas do último portal se fecharam sobre o soberano demoníaco. Sua espada ficou presa a poucos centímetros do peito do aventureiro, imóvel como uma relíquia dentro de vidro escuro.",
                "O reino foi salvo sem que a essência do inimigo escapasse para escolher um sucessor. Contudo, o selo precisava de uma consciência desperta para continuar existindo.",
                "O herói tornou-se o Arquimago do Último Portal. Viveu além de reis e dinastias, vigiando a prisão e ensinando novos guardiões a reconhecer o som de uma corrente mágica começando a se partir.",
            ],
            [CASTELO, DUELO, PORTAL, GUARDIAO_PORTAL],
            "arcano",
        )

    arqueiro = (
        {"arco", "flechas"}.issubset(itens)
        or {"besta", "virotes"}.issubset(itens)
    )
    if arqueiro and "mapa antigo" in itens and itens & {
        "flechas de fogo", "bomba", "facas de arremesso"
    }:
        return _final(
            "a-flecha-antes-da-aurora",
            "A Flecha Antes da Aurora",
            "A distância também pode ser coragem.",
            [
                "O Mapa Antigo mostrava uma torre que já não aparecia em nenhuma planta do castelo. Para alcançá-la, o herói atravessou muralhas quebradas, subiu escadas sem corrimão e avançou acima das nuvens da tempestade.",
                "Do alto, observou o salão do trono através de uma abertura estreita. Preparou a munição, calculou a força do vento e aguardou enquanto bombas e projéteis incendiários desviavam a atenção dos guardas.",
                "O Rei Demônio surgiu na varanda para ordenar o ataque final ao reino. A distância era absurda; qualquer arqueiro sensato teria recusado o disparo.",
                "O herói respirou uma vez e soltou a corda. Quando o soberano ergueu a arma, o projétil já atravessava a tempestade, guiado pelo relâmpago e pela única rota que o mapa prometera.",
                "A flecha atingiu a fenda da armadura. Sem seu mestre, os exércitos demoníacos se dispersaram antes de alcançar as primeiras muralhas humanas.",
                "Ao amanhecer, o herói desceu da torre e encontrou uma multidão esperando. O reino aprendeu o nome daquele que venceu uma guerra sem permitir que ela chegasse perto o bastante para começar.",
            ],
            [CASTELO, DUELO, AMANHECER, ARQUEIRO_REINO],
            "vitoria",
        )

    armas_normais = itens & {
        "espada", "espada longa", "adaga", "machado", "lanca",
        "martelo de guerra", "arco", "besta", "cajado",
    }
    armadura_pesada = itens & {"armadura", "cota de malha"}
    escudos = itens & {"escudo", "escudo de torre"}
    if armadura_pesada and escudos and armas_normais and "pocao de vida" in itens:
        return _final(
            "o-bastiao-do-reino",
            "O Bastião do Reino",
            "O golpe que não derruba apenas fortalece.",
            [
                "O herói atravessou os portões sem tentar esconder sua presença. Cada passo da Armadura Pesada ecoava pelos corredores, chamando para si soldados que, de outro modo, marchariam contra o reino.",
                "O Escudo de Torre recebeu flechas, fogo e golpes capazes de partir colunas. Atrás dele, o aventureiro avançou lentamente, usando poções para manter o corpo de pé quando os músculos já imploravam por descanso.",
                "No salão do trono, o Rei Demônio riu daquela estratégia. Esperava velocidade, magia ou algum artefato lendário; encontrou apenas alguém disposto a suportar um golpe a mais do que qualquer criatura deveria suportar.",
                "A armadura gemeu sob cada impacto, mas o escudo jamais deixou o herói tocar o chão. O duelo atravessou a noite, destruindo degraus, pilares e a própria base do trono.",
                "Quando o inimigo finalmente hesitou, exausto, encontrou aço onde esperava fraqueza. A espada longa atravessou a abertura criada por milhares de golpes defendidos pacientemente.",
                "Coberto de cicatrizes, o vencedor voltou ao reino sob o sol da manhã. Não aceitou coroa nem terras; permaneceu nas muralhas como o Bastião vivo que nenhum novo tirano ousaria enfrentar.",
            ],
            [CASTELO, DUELO, AMANHECER, BASTIAO_REINO],
            "vitoria",
        )

    protecao = itens & {
        "escudo", "escudo de torre", "armadura", "armadura de couro",
        "cota de malha", "anel de protecao",
    }
    cura = itens & {"pocao de vida", "antidoto"}
    utilidade = itens & {
        "tocha", "corda", "mochila", "mapa antigo", "racao de viagem",
        "lanterna", "gazua",
    }
    if armas_normais and protecao and cura and utilidade:
        return _final(
            "vitoria-do-amanhecer",
            "Vitória do Amanhecer",
            "Preparação, coragem e um reino salvo.",
            [
                "A jornada começou muito antes do castelo. O mapa evitou estradas dominadas por demônios, as provisões mantiveram o herói em movimento e cada pequena utilidade comprada no bazar encontrou uma função inesperada.",
                "As defesas abriram caminho pelas muralhas. A cura permitiu atravessar as armadilhas e a arma escolhida respondeu sempre que uma criatura tentou transformar a preparação em medo.",
                "O Rei Demônio ofereceu poder, riqueza e um lugar ao seu lado. O herói recusou sem discurso grandioso; havia chegado longe demais para negociar a vida das pessoas que esperavam além das montanhas.",
                "O duelo foi equilibrado. Defesa e ataque se alternaram até que uma poção, uma peça de armadura e um último movimento calculado criaram a oportunidade que nenhuma profecia conseguiria garantir.",
                "Com a queda do soberano, as nuvens se abriram e os exércitos demoníacos perderam a vontade de lutar. Pela primeira vez em muitos anos, o sol alcançou as estradas ao redor do castelo.",
                "O herói retornou ao reino por uma avenida coberta de flores e bandeiras. Seu nome foi gravado nos portões, mas sua maior recompensa foi ouvir crianças brincando de aventura num mundo que finalmente poderia ter um amanhã.",
            ],
            [CASTELO, DUELO, AMANHECER, VITORIA_RECONHECIDA],
            "vitoria",
        )

    ofensiva_pesada = itens & {
        "espada longa", "machado", "martelo de guerra", "foice amaldicoada"
    }
    if (
        ofensiva_pesada
        and "pocao de forca" in itens
        and not protecao
        and "pocao de vida" not in itens
    ):
        return _final(
            "vitoria-postuma",
            "Vitória Póstuma",
            "O reino viveu. Seu herói, não.",
            [
                "Sem escudo, proteção ou cura suficiente, o herói sabia que não sobreviveria a uma batalha prolongada. Guardou a Poção de Força para o instante em que recuar deixasse de ser uma possibilidade.",
                "O Rei Demônio percebeu a fragilidade daquela preparação e atacou sem cautela. Cada ferimento aproximava o aventureiro da morte, mas também convencia o inimigo de que a vitória já estava garantida.",
                "Quando o soberano ergueu a arma para o golpe final, o herói bebeu a poção. Toda a dor transformou-se em força suficiente para sustentar um único ataque impossível.",
                "A lâmina partiu a coroa, atravessou a armadura e alcançou o coração demoníaco. No mesmo instante, a resposta do inimigo encontrou um corpo sem proteção para detê-la.",
                "Duas figuras tombaram diante do trono. Horas depois, os soldados do reino encontraram o herói ainda segurando a arma, como se recusasse permitir que o adversário se levantasse outra vez.",
                "A vitória foi celebrada em silêncio. Uma estátua foi erguida voltada para o castelo, e todos os anos o reino deixava diante dela uma poção de vida — o presente que chegara tarde demais.",
            ],
            [CASTELO, DUELO, AMANHECER, MEMORIAL_HEROI],
            "sacrificio",
        )

    fuga = itens & {
        "pergaminho de teleporte", "pocao de invisibilidade", "bomba de fumaca"
    }
    if fuga and not armas_normais and "foice amaldicoada" not in itens:
        return _final(
            "sobrevivente-nao-salvador",
            "Sobrevivente, Não Salvador",
            "Viver também pode deixar cicatrizes.",
            [
                "O herói alcançou o salão do trono evitando patrulhas e fechando portas atrás de si. Até aquele momento, astúcia parecera suficiente para substituir armas e proteção.",
                "Diante do Rei Demônio, porém, todas as pequenas vantagens perderam o significado. A bolsa continha rotas de fuga, fumaça e invisibilidade, mas nada capaz de encerrar aquela guerra.",
                "O primeiro golpe destruiu o chão onde o aventureiro estava. O segundo deixou claro que coragem sem preparação apenas ofereceria ao inimigo mais um cadáver.",
                "As sombras esconderam sua retirada. Um pergaminho, uma poção ou uma nuvem de fumaça abriu a distância necessária para escapar enquanto o castelo engolia os últimos defensores humanos.",
                "O herói sobreviveu, mas viu de longe as luzes do reino se apagarem uma a uma. Ninguém o chamou de covarde; quase ninguém restara para pronunciar qualquer julgamento.",
                "Durante anos, ele contou a história e estudou cada escolha feita no bazar. Em seus sonhos, a estrada sempre retornava àquela noite, oferecendo uma pergunta cruel: o que teria acontecido se tivesse escolhido diferente?",
            ],
            [CASTELO, DUELO, AMANHECER, SOBREVIVENTE_RUINAS],
            "derrota",
        )

    # Regra final obrigatória: qualquer combinação válida chega aqui.
    return _final(
        "a-batalha-sem-profecia",
        "A Batalha sem Profecia",
        "Nenhuma lenda previu aquelas escolhas.",
        [
            "O herói chegou ao castelo com uma coleção improvável de armas, provisões e pequenos objetos que nenhum estrategista colocaria no mesmo plano de batalha.",
            "As primeiras horas pareceram confirmar o erro. Faltava proteção quando surgiam lâminas, faltava alcance quando os inimigos voavam e sobravam ferramentas cuja utilidade ninguém conseguia explicar.",
            "Ainda assim, cada fracasso produziu uma ideia. Uma corda virou armadilha, uma lanterna revelou inscrições escondidas e um item aparentemente inútil comprou os segundos necessários para atravessar uma sala condenada.",
            "O Rei Demônio zombou daquela preparação desordenada. Sua certeza durou até perceber que o aventureiro não repetia movimento algum e transformava cada destroço do salão em uma nova arma.",
            "O golpe decisivo não foi elegante nem profetizado. Nasceu de tudo que dera errado: uma distração, um passo desesperado e a recusa absoluta de permanecer no chão.",
            "Quando o soberano caiu, os sábios procuraram durante meses uma explicação para a vitória. Nunca encontraram. O reino acabou celebrando uma verdade mais simples: às vezes o destino pertence justamente a quem não cabe em nenhuma profecia.",
        ],
        [CASTELO, DUELO, AMANHECER, BATALHA_SEM_PROFECIA],
        "generico",
        generico=True,
    )
