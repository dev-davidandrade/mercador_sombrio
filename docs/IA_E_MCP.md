# IA, respostas e ferramentas MCP

Este documento explica onde o modelo de linguagem é configurado, como uma
mensagem percorre o sistema e quais partes podem ou não alterar o jogo.

## Mapa dos arquivos

| Responsabilidade | Arquivo |
|---|---|
| Endpoint de chat e modelos de entrada HTTP | `backend/main.py` |
| Prompt, cliente Ollama, orquestração MCP e fallback | `backend/agente.py` |
| Definição das ferramentas MCP | `backend/servidor_sombrio.py` |
| Itens, categorias, nomes e preços oficiais | `backend/catalogo.py` |
| Cálculo e validação de orçamento | `backend/economia.py` |
| Saldo, inventário e transações SQLite | `backend/banco.py` |
| Configuração local de exemplo | `.env.example` |

## Qual modelo responde

O modelo não fica gravado no código da interface. Ele é selecionado pela
variável `OLLAMA_MODEL` do arquivo `.env` local:

```dotenv
OLLAMA_HOST=https://ollama.com
OLLAMA_API_KEY=sua_chave_local
OLLAMA_MODEL=gemma4:31b
```

`gemma4:31b` é o padrão atual quando `OLLAMA_MODEL` não é informado. Para uma
instância local do Ollama, use por exemplo:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Hosts locais não exigem chave. No Ollama Cloud, sem `OLLAMA_API_KEY`, o projeto
entra em modo de demonstração e não envia mensagens a um LLM.

O método `modo_ia()` em `backend/agente.py` decide entre:

- `ollama`: existe uma instância local ou uma chave para o host remoto;
- `demonstracao`: não existe credencial para o host remoto.

## Como o mercador aprende a responder

A constante `REGRA`, em `backend/agente.py`, é o prompt de sistema. Ela define:

- a personalidade teatral e enigmática do Mercador Sombrio;
- português brasileiro e respostas de até três parágrafos;
- as categorias permitidas e a proibição de inventar preços ou itens;
- venda somente no balcão, sem entrega, endereço ou frete;
- quando consultar, listar ou comprar;
- que perguntas de preço não são intenção de compra;
- que uma venda só pode ser afirmada depois de `sucesso=true`;
- o uso obrigatório de `ouros`, nunca `oros`.

Depois do prompt, o agente envia no máximo as dez entradas mais recentes do
histórico. Cada entrada é limitada a 1.800 caracteres. A mensagem atual é
acrescentada por último.

O cliente Ollama usa atualmente `temperature=0.1` para manter respostas
consistentes e `num_predict=450` para limitar o tamanho da geração.

## Caminho de uma mensagem

```text
Navegador
  │ POST /api/chat
  ▼
FastAPI: backend/main.py
  │ agente.responder(mensagem, histórico)
  ▼
Agente: backend/agente.py
  ├── modo demonstração: interpretador determinístico local
  └── modo Ollama
        │ inicia um subprocesso MCP por stdio
        ▼
Servidor MCP: python -m backend.servidor_sombrio
        │ expõe somente três ferramentas
        ▼
Ollama escolhe se responde ou chama uma ferramenta
        │
        ├── consulta/listagem → catálogo oficial
        └── compra → economia → transação SQLite
        │
        ▼
Resultado da ferramenta volta ao Ollama
        │
        ▼
Resposta final volta ao navegador
```

O servidor MCP usa `stdio`: ele conversa com o agente por entrada e saída do
subprocesso, não abre outra porta de rede. O FastAPI continua sendo o servidor
HTTP acessado pelo navegador.

O agente permite no máximo seis rodadas com o modelo e oito chamadas de
ferramenta por mensagem. Apenas nomes presentes em `PERMITIDAS` são expostos e
executados.

## Ferramentas MCP

### `listar_mercadorias(categoria="")`

Lista categorias, itens e preços. O filtro é opcional e aceita aliases como
`arma`, `veneno`, `raridades` e `equipamentos`. Um filtro desconhecido devolve
`encontrada=false` e as categorias válidas.

É uma operação somente de leitura.

### `consultar_item(nome_item)`

Normaliza o nome e consulta a fonte oficial em `backend/catalogo.py`. Retorna
existência, identificador, nome de exibição, categoria e preço em ouros.

É uma operação somente de leitura.

### `comprar_item(nome_item, quantidade=1)`

É a única ferramenta da IA autorizada a alterar o estado. Ela:

1. normaliza e valida o item;
2. recalcula o preço no servidor;
3. valida a quantidade;
4. abre a transação no SQLite;
5. confere o saldo;
6. debita e atualiza o inventário de forma atômica;
7. retorna `sucesso=true` com orçamento e estado atualizado.

Se o saldo for insuficiente ou a entrada for inválida, retorna
`sucesso=false`; nenhum ouro é debitado e nenhum item é adicionado.

Nenhuma ferramenta recebe preço fornecido pelo jogador, endereço, destino ou
frete.

## Como o modelo decide usar ferramentas

O próprio Ollama recebe os schemas das três ferramentas. O prompt orienta a
decisão, mas o servidor continua sendo a autoridade:

| Mensagem | Ação esperada |
|---|---|
| “Quais poções você tem?” | `listar_mercadorias("pocoes")` |
| “Quanto custa a espada longa?” | `consultar_item("espada longa")` |
| “Quero duas poções de vida.” | `comprar_item("pocao de vida", 2)` |
| “Você entrega no castelo?” | Responder que só vende no balcão |

Quando há várias mercadorias numa intenção clara de compra, o modelo deve
chamar `comprar_item` uma vez para cada item citado.

Os retornos das ferramentas são anexados à conversa como mensagens `tool`.
Então o modelo recebe os resultados oficiais e redige a fala final do
mercador. O modelo nunca recebe uma conexão direta com o SQLite.

## Modo de demonstração e falhas

`_resposta_demo()` é um interpretador determinístico, não outro modelo de
linguagem. Ele reconhece intenções, aliases, categorias, quantidades e compras
mais comuns para que o projeto continue demonstrável sem credencial.

Se Ollama ou MCP falhar antes de qualquer compra, o agente registra o erro no
servidor e responde pelo modo de demonstração. A resposta inclui um `aviso`.

Se a ferramenta confirmar uma compra e o modelo falhar depois, o sistema não
repete a operação. Ele compara o estado anterior e posterior e responde com
uma confirmação segura de que a mercadoria já está na bolsa.

## Formato devolvido por `/api/chat`

A resposta contém normalmente:

```json
{
  "fala": "Texto exibido no diálogo",
  "modo": "ollama",
  "ferramentas": ["consultar_item"],
  "compra_realizada": false
}
```

Quando uma compra é tentada, também pode existir `estado`. Quando ocorre
fallback, pode existir `aviso`.

Os modelos Pydantic de entrada ficam em `backend/main.py`:

- `PedidoChat`: mensagem e até dez entradas de histórico;
- `EntradaHistorico`: papel `user` ou `assistant` e conteúdo limitado;
- `PedidoCompra`: item e quantidade para os endpoints diretos de compra.

## Onde alterar cada comportamento

- Trocar o LLM: altere `OLLAMA_MODEL` no `.env`.
- Trocar host ou usar Ollama local: altere `OLLAMA_HOST`.
- Ajustar personalidade e regras de fala: edite `REGRA` em
  `backend/agente.py`.
- Adicionar aliases de linguagem: edite os mapas em `backend/agente.py` e,
  quando forem aliases de categoria MCP, em `backend/servidor_sombrio.py`.
- Alterar uma ferramenta: edite `backend/servidor_sombrio.py` e seus testes.
- Alterar itens ou preços: edite somente `backend/catalogo.py`.
- Alterar validação de preço/quantidade: edite `backend/economia.py`.
- Alterar persistência e atomicidade: edite `backend/banco.py`.

Ao criar uma nova ferramenta, ela também precisa ser adicionada a `PERMITIDAS`
para ficar visível ao modelo. Ferramentas com efeito colateral devem manter a
validação no domínio; nunca confie apenas no texto produzido pelo LLM.

## Limites de segurança

- `.env` e bancos locais são ignorados pelo Git.
- O token não aparece em respostas, logs intencionais ou documentação.
- O modelo não define preços e não escreve diretamente no banco.
- O servidor recalcula todo orçamento.
- A lista de ferramentas é fechada.
- Resultados MCP são tratados como dados, não como instruções.
- Compras usam transações atômicas e falham sem alteração parcial.
