# ☽ Mercador Sombrio

> *"Nem tudo que brilha é ouro..."*

Uma pequena experiência de fantasia sombria em **pixel art**, combinando **agente de IA com Ollama**, **ferramentas MCP**, **FastAPI**, **SQLite** e um **frontend interativo**. Projeto acadêmico e de portfólio.

### O que já funciona (v0.1)

- Cenário noturno pixel art renderizado com **Canvas 2D**: castelo, lua, nuvens, chuva e relâmpagos.
- Mercador clicável em pixel art, caixa de diálogo e histórico da conversa na página.
- Vitrine pesquisável com os **47 itens e 11 destinos do servidor MCP original**.
- Bolsa com saldo de ouro, inventário persistente e total de compras.
- Orçamento com quantidade, frete e confirmação da compra.
- SQLite com transação atômica para débito de ouro e atualização de inventário.
- Agente conversacional com Ollama + **as quatro ferramentas MCP originais** quando configurado.
- **Modo demonstração** sem chave de IA: mensagens simples baseadas em catálogo, loja e compras funcionando localmente.
- Testes automatizados e workflow GitHub Actions.

## 🚀 Começar no Windows (jeito mais fácil)

1. Instale **Python 3.11 ou superior** e habilite o Python no PATH (se necessário).
2. Descompacte o projeto em uma pasta.
3. Clique duas vezes em **`iniciar.bat`**.
4. Na primeira execução, ele criará `.venv` e instalará as dependências (é preciso internet).
5. Acesse **http://127.0.0.1:8000** no navegador.

O app funciona imediatamente em **modo demonstração**. Para ativar o agente real, siga as instruções abaixo.

### Iniciar manualmente no Windows (PowerShell)

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

No Linux/macOS: `bash iniciar.sh` (ou crie um venv e rode os comandos equivalentes).

## 🤖 Habilitar o agente Ollama + MCP

O notebook acadêmico original chamava **Ollama Cloud** em `https://ollama.com`, usando **`gemma4:31b`**. Mantivemos esses valores como padrões.

1. Na raiz do projeto, **copie `.env.example` para `.env`**.
2. Edite `.env` e preencha **`OLLAMA_API_KEY`** com sua própria chave do Ollama Cloud.
3. Confira se o modelo configurado (`OLLAMA_MODEL`) está acessível na sua conta.
4. Reinicie a aplicação. Na barra superior aparecerá **OLLAMA CONECTÁVEL** e as respostas do agente, quando concluídas, indicarão **IA ATIVA**.

**Ou utilize um Ollama local**, instalado e rodando no PC, modificando no `.env`:

```dotenv
OLLAMA_API_KEY=
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Faça o download do modelo escolhido antes de iniciar (`ollama pull qwen3:8b`). Escolha um modelo que suporte **tool calling** e que sua máquina consiga executar. O Ollama/MCP é chamado apenas quando você conversa com o mercador; a vitrine e o banco funcionam sem LLM.

**Importante:** indicador de Ollama configurado não garante disponibilidade do modelo. Se a chamada falhar, a resposta muda explicitamente para o modo básico; consulte o terminal. O chat real requer pacotes `mcp` e `ollama`, fornecidos no `requirements.txt`.

## 🏰 Como testar a aplicação

1. Clique no **Mercador Sombrio** e pergunte: “Quanto custa a Poção de Vida?”
2. Clique em **Explorar mercadorias**, procure uma poção e selecione **Negociar**.
3. Escolha quantidade e destino. O orçamento será calculado pelo servidor.
4. Confirme. O ouro diminui e a mercadoria aparece na **Bolsa**.
5. Atualize a página: o saldo e inventário continuam salvos em `dados/mercador.db`.
6. Na Bolsa, **Reiniciar demonstração** restaura o saldo inicial de **1.000 moedas**.

### Segurança da compra

A IA **nunca** debita ouro ou grava no inventário. Ela apenas consulta ferramentas do MCP, conversa e calcula ofertas. O cliente envia somente item, quantidade e destino. O backend recalcula o preço oficial e executa uma transação SQLite com validação do saldo.

### Estrutura do repositório

```text
mercador_sombrio_app/
├── backend/
│   ├── main.py             # API FastAPI
│   ├── agente.py           # Orquestrador Ollama ↔ MCP e modo demo
│   ├── servidor_sombrio.py # As quatro ferramentas MCP originais
│   ├── catalogo.py         # Fonte única de preços/destinos
│   ├── economia.py         # Regras de preço e validações
│   └── banco.py            # SQLite + transações
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js             # Interface + Canvas pixel art
├── docs/
│   └── ARQUITETURA.md
├── tests/
├── .github/workflows/tests.yml
├── iniciar.bat
├── iniciar.sh
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── .gitignore
```

### Endpoints

| Método | Caminho | Responsabilidade |
|---|---|---|
| GET | `/` | Página web |
| GET | `/api/saude` | Modo IA e diagnóstico |
| GET | `/api/loja` | Itens, categorias, fretes |
| GET | `/api/estado` | Ouro e inventário |
| POST | `/api/chat` | Agente ou diálogo básico |
| POST | `/api/orcamentos` | Cálculo de orçamento, sem modificar estado |
| POST | `/api/compras` | Compra e atualização transacional |
| POST | `/api/reiniciar` | Reinicia os dados da demo local |
| GET | `/docs` | Documentação automática FastAPI |

### Testes

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

## ⚠️ Escopo acadêmico

Esta versão é **single-player local, sem login**. Não deve ser publicada na internet como aplicação aberta: o banco e o endpoint de reinício não são protegidos por autenticação e o mesmo jogador seria compartilhado entre visitantes. Em um deploy público futuro, adicionar contas/sessões, autenticação/autorização, limites de requisição, controle de gastos da API e segurança operacional.

Não inclua `.env`, chaves ou `dados/` no GitHub. O `.gitignore` já protege esses arquivos por padrão; confira `git status` antes de publicar.

**Próximas versões:** ilustrações/sprites exclusivos, animações avançadas, sons opcionais, maior observabilidade do agente, testes MCP integrados, sessões de usuário e deploy seguro.

---

**Agradecimentos:** baseada no notebook do projeto acadêmico original. As quatro ferramentas MCP, preços e destinos foram reaproveitados; interface, persistência, API e regras de compra foram adicionadas na v0.1.
