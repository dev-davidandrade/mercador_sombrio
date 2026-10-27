# Mercador Sombrio

Uma loja RPG completa com interface web, persistência SQLite e um agente conectado por MCP ao Ollama.

## O que a versão 0.5 faz

- Exibe 47 mercadorias com preços oficiais definidos no servidor.
- Organiza o catálogo em Armas, Munições, Armaduras, Poções e Venenos, Magia e Raridades, e Utilidades.
- Permite consultar itens, categorias e preços pelo catálogo ou pelo diálogo.
- Entende pedidos claros como “quero comprar duas poções de vida” e executa a compra automaticamente.
- Começa com 1.000 ouros em um banco novo.
- Debita o saldo e inclui a mercadoria no inventário na mesma transação.
- Recusa a compra sem alterar o estado quando não há ouros suficientes.
- Usa um sprite sheet por categoria, com um ícone próprio para cada mercadoria.
- Libera o desfecho com oito tipos de item ou ao esgotar o ouro.
- Resolve combinações especiais em ordem e usa um final genérico obrigatório.
- Exibe o futuro do herói com texto progressivo e slideshow cinematográfico.
- Funciona em modo de demonstração quando a chave do Ollama não estiver configurada.

O Mercador Sombrio vende diretamente no balcão. Não existem entrega, destino ou frete.

## Categorias

| Categoria | Conteúdo |
|---|---|
| Armas | Espadas, adaga, machado, lança, martelo, arco, besta, cajado e foice |
| Munições | Flechas, virotes, facas de arremesso e bombas |
| Armaduras | Escudos, capacete, Armadura Pesada, couro, cota de malha, manoplas, botas e capa |
| Poções e Venenos | Poções, antídoto, venenos e elixir |
| Magia e Raridades | Pergaminho, anel, amuleto, grimório, olho de dragão e alma engarrafada |
| Utilidades | Tocha, corda, mochila, mapa, ração, lanterna e gazua |

## Execução local

Requer Python 3.11 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Abra `http://127.0.0.1:8000`. Em outro dispositivo da mesma rede, use o endereço IPv4 do computador no lugar de `127.0.0.1`.

## Ollama

Crie um arquivo `.env` local, que já é ignorado pelo Git:

```dotenv
OLLAMA_API_KEY=sua_chave
OLLAMA_HOST=https://ollama.com
OLLAMA_MODEL=gemma4:31b
```

A chave nunca deve ser adicionada ao repositório.

O funcionamento completo do modelo, do prompt, dos fallbacks e das ferramentas
está documentado em [`docs/IA_E_MCP.md`](docs/IA_E_MCP.md).

## Fluxo seguro de compra

1. A intenção clara de compra chama a ferramenta MCP `comprar_item`.
2. O servidor normaliza o nome e busca o preço oficial no catálogo.
3. O SQLite abre uma transação e confere o saldo.
4. Com saldo suficiente, debita os ouros e atualiza o inventário.
5. Sem saldo suficiente, desfaz a operação e retorna o estado inalterado.

Uma pergunta de preço ou disponibilidade não realiza compra. Pedidos de entrega são recusados sem iniciar uma compra.

## API

| Método | Caminho | Finalidade |
|---|---|---|
| GET | `/api/saude` | Saúde, modo de IA e ferramentas MCP |
| GET | `/api/loja` | Categorias e mercadorias |
| GET | `/api/estado` | Saldo, inventário e compras |
| GET | `/api/desfecho` | Resolve o futuro do herói quando a preparação termina |
| POST | `/api/orcamentos` | Calcula o preço oficial |
| POST | `/api/compras` | Compra transacional no balcão |
| POST | `/api/chat` | Conversa e compra por linguagem natural |
| POST | `/api/reiniciar` | Reinicia a demonstração |

## Ferramentas MCP

- `listar_mercadorias(categoria="")`
- `consultar_item(nome_item)`
- `comprar_item(nome_item, quantidade=1)`

Nenhuma ferramenta recebe endereço, destino ou taxa de entrega.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --check frontend\app.js
```

Os testes cobrem catálogo e categorias, orçamento, débito, compras múltiplas, inventário, saldo insuficiente, finais específicos e genérico, ausência de entrega, chat em modo de demonstração e integração MCP por stdio.
