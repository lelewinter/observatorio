---
tags: [apis, dados, desenvolvimento, open-source, ferramentas, recursos]
source: https://x.com/Dharmikpawar13/status/2033741169126215832?s=20
date: 2026-04-02
tipo: aplicacao
---

# Integrar 320+ APIs Públicas Gratuitas em Aplicações

## O que é

Repositório curado ([[awesome-public-apis]]) com 320k+ APIs públicas documentadas, organizadas por categoria (clima, finanças, IA, mapas, entretenimento, cripto). Elimina custo de aquisição de dados no desenvolvimento de MVPs e protótipos.

## Como implementar

**Setup: encontrar e validar API**

1. **Explorar repositório**:
   ```bash
   git clone https://github.com/public-apis/public-apis.git
   cd public-apis
   # Ver categorias em README.md (Weather, Finance, Cryptocurrency, etc.)
   ```

2. **Checklist de avaliação de API**:
   - Requer autenticação? (OAuth, API key grátis, ou open?)
   - Rate limit? (ex: 100 req/min, 1000 req/dia)
   - Latência: tempo de resposta típico
   - SLA: serviço oferece garantia de uptime?
   - Dados históricos disponíveis?

**Caso de uso 1: Dashboard de clima + geolocalização (OpenWeatherMap + OpenStreetMap)**

```javascript
// Frontend: React
import { useEffect, useState } from 'react';

const WeatherDashboard = ({ lat, lon }) => {
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    // OpenWeatherMap: 1000 calls/dia grátis
    fetch(
      `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=YOUR_API_KEY&units=metric`
    )
      .then(r => r.json())
      .then(data => setWeather(data))
      .catch(err => console.error(err));
  }, [lat, lon]);

  return weather ? (
    <div>
      <h2>{weather.name}</h2>
      <p>{weather.main.temp}°C</p>
      <p>{weather.weather[0].description}</p>
    </div>
  ) : <p>Carregando...</p>;
};

export default WeatherDashboard;
```

**Caso de uso 2: App financeiro com múltiplas fontes (CoinGecko + Alpha Vantage + FRED)**

```python
import requests
import pandas as pd
from datetime import datetime

class FinancialAggregator:
    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.alphavantage_key = "YOUR_KEY"
        self.fred_key = "YOUR_KEY"

    def get_crypto_price(self, crypto_id):
        """CoinGecko: grátis, unlimited"""
        response = requests.get(
            f"{self.coingecko_url}/simple/price",
            params={'ids': crypto_id, 'vs_currencies': 'usd'}
        )
        return response.json()[crypto_id]['usd']

    def get_stock_price(self, symbol):
        """Alpha Vantage: 5 req/min free tier"""
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alphavantage_key
            }
        )
        quote = response.json().get('Global Quote', {})
        return float(quote.get('05. price', 0))

    def get_macro_data(self, series_id):
        """FRED (Federal Reserve): grátis, economia"""
        response = requests.get(
            "https://api.stlouisfed.org/fred/series/observations",
            params={
                'series_id': series_id,
                'api_key': self.fred_key
            }
        )
        data = response.json().get('observations', [])
        return pd.DataFrame(data)

# Usar
agg = FinancialAggregator()
btc_price = agg.get_crypto_price('bitcoin')           # $45,230
aapl_price = agg.get_stock_price('AAPL')              # $185.42
gdp = agg.get_macro_data('A191RL1Q225SBEA')           # PIB trimestral USA

print(f"BTC: ${btc_price}, AAPL: ${aapl_price}")
```

**Caso de uso 3: App de entretenimento (OMDB + Spotify + Giphy)**

```javascript
// Buscar filmes + recomendações + GIFs
const fetchMovieInfo = async (title) => {
  const omdbKey = "YOUR_KEY";

  // OMDB: dados de filmes
  const movieRes = await fetch(
    `https://www.omdbapi.com/?t=${title}&apikey=${omdbKey}`
  );
  const movie = await movieRes.json();

  // Giphy: GIF do ator principal
  const gifRes = await fetch(
    `https://api.giphy.com/v1/gifs/search?q=${movie.Actors}&api_key=YOUR_GIPHY_KEY`
  );
  const gif = await gifRes.json();

  return {
    movie: movie.Title,
    rating: movie.imdbRating,
    plot: movie.Plot,
    gif: gif.data[0].url
  };
};

fetchMovieInfo('Inception').then(console.log);
```

**Caso de uso 4: Segurança (verificar Se email/senha foi comprometida)**

```python
import requests
import hashlib

# Have I Been Pwned: verificar compromissos de segurança
def check_email_breached(email):
    """Grátis, rate-limited, offline-first"""
    response = requests.get(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
        headers={'User-Agent': 'MyApp'}
    )
    if response.status_code == 200:
        return response.json()  # Breaches encontrados
    elif response.status_code == 404:
        return None  # Seguro
    else:
        raise Exception(f"Erro: {response.status_code}")

def check_password_pwned(password):
    """Algoritmo k-anonymity: nunca envia senha completa"""
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    hashes = response.text.split('\r\n')

    for h in hashes:
        if h.split(':')[0] == suffix:
            return True  # Senha comprometida
    return False  # Senha segura

print(check_email_breached('user@example.com'))
print(check_password_pwned('myPassword123'))
```

## Stack e requisitos

**Popular API públicas (grátis):**

| Categoria | API | Rate Limit | Auth |
|-----------|-----|-----------|------|
| Clima | OpenWeatherMap | 1k/dia | API key grátis |
| Financeiro | CoinGecko | unlimited | nenhuma |
| Financeiro | Alpha Vantage | 5 req/min | API key grátis |
| Macro | FRED | unlimited | API key grátis |
| Mapas | OpenStreetMap/Mapbox | 600k/mês | token |
| NLP | Hugging Face Inference | unlimited | token grátis |
| Cripto | Blockchain.com | 4 req/s | nenhuma |
| Segurança | Have I Been Pwned | unlimited | nenhuma |
| Entretenimento | OMDb | 1k/dia | API key grátis |
| Entretenimento | Spotify | 180k req/hora | OAuth |

**Requisitos técnicos:**
- HTTP client: Axios (JS), Requests (Python), cURL (bash)
- Rate limiting: implementar backoff exponencial
- Cache: Redis/localStorage para não sobrecarregar API
- Timeout: sempre definir (ex: 30 segundos)

## Armadilhas e limitações

1. **Armadilha: dependência crítica em API free**: Startup cresce, API é deprecada ou muda schema. Sempre planeje migração de dados.

2. **Limitação: rate limits**: API gratuita com 100 req/min é inútil para aplicação com 1000 usuários simultâneos. Calcule: (req por usuário/dia) × (usuários) = rate limit necessário.

3. **Armadilha: SLA zero**: APIs free não oferecem garantia de uptime. Produção exige fallback (cache, dados locais).

4. **Limitação: cobertura geográfica**: OpenWeatherMap excelente para cidades grandes, péssimo para zonas rurais. Testar com seus casos de uso.

5. **Armadilha: esquecer rate limit headers**: APIs retornam `X-RateLimit-Remaining`. Use para não bater no limit:
   ```python
   remaining = int(response.headers['X-RateLimit-Remaining'])
   if remaining < 10:
       print("Quase no limit, aguarde...")
       time.sleep(60)
   ```

6. **Limitação: CORS em browsers**: APIs backend precisam estar acessíveis via CORS. Alternativa: proxy backend próprio.

## Conexões

- [[alternativas-open-source-ao-bloomberg-terminal-podem-ser-executadas-localmente-s]] - Agregador de APIs financeiras
- [[web-scraping-sem-api-para-agentes-ia]] - Quando APIs não existem, fazer scraping
- [[spec-driven-ai-coding]] - Usar Claude para gerar integração com API
- [[clonagem-de-voz-local-open-source]] - Integrar TTS com APIs públicas

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com guia prático de implementação
