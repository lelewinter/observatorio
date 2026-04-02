# Second Brain Pipeline

Monitora Reddit, X/Twitter e Hacker News 2x por dia.
Avalia relevância com Claude Haiku e cria notas Zettelkasten direto no Obsidian.

---

## Setup (5 minutos)

### 1. Copiar para um lugar fixo no seu PC
```
C:\Users\leeew\second-brain\
```
(ou qualquer pasta que não mude)

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar API key do Anthropic
Abra `config.json` e substitua:
```json
"anthropic_api_key": "sk-ant-YOUR-KEY-AQUI"
```
pela sua chave real em https://console.anthropic.com/settings/keys

### 4. Testar sem salvar nada
```bash
python pipeline.py --dry-run
```
Isso mostra o que seria criado, sem gravar no vault.

### 5. Testar de verdade
```bash
python pipeline.py
```

### 6. Agendar (08h e 17h automático)
Abra PowerShell como Administrador e rode:
```powershell
powershell -ExecutionPolicy Bypass -File agendar.ps1
```

---

## Como funciona

```
Feeds RSS (Reddit + Nitter + HN)
        ↓
  Filtrar novos (state.json)
        ↓
  Claude Haiku avalia score 0-10
        ↓
  Score ≥ 7 → Claude Sonnet gera nota Zettelkasten
        ↓
  Obsidian REST API → Links Salvos/
  (fallback: escrita direta no arquivo)
```

---

## Custo estimado

Por run (25 itens avaliados, ~5 notas geradas):
- Haiku (avaliação): ~25 × 300 tokens = 7.500 tokens ≈ $0.001
- Sonnet (geração): ~5 × 1.500 tokens = 7.500 tokens ≈ $0.03

**~$0.03 por run × 2 runs por dia = ~$1.80/mês**

---

## Personalizar

**Adicionar conta do X:**
```json
"twitter_accounts": ["nova_conta", ...]
```

**Adicionar subreddit:**
```json
"reddit_subreddits": ["novo_sub", ...]
```

**Mudar threshold de relevância (padrão 7/10):**
```json
"relevance_threshold": 8
```

**Ver histórico de runs:**
```bash
cat state.json | python -m json.tool | grep last_run
```

---

## Troubleshooting

**Nitter não funciona:** Instâncias públicas caem com frequência.
Tente adicionar outras em `nitter_instances` ou remova X por enquanto.

**Obsidian API retorna erro:** Certifique que o Obsidian está aberto
e o plugin Local REST API está ativo. O pipeline tem fallback para
escrita direta no arquivo se a API falhar.

**Poucas notas criadas:** Aumente `max_items_per_run` ou diminua
`relevance_threshold` para 6.
