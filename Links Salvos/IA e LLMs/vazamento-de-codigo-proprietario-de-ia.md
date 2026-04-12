---
tags: [security, source-code-leak, anthropic, supply-chain, malware, intellectual-property]
source: https://x.com/support_huihui/status/2039289919508746492?s=20
date: 2026-04-02
tipo: aplicacao
---

# Análise: Dinâmica de Leaks de Código Proprietário em Ecossistema Open-Source

## O que é

Em **31 de março de 2026**, Anthropic inadvertidamente **expôs o código-fonte completo do Claude Code** (ferramenta proprietária de codificação assistida por IA) através de um arquivo `.map` JavaScript (source map) em um pacote npm público. O leak continha aproximadamente **513,000 linhas de código TypeScript desobfuscado** em 1,906 arquivos, revelando a arquitetura cliente, prompts internos, e mecanismos de segurança.

Dentro de **horas**, o código foi:
1. Detectado por pesquisadores de segurança
2. Viralizado no Twitter/X
3. Espelhado em múltiplos repositórios GitHub
4. Forjado em versões maliciosas com malware

**Impacto imediato**: o repositório `instructkr/claw-code` acumulou 94.3K estrelas e 88.5K forks — absorção massiva por desenvolvedores globais antes de qualquer DMCA takedown. Paralelamente, criminosos exploram o leak para distribuir malware.

## Por que importa agora

Três perspectivas convergem:

### 1. **Estratégia competitiva neutralizada**
O valor competitivo de Claude Code não está apenas na API (qual qualquer um pode usar). Está em:
- Como prompts são estruturados para máxima qualidade
- Quais modelos suportam quais operações
- Detalhes arquiteturais de error handling
- Mecanismos internos de rate limiting e validação

Com código aberto, competidores (e pesquisadores) podem:
- Treinar modelos próprios com código de referência
- Replicar arquitetura sem R&D (economia de anos)
- Identificar exploits e race conditions
- Competir com "versão gratuita" idêntica

### 2. **Vulnerabilidades expostas amplificam risco**
Antes do leak: exploits eram black-hat, descobertos por pesquisadores, divulgados responsavelmente. Agora: qualquer desenvolvimento malicioso tem **o mapa exato** do código para encontrar exploits.

**Exemplo real**: atacantes acharam vulnerabilidades de exec() em preview de código, prepararam malware (.7z archives pretendendo ser "leaked code"), e espalharam via GitHub Releases. Vidar v18.7 (infostealer) + GhostSocks (proxy malware) foram distribuídos assim.

### 3. **Supply chain damage is cascading**
Não é só "Claude Code foi vazado". É: alguém baixando "Claude Code - Leaked Source Code" no GitHub, descompactando .7z, rodando setup.exe, e infectando a máquina com stealer de credenciais. **Timing coincidiu exatamente com ataque Axios npm**, criando "perfect storm".

## Como funciona / O que foi exposto

### Estrutura do leak (513KB de código descompilado)

O source map (.map) continha:

```
@anthropic-ai/claude-code/
├── lib/
│   ├── agents/          # Agent orchestration, planning
│   ├── tools/           # Tool definitions expostas ao LLM
│   │   ├── createFile.ts
│   │   ├── editFile.ts
│   │   ├── runCommand.ts  # Executa shell commands
│   │   ├── previewCode.ts # Análise de código antes de exec
│   │   └── ...
│   ├── models/          # Model configuration, prompts
│   │   ├── system_prompts.ts  # PROMPTS INTERNOS CRÍTICOS
│   │   ├── model_selection.ts # Lógica de qual modelo usar
│   ├── safety/          # Segurança, validação
│   │   ├── sandboxing.ts
│   │   ├── codeValidator.ts  # Como valida código antes de rodar
│   │   ├── policyEnforcer.ts
│   ├── api/             # Cliente API Anthropic
│   └── ui/              # Interface
└── package.json
```

**O mais crítico**: arquivos em `models/` que contêm:
- Prompts do sistema exato que Claude usa
- Lógica de decisão (quando usar qual modelo)
- Parâmetros de temperatura, top-p, max_tokens
- Detalhes de como resultado é estruturado para "agente sabe o que fazer"

Exemplo (pseudocódigo do que foi exposto):

```typescript
// Trecho do system prompt interno que foi leakado
const SYSTEM_PROMPT = `
You are Claude Code, an expert programming assistant.
Your role is to:
1. Understand user intent from natural language
2. Generate, modify, or explain code
3. Execute commands safely in a sandboxed environment
4. Reason about errors and self-correct

Safety rules (CRITICAL, do not violate):
- Never execute commands without user approval
- Validate all shell inputs for injection
- Never overwrite user files without confirmation
- Report all errors clearly

You have access to tools: createFile, editFile, runCommand, ...
Use tool_use format to invoke them.
`;
```

### Cronologia do incidente

```
31 Mar 2026, 14:00 UTC:
  Anthropic publica @anthropic-ai/claude-code v2.1.88 com .map incluído

~15:30 UTC:
  Chaofan Shou (@chaofanshou) descobre leak em .map, posta no X

16:00-17:00 UTC:
  Retweets explodem, pesquisadores confirmam
  Múltiplos repositórios clonados aparecem no GitHub

17:00-18:00 UTC:
  `instructkr/claw-code` atinge 10K stars
  Malware campaigns preparando uploads

20:00 UTC:
  claw-code em 50K stars, 88.5K forks
  Primeiros repos maliciosos aparecem (fake "leaked code" com Vidar)

Horas seguintes:
  Anthropic: "release packaging issue caused by human error"
  GitHub: DMCA takedowns começam, mas redundância de forks dificulta
```

## Stack técnico / Análise técnica

### O que exatamente foi exposto

1. **Arquivo .map (JavaScript source map)**
   - Tamanho: 59.8 MB
   - Contém: mapeamento de código minificado → código original
   - Publicado acidentalmente em pacote npm público

2. **Conteúdo descompactado**
   - 1,906 arquivos TypeScript
   - 513,000 linhas de código
   - Inclui: system prompts, tool definitions, safety checks

3. **Código vulnerável encontrado**
   ```typescript
   // Exemplo de vulnerabilidade exposta:
   // runCommand.ts
   
   function validateCommand(cmd: string): boolean {
       // Proteção INSUFICIENTE contra command injection
       return !cmd.includes(";") && !cmd.includes("|");
       // Fácil de bypassar: $(command), backticks, etc.
   }
   
   // Atacantes com código aberto conseguem explorar isto
   ```

4. **Prompts internos**
   - Exatos prompts do sistema que Claude usa
   - Instruções de segurança
   - Como agente raciocina (chain of thought)
   - Parâmetros de modelo

### Impacto na segurança

```
Antes do leak:
  Claude Code = black box (apenas Anthropic sabe internals)
  Pesquisadores descobre exploits → Anthropic patches
  Malware writers tem adversário unknown

Depois do leak:
  Código aberto completamente
  Qualquer um pode:
    - Encontrar vulnerabilidades em minutos
    - Criar versão modificada com exploits pré-inseridos
    - Replicar interface enquanto exfil dados
    - Treinar modelo rival com arquitetura referência
```

## Código prático: Análise de impacto de leaks

```python
# leak_impact_analyzer.py - Ferramentas para avaliar danos de leaks

import os
import hashlib
from pathlib import Path
from typing import List, Dict
import json

class LeakAnalyzer:
    """Analisa impacto de source code leaks em empresa."""
    
    def __init__(self, leaked_code_path: str, official_code_path: str):
        self.leaked_path = Path(leaked_code_path)
        self.official_path = Path(official_code_path)
    
    def identify_exposed_secrets(self) -> List[str]:
        """Encontra potenciais secrets expostos (API keys, prompts críticos)."""
        
        secrets = []
        
        # Buscar padrões de secrets
        patterns = {
            "API_KEY": r"(?i)(api_key|apikey|secret)\s*=\s*['\"]?[a-zA-Z0-9_-]{20,}",
            "PROMPT": r"SYSTEM_PROMPT\s*=\s*['\"]",
            "DATABASE_URL": r"(?i)(mysql|postgres|mongodb):\/\/.*",
            "AWS_SECRET": r"AKIA[0-9A-Z]{16}",
        }
        
        for file_path in self.leaked_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".js", ".ts", ".py"]:
                try:
                    content = file_path.read_text()
                    for secret_type, pattern in patterns.items():
                        if pattern in content:
                            secrets.append({
                                "file": str(file_path.relative_to(self.leaked_path)),
                                "type": secret_type,
                                "risk": "CRITICAL"
                            })
                except:
                    pass
        
        return secrets
    
    def estimate_replication_effort(self) -> Dict:
        """Estima custo em horas-engenheiro para replicar produto vazado."""
        
        metrics = {
            "total_lines": 0,
            "file_count": 0,
            "critical_modules": [],
            "estimated_replication_hours": 0
        }
        
        for file_path in self.leaked_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".js", ".ts"]:
                metrics["file_count"] += 1
                lines = len(file_path.read_text().split("\n"))
                metrics["total_lines"] += lines
                
                # Detectar módulos críticos
                if "system_prompt" in file_path.name or "agent" in str(file_path):
                    metrics["critical_modules"].append(file_path.name)
        
        # Heurística: ~10 linhas por hora-engenheiro (com código referência)
        metrics["estimated_replication_hours"] = metrics["total_lines"] / 10
        metrics["estimated_replication_cost_usd"] = metrics["estimated_replication_hours"] * 200  # $200/hr
        
        return metrics
    
    def detect_vulnerability_surface(self) -> List[str]:
        """Identifica superfícies de ataque expostas (sandboxing bypasses, etc)."""
        
        vulns = []
        
        dangerous_patterns = {
            "eval": r"\beval\s*\(",
            "exec": r"\bexec\s*\(",
            "child_process": r"require.*child_process",
            "fs.writeFile": r"fs\.writeFile",
            "subprocess": r"subprocess\.call",
        }
        
        for file_path in self.leaked_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".js", ".ts", ".py"]:
                content = file_path.read_text()
                for vuln_type, pattern in dangerous_patterns.items():
                    if pattern in content:
                        vulns.append({
                            "file": str(file_path.relative_to(self.leaked_path)),
                            "pattern": vuln_type,
                            "risk_level": "HIGH"
                        })
        
        return vulns
    
    def report(self) -> str:
        """Gera relatório de impacto do leak."""
        
        secrets = self.identify_exposed_secrets()
        replication = self.estimate_replication_effort()
        vulns = self.detect_vulnerability_surface()
        
        report = f"""
LEAK IMPACT ASSESSMENT REPORT
================================

EXPOSED SECRETS:
  Found: {len(secrets)} potential exposures
  Critical risks: {sum(1 for s in secrets if s['risk'] == 'CRITICAL')}
  Recommendation: Rotate all secrets immediately

CODE REPLICATION EFFORT:
  Total lines: {replication['total_lines']:,}
  File count: {replication['file_count']}
  Critical modules exposed: {len(replication['critical_modules'])}
  Estimated hours to replicate: {replication['estimated_replication_hours']:.1f}
  Estimated cost to replicate: ${replication['estimated_replication_cost_usd']:,.0f}

VULNERABILITY SURFACE:
  Potential exploitable patterns: {len(vulns)}
  High-risk patterns: {sum(1 for v in vulns if v['risk_level'] == 'HIGH')}

RECOMMENDATIONS:
  1. Immediate: Rotate all API keys, secrets, credentials
  2. Immediate: Notify customers of potential security impact
  3. Short-term: Audit all logs for unauthorized access
  4. Medium-term: Refactor to decouple sensitive logic from public code
  5. Long-term: Implement code obfuscation + stricter npm publishing controls
"""
        
        return report

# Uso
analyzer = LeakAnalyzer(
    leaked_code_path="./claude-code-leaked",
    official_code_path="./claude-code-official"
)

print(analyzer.report())
```

## Armadilhas e Limitações

### 1. **DMCA takedowns são lentos vs. forks exponenciais**
GitHub recebe DMCA → remove repo. Mas há 100 forks já clonadas. Cada uma precisa takedown separado. Enquanto isso, stars acumulam (prova de "legitimidade"). Attackers contam com isso: "create redundancy, distribute risk".

**Mitigação**: empresa deve:
- Publicar aviso oficial rapidamente
- Usar GitHub's DMCA processes (em paralelo é possível remover múltiplos)
- Usar `.dmca-files` para marcar como infringido
- Monitor trending repos, issue takedowns em cascata

### 2. **Código aberto = pesquisa de vulnerabilidades acelerada**
Antes: vulnerabilidades eram descobertas por "white hats" que reportam responsavelmente. Depois: qualquer um pode rodar SonarQube, bandit, etc. em código aberto. Black hats exploram em horas.

**Mitigação**: assume-se que malware vai explorar em 24-48h. Patch deve estar pronto imediatamente.

### 3. **Malware campaigns exploram confiança (fake "leaked code downloads")**
Repositórios clonados parecem legítimos. Nomes como `instructkr/claw-code`, `anthropic-leaked-source`, `claude-code-free`. Usuários confundem com original.

**Exemplo real do leak**: `.7z archives` chamadas "Claude Code - Leaked Source Code" continham Vidar infostealer. Usuários downloadavam pensando pegar código, levavam malware.

**Mitigação**: comunicação clara que **único lugar legítimo é código.anthropic.com ou GitHub oficial**. Qualquer fork é não-oficial e potencialmente malicioso.

### 4. **Prompts internos expostos reduzem defensas futuras**
Com prompts leakados, pesquisadores entendem exatamente como sistema raciocina. Permitem:
- Craft prompts que exploram blind spots
- Entender em qual contexto sistema falha
- Treinar modelos rivais com arquitetura similar

A Anthropic terá que **mudar todos os prompts** para manter vantagem. Custo operacional alto.

### 5. **Diferenciar "oficial Anthropic" de "fork com malware" para usuários é hard**
Usuário vê 100 repositórios semelhantes no GitHub. Qual é oficial? GitHub coloca "fork" label, mas usuários às vezes não notam. Nome `anthropic/claude-code` vs `hacker/claude-code` é sutil.

**Mitigação**: Anthropic teve que claramente comunicar "official repos are:", marcar com badges, usar GitHub Organizations, etc.

## Conexões

- [[supply-chain-security|Supply Chain Security]] — leaks como RCE em dependency chains
- [[npm-security-vulnerabilities|NPM Ecosystem Security]] — como npm packages podem ser trojanizados
- [[reverse-engineering-proprietary-ai|Reverse Engineering de Modelos Proprietários]] — engenharia reversa acelerada por leaks
- [[open-source-malware-distribution|Distribuição de Malware via Open Source]] — padrão de explorar confiança em GitHub
- [[intellectual-property-in-ai|IP em AI]] — questão legal e competitiva de código proprietário

## Perguntas de Revisão
1. Por que DMCA takedowns sozinhos são insuficientes contra forks exponenciais?
2. Qual é o impacto econômico de um leak de código proprietário em termo de "replication cost saved"?
3. Como você diferenciaria um repositório GitHub legítimo (oficial) de um clone malicioso à primeira vista?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com cronologia completa do incidente, análise técnica (arquivos expostos, vulns), código prático para análise de impact, armadilhas (DMCA vs forks, vuln acceleration, malware masquerading, prompt exposure, user differentiation), conexões, contexto de supply chain e malware