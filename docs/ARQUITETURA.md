# Arquitetura — Mercador Sombrio v0.1

## Diagrama

```text
Navegador / frontend (HTML + CSS + JS + Canvas)
        │ HTTP / JSON
        ▼
FastAPI (backend/main.py)
   ├── /api/loja ───────────────> catalogo.py (LOJA + TAXAS originais)
   ├── /api/estado ─────────────> SQLite (banco.py)
   ├── /api/orcamentos ─────────> economia.py (valores em centavos)
   ├── /api/compras ────────────> banco.py (BEGIN IMMEDIATE + COMMIT/ROLLBACK)
   └── /api/chat ───────────────> agente.py
                  ├── sem chave: diálogo básico (indicado como demo)
                  └── Ollama configurado: Ollama AsyncClient
                        │ ferramentas descobertas MCP
                        ▼
                 MCP ClientSession (stdio)
                        │ inicia subprocesso Python
                        ▼
              backend.servidor_sombrio
                   ├── listar_loja
                   ├── consultar_item
                   ├── consultar_taxa
                   └── calcular_total
```

## Modelo de dados

- `jogador(id, nome, ouro_centavos)`: um jogador local com 100.000 centésimos de ouro (1.000 moedas).
- `inventario(jogador_id, item, quantidade)`: quantidades acumuladas por item.
- `compras(id, jogador_id, item, quantidade, local, subtotal_centavos, taxa_centavos, total_centavos, criado_em)`: histórico de transações.

Todos os valores monetários persistidos são inteiros. O catálogo original utiliza floats; eles são convertidos **via `Decimal(str(valor))`** uma única vez antes dos cálculos para evitar problemas de precisão binária.

## Garantias

1. A IA não possui uma ferramenta para comprar: somente as 4 ferramentas originais de leitura/cálculo são expostas via MCP.
2. O frontend não envia preços oficiais ou saldos: o backend recalcula valores usando seu catálogo.
3. A compra usa `BEGIN IMMEDIATE` e atualiza ouro, inventário e histórico numa transação indivisível.
4. Operação inválida ou saldo insuficiente cancela a transação.
5. Chaves de API só são lidas pelo backend a partir do `.env`; nunca entram no JavaScript.
6. O modo básico é **claramente identificado**, sem fingir que o modelo ou o MCP responderam.

## Restrições do MVP

- Single-player, sem autenticação/sessões.
- Compras simuladas com ouro fictício.
- `.env` e `.db` ignorados pelo Git.
- Ferramentas MCP só estão ativas com Ollama funcionando; CRUD da aplicação independe do modelo.
- API funciona localmente em `127.0.0.1`; não publicar assim diretamente na internet.

## O que testar depois em uma máquina com dependências completas

- Chamada real de `/api/chat` em Ollama Cloud e com Ollama local, verificando retorno de tool calling.
- `session.list_tools()` retornando as quatro ferramentas e `call_tool()` com os esquemas esperados.
- Windows, Python 3.11+, instância local SQLite persistente, layout mobile.
- Redução de movimento, navegação por teclado e contraste visual.
