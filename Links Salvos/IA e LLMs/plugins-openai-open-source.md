---
tags: []
source: https://x.com/reach_vb/status/2037334254619709755?s=20
date: 2026-04-02
tipo: aplicacao
---

# Estudar e Implementar Plugins OpenAI Open Source

## O que é

Especificação aberta (repositório openai/plugins no GitHub) que documenta como criar plugins para LLMs — ferramenta chamável de código externo que o modelo invoca durante geração. Desmistifica mecanismo de function calling e tool use.

## Como implementar

**Etapa 1: Entender estrutura de manifesto.** Um plugin OpenAI requer 3 componentes:
```json
{
  "schema_version": "v1",
  "name_for_human": "Meu Plugin de CRM",
  "name_for_model": "crm_connector",
  "description_for_human": "Acessa contatos no Salesforce",
  "description_for_model": "Chamável para buscar/atualizar contatos",
  "auth": {
    "type": "oauth2",
    "client_id": "...",
    "authorization_url": "https://..."
  },
  "api": {
    "type": "openapi",
    "url": "https://seu-servidor/openapi.yaml"
  }
}
```

**Etapa 2: Definir OpenAPI spec.** Plugin precisa de especificação OpenAPI 3.0 descrevendo endpoints:
```yaml
openapi: 3.0.0
info:
  title: CRM Connector API
  version: 1.0.0
paths:
  /contacts/search:
    post:
      summary: Buscar contato por email
      parameters:
        - name: email
          in: query
          required: true
          schema:
            type: string
      responses:
        200:
          description: Contato encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Contact'
```

**Etapa 3: Implementar backends.** Seu servidor precisa implementar os endpoints:
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/contacts/search")
async def search_contact(email: str):
    # Chama Salesforce API
    result = salesforce_client.query(f"SELECT * FROM Contact WHERE Email='{email}'")
    if result:
        return {"id": result[0]["Id"], "name": result[0]["Name"]}
    raise HTTPException(status_code=404)

@app.post("/contacts/update")
async def update_contact(contact_id: str, data: dict):
    # Atualiza contato em Salesforce
    salesforce_client.update(contact_id, data)
    return {"status": "updated"}
```

**Etapa 4: Autenticação.** Use OAuth2 para segurança:
```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/contacts/search")
async def search_contact(email: str, token: str = Depends(oauth2_scheme)):
    # Valida token JWT
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    user_id = payload.get("sub")
    # ... continua
```

**Etapa 5: Registrar plugin.** Na interface OpenAI (ou Claude se suportar MCP), adicione plugin via URL do seu manifest:
```
https://seu-dominio.com/.well-known/openai-plugin.json
```

OpenAI/Claude indexa automaticamente endpoints do manifest.

**Etapa 6: Testar invocação.** Use playground OpenAI ou Claude Code:
```
"Busca o contato do email leticia@empresa.com no CRM"
```

Modelo internamente chama seu endpoint `/contacts/search?email=leticia@empresa.com` e usa resposta.

**Padrão MCP (Model Context Protocol).** Anthropic expandiu o padrão com MCP, compatível com Claude:
```json
{
  "type": "mcp_server",
  "host": "localhost",
  "port": 3000,
  "name": "crm_connector"
}
```

MCP é bidirecional — o servidor pode iniciar chamadas, não só responder.

## Stack e requisitos

- FastAPI ou Express para implementar endpoints
- OpenAPI 3.0 spec (editar manualmente ou gerar com ferramentas)
- OAuth2 provider (ou usar Anthropic's auth)
- HTTPS obrigatório (certificado SSL/TLS)
- Repositório público (GitHub, GitLab) para versionamento
- Tempo: 2-4 horas implementação básica

## Armadilhas e limitações

OpenAI plugins foram deprecated em 2024 em favor de function calling. MCP é a nova abordagem recomendada. HTTPS é obrigatório — localhost com HTTP não funciona. Rate limiting é responsabilidade do implementador (OpenAI não throttle automaticamente). Timeouts: requisição de plugin é limitada a 30 segundos. Erro em plugin quebra fluxo do modelo — tratamento de erro robusto é crítico. OAuth2 setup é complexo — considere usar gerenciador de auth pronto (Auth0, Okta).

## Conexões

[[Sistemas Multi-Agente para Engenharia de Software]], [[Unity-MCP Integração LLM com Game Engine]], [[Workflow 3D Completo via MCP]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação