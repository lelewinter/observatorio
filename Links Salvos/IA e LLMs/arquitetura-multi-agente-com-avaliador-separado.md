---
tags: []
source: https://x.com/0xCVYH/status/2036485891250635248?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Pipeline Multi-Agente com Avaliador Crítico

## O que é
Arquitetura de 3 agentes especializados em tensão produtiva (GAN-inspired): Planejador expande requisito em spec, Gerador implementa iterativamente, Avaliador testa com Playwright e valida contrato. Supera agente solo em qualidade e criatividade; custo maior mas delta de valor desproporcional.

## Como implementar
**1. Define os 3 agentes**:

```python
from anthropic import Anthropic
from dataclasses import dataclass

@dataclass
class AgentConfig:
    name: str
    role: str
    sys_prompt: str
    model: str = "claude-3-5-sonnet-20241022"

class TriAgentPipeline:
    def __init__(self):
        self.client = Anthropic()

        self.planner = AgentConfig(
            name="Planner",
            role="Estrategista",
            sys_prompt="""Você é estrategista de produto.
            Dado um requisito curto, expanda em especificação detalhada.
            Inclua: features, UI mockups, critérios de aceitação,
            ordem de implementação, testes necessários.
            Output em JSON estruturado."""
        )

        self.generator = AgentConfig(
            name="Generator",
            role="Implementador",
            sys_prompt="""Você é engenheiro implementador.
            Receba uma especificação, implemente em sprints.
            Cada sprint = 1-2 features. Escreva código limpo, testado.
            Após cada sprint, relatar progresso e problemas."""
        )

        self.evaluator = AgentConfig(
            name="Evaluator",
            role="Crítico",
            sys_prompt="""Você é revisor crítico de software.
            Teste a aplicação com Playwright. Verifique:
            - Features funcionam conforme spec
            - UI é responsiva e usável
            - Performance aceitável
            - Bugs ou edge cases

            Output: relatório de problemas encontrados."""
        )

    def call_agent(self, agent_config: AgentConfig, prompt: str, context: str = "") -> str:
        """Invoca um agente com prompt + contexto."""
        messages = [
            {
                "role": "user",
                "content": f"{context}\n\n{prompt}"
            }
        ]

        response = self.client.messages.create(
            model=agent_config.model,
            max_tokens=3000,
            system=agent_config.sys_prompt,
            messages=messages
        )

        return response.content[0].text
```

**2. Fase 1: Planejamento colaborativo**:

```python
def phase_planning(self, user_requirement: str) -> dict:
    """Planejador expande requisito; contrato explícito."""

    # Passo 1: Planejador cria spec
    spec_prompt = f"""Analise este requisito:
    {user_requirement}

    Crie uma especificação em JSON com:
    - nome do projeto
    - features principais (5-10)
    - user stories
    - critérios de aceitação
    - estimar 'pronto' em cada feature"""

    spec = self.call_agent(self.planner, spec_prompt)

    # Passo 2: Gerador revisa e negocia
    gen_prompt = f"""Revise esta spec para implementação:
    {spec}

    Você consegue fazer tudo? Se não, qual a priorização?
    Retorne JSON com: viável=true/false, risco=baixo/médio/alto"""

    gen_feedback = self.call_agent(self.generator, gen_prompt, context=spec)

    # Passo 3: Contrato explícito
    contract_prompt = f"""Baseado nessa discussão:
    Spec: {spec}
    Feedback do gerador: {gen_feedback}

    Crie um contrato explícito:
    - Features comprometidas
    - Ordem de entrega
    - Definição de 'pronto' para cada sprint
    - Critérios de teste

    Todos (planner, gerador, evaluator) concordam?"""

    contract = self.call_agent(self.planner, contract_prompt)

    return {
        "spec": spec,
        "feedback": gen_feedback,
        "contract": contract
    }
```

**3. Fase 2: Implementação em sprints**:

```python
def phase_generation_with_feedback_loop(self, contract: str, max_sprints: int = 10) -> dict:
    """Generator implementa iterativamente, Evaluator testa cada sprint."""

    implementation_state = {
        "sprint": 0,
        "completed_features": [],
        "known_issues": [],
        "code": "",
        "test_results": []
    }

    for sprint_num in range(max_sprints):
        implementation_state["sprint"] = sprint_num

        # Gerador implementa sprint
        gen_prompt = f"""Sprint {sprint_num}: Implemente a próxima feature.

        Contrato: {contract}
        Já completo: {implementation_state['completed_features']}
        Problemas anteriores: {implementation_state['known_issues']}

        Escreva código (HTML/CSS/JS ou sua linguagem).
        Retorne JSON com: código, features_nesta_sprint, problemas_encontrados"""

        gen_output = self.call_agent(self.generator, gen_prompt)
        gen_json = json.loads(self.extract_json(gen_output))

        implementation_state["code"] += "\n" + gen_json["código"]
        implementation_state["completed_features"].extend(
            gen_json.get("features_nesta_sprint", [])
        )

        # Evaluador testa
        eval_prompt = f"""Teste esta implementação:

        {gen_json['código']}

        Features esperadas: {gen_json['features_nesta_sprint']}

        Use Playwright (simulado):
        - Teste cada feature
        - Reporte bugs encontrados
        - Score: 0-100% (quanto da spec funciona)

        Output: {{score: X, bugs: [...], aprovado: true/false}}"""

        eval_output = self.call_agent(self.evaluator, eval_prompt)
        eval_json = json.loads(self.extract_json(eval_output))

        implementation_state["test_results"].append(eval_json)
        implementation_state["known_issues"].extend(
            eval_json.get("bugs", [])
        )

        print(f"Sprint {sprint_num}: Score={eval_json['score']}%, "
              f"Bugs={len(eval_json.get('bugs', []))}")

        # Parar se passou
        if eval_json.get("aprovado", False):
            break

    return implementation_state
```

**4. Fase 3: Refinamento pós-teste**:

```python
def phase_refinement(self, implementation: dict, max_iterations: int = 3) -> str:
    """Se avaliador reprovou, gerar volta para corrigir."""

    for iteration in range(max_iterations):
        last_eval = implementation["test_results"][-1]

        if last_eval.get("aprovado", False):
            return "✓ Implementação aprovada"

        # Gerador corrige baseado em bugs do avaliador
        bug_list = last_eval.get("bugs", [])

        fix_prompt = f"""Corrija estes bugs na implementação:

        Bugs reportados:
        {chr(10).join(bug_list)}

        Código atual:
        {implementation['código'][-1000:]}  # últimos 1000 chars

        Gere código corrigido."""

        fixed_code = self.call_agent(self.generator, fix_prompt)
        implementation["código"] += "\n" + fixed_code

        # Re-testar
        eval_prompt = f"""Re-teste com as correções:
        {fixed_code}

        Bugs agora resolvidos? Output: {{score: X, bugs: [], aprovado: T/F}}"""

        new_eval = self.call_agent(self.evaluator, eval_prompt)
        implementation["test_results"].append(json.loads(self.extract_json(new_eval)))

    return "⚠ Max iterations reached, entrega parcial"
```

**5. Métricas e análise de comportamento emergente**:

```python
def analyze_pipeline_effectiveness(self, implementation: dict) -> dict:
    """Analisa qualidade do output comparado a agente solo."""

    metrics = {
        "total_sprints": implementation["sprint"],
        "approval_rate": sum(
            1 for r in implementation["test_results"] if r.get("aprovado")
        ) / len(implementation["test_results"]),
        "final_score": implementation["test_results"][-1]["score"],
        "creativity_signal": self._detect_creative_pivots(implementation),
        "cost_vs_solo": {
            "multi_agent_cost": 200,  # $ estimado
            "solo_agent_cost": 9,      # $ estimado
            "quality_delta": 16,       # features funcionando vs 1-2
            "roi": "16x features / 22x custo = 0.73 (ainda favorável)"
        }
    }

    return metrics

def _detect_creative_pivots(self, implementation: dict) -> bool:
    """Detecta se agente teve insights criativos (10ª iteração)."""
    if implementation["sprint"] >= 10:
        # Padrão observado: iteração 10+ tem pivots criativos
        return True
    return False
```

## Stack e requisitos
- **Modelos**: Claude 3.5 Sonnet (Opus para melhor qualidade se budget permitir)
- **Testing**: Playwright (ou Selenium)
- **Custo**: ~$200 por ciclo completo (vs. $9 agente solo)
- **Tempo**: 6+ horas (vs. 20 minutos solo)
- **Vantagem**: qualidade e features 16x melhor

## Armadilhas e limitações
- **Context anxiety**: Sonnet 4.5 degrada com contexto crescente. Opus 4.5 não. Escolher modelo cuidadosamente.
- **Custo linear**: cada iteração custa. Implementar max_iterations rigorosamente.
- **Hallucination de teste**: Evaluator pode alucinar "testes passando" sem realmente rodar Playwright. Integrar Playwright real se possível.
- **Divergência de modelos**: diferentes LLMs podem não colaborar bem. Testar composição completa.

## Conexões
[[Arquitetura Multi-Agente]], [[Tool Use com LLMs]], [[Playwright Testing]], [[Agentes Especializados]], [[GAN-Inspired Architecture]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
