# Arquitetura do Mercador Sombrio

## Visão geral

```text
Navegador
  ├── catálogo com 47 mercadorias
  ├── bolsa e saldo
  ├── botão de destino e slideshow final
  └── diálogo
         │ HTTP/JSON
         ▼
FastAPI
  ├── catálogo e orçamento
  ├── compra transacional no balcão
  ├── estado do jogador
  ├── resolvedor determinístico de desfechos
  └── agente Ollama
         │ MCP por stdio
         ▼
Mercador Sombrio
  ├── listar_mercadorias
  ├── consultar_item
  └── comprar_item
         │
         ▼
SQLite
  ├── saldo
  ├── inventário
  └── histórico de compras
```

## Fonte única do catálogo

`backend/catalogo.py` contém 47 mercadorias, preços e a relação entre item e categoria. O frontend recebe esses dados de `GET /api/loja`; não mantém preços próprios.

As categorias são:

- Armas
- Munições
- Armaduras
- Poções e Venenos
- Magia e Raridades
- Utilidades

Cada mercadoria pertence exatamente a uma categoria.

## Compra

A compra pode começar no botão do catálogo, em `POST /api/compras`, ou por uma intenção clara no chat. Em todos os casos o servidor:

1. normaliza o nome da mercadoria;
2. rejeita itens que não pertencem ao catálogo;
3. recalcula o preço a partir da fonte oficial;
4. abre uma transação SQLite;
5. verifica o saldo;
6. debita e adiciona ao inventário de forma atômica.

Se o saldo for insuficiente, a transação não debita nem adiciona itens.

Pedidos locais com várias mercadorias são calculados e debitados numa única
transação. Ou todas entram no inventário, ou nenhuma delas é cobrada.

## Desfechos

`backend/desfechos.py` libera o resultado quando o jogador possui oito tipos
distintos de mercadoria ou zera o saldo. Combinações especiais são avaliadas
em ordem. A última regra é sempre `A Batalha sem Profecia`, garantindo que
qualquer preparação válida produza uma história.

`GET /api/desfecho` valida novamente o progresso no servidor e devolve título,
texto, tom e cenas. O frontend apenas apresenta esse resultado com slideshow e
texto progressivo; ele não decide qual final o jogador recebeu.

## Venda no balcão

O projeto não possui ferramentas, campos ou cálculos de entrega. Destino e frete não fazem parte da API. Se o usuário pedir entrega no diálogo, o mercador explica que as vendas acontecem somente no balcão e não executa compra.

As colunas internas `local` e `taxa_centavos` da tabela histórica são preservadas apenas para compatibilidade com bancos SQLite criados pela versão anterior. Novas compras gravam `balcao` e taxa zero; esses campos não são expostos ao cliente.

## Agente e MCP

O agente possui uma lista fechada com três ferramentas permitidas: `listar_mercadorias`, `consultar_item` e `comprar_item`. O prompt determina que perguntas não sejam confundidas com compras e que somente o retorno confirmado da ferramenta autorize afirmar que uma venda ocorreu.

Sem `OLLAMA_API_KEY`, o interpretador local mantém as mesmas regras essenciais para demonstração e testes.

## Persistência

`backend/banco.py` usa SQLite. Um banco novo começa com 100.000 centésimos, equivalentes a 1.000 ouros. Valores monetários são inteiros em centésimos para evitar erros de ponto flutuante.

## Segurança

- A chave do Ollama fica apenas no `.env` ignorado.
- Preços enviados pelo cliente são ignorados.
- A IA não escreve diretamente no banco.
- A compra é validada e executada pela camada de domínio.
- O histórico enviado ao modelo é limitado.
