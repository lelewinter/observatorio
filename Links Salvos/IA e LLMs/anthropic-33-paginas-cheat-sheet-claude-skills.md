---
date: 2026-03-08
tags: [Claude, skills, Anthropic, cheat sheet, building skills, guia oficial, documentação]
source: https://x.com/RoundtableSpace/status/2030595632998580328
author: "Anthropic (via 0xMarioNawfal)"
tipo: aplicacao
---

# Implementar Claude Skills Produtivos

## O que é
33-página cheat sheet oficial da Anthropic consolidando padrões, templates e boas práticas para construir [[Claude]] skills — blocos reutilizáveis que integram com Claude Code, workflows e ecossistema completo, evitando armadilhas comuns.

## Como implementar
**1. Estrutura de diretório de skill**:

```bash
my-skill/
├── SKILL.md                 # Metadados e documentação
├── skill.json              # Configuração JSON
├── src/
│   ├── main.ts             # Lógica principal
│   ├── utils.ts            # Funções auxiliares
│   └── types.ts            # TypeScript interfaces
├── tests/
│   ├── main.test.ts        # Testes unitários
│   └── integration.test.ts # Testes de integração
├── README.md               # Documentação para usuários
├── package.json            # Dependências
└── .gitignore              # Arquivos a ignorar
```

**2. SKILL.md template** (metadados e UI):

```yaml
---
name: "Process CSV to JSON"
displayName: "CSV to JSON Converter"
description: "Lê arquivo CSV e transforma em JSON estruturado com tipagem"
version: "1.0.0"
author: "seu-nome"
authorUrl: "https://github.com/seu-usuario"
license: "MIT"
tags: ["data-processing", "csv", "transformation", "json"]
category: "Data"
icon: "📊"
keywords: ["csv", "json", "converter", "data"]

# Configuração de input/output
inputSchema:
  type: "object"
  properties:
    csvFile:
      type: "file"
      description: "Arquivo CSV para processar"
      mimeType: "text/csv"
    delimiter:
      type: "string"
      description: "Delimitador (padrão: vírgula)"
      default: ","
    hasHeader:
      type: "boolean"
      description: "Primeira linha é cabeçalho?"
      default: true
  required: ["csvFile"]

outputSchema:
  type: "object"
  properties:
    data:
      type: "array"
      description: "Dados como array de objetos"
    rowCount:
      type: "number"
    columnNames:
      type: "array"
    errors:
      type: "array"
      description: "Problemas encontrados durante processamento"
---

# Descrição Detalhada

Conversor robusto de CSV para JSON com validação automática de tipos.
Detecta automaticamente tipos de coluna (string, number, date, boolean).
```

**3. skill.json (configuração)**:

```json
{
  "name": "process-csv-json",
  "version": "1.0.0",
  "runtime": "node",
  "handler": "src/main.ts",
  "dependencies": {
    "csv-parse": "^5.4.1",
    "typescript": "^5.2.0"
  },
  "timeout": 30000,
  "memory": 512,
  "environment": {
    "NODE_ENV": "production"
  },
  "permissions": ["file-read"],
  "caching": {
    "enabled": true,
    "ttl": 3600
  }
}
```

**4. Implementação em TypeScript** (src/main.ts):

```typescript
import { parse } from 'csv-parse/sync';
import * as fs from 'fs';

interface SkillInput {
  csvFile: Buffer | string;
  delimiter?: string;
  hasHeader?: boolean;
}

interface SkillOutput {
  data: Record<string, any>[];
  rowCount: number;
  columnNames: string[];
  errors: string[];
}

export async function handler(input: SkillInput): Promise<SkillOutput> {
  const errors: string[] = [];

  try {
    // Validar input
    if (!input.csvFile) {
      throw new Error("csvFile is required");
    }

    const content = typeof input.csvFile === 'string'
      ? fs.readFileSync(input.csvFile, 'utf-8')
      : input.csvFile.toString('utf-8');

    // Parse CSV
    const records = parse(content, {
      delimiter: input.delimiter || ',',
      columns: input.hasHeader !== false,
      skip_empty_lines: true,
      on_error: (err) => errors.push(err.message)
    });

    // Inferir tipos
    const columnNames = Object.keys(records[0] || {});
    const typedData = records.map((row: any) =>
      inferTypes(row, columnNames)
    );

    return {
      data: typedData,
      rowCount: records.length,
      columnNames,
      errors
    };

  } catch (err) {
    return {
      data: [],
      rowCount: 0,
      columnNames: [],
      errors: [err instanceof Error ? err.message : String(err)]
    };
  }
}

function inferTypes(row: any, columns: string[]) {
  const result: Record<string, any> = {};

  for (const col of columns) {
    const value = row[col];

    // Tentar converter em tipos mais específicos
    if (value === null || value === '') {
      result[col] = null;
    } else if (value === 'true' || value === 'false') {
      result[col] = value === 'true';
    } else if (!isNaN(Number(value))) {
      result[col] = Number(value);
    } else if (isValidDate(value)) {
      result[col] = new Date(value).toISOString();
    } else {
      result[col] = value;
    }
  }

  return result;
}

function isValidDate(dateString: string): boolean {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date.getTime());
}
```

**5. Testes** (tests/main.test.ts):

```typescript
import { handler } from '../src/main';

describe('CSV to JSON Skill', () => {
  it('should convert simple CSV', async () => {
    const input = {
      csvFile: Buffer.from('name,age\nAlice,30\nBob,25'),
      hasHeader: true
    };

    const result = await handler(input);

    expect(result.rowCount).toBe(2);
    expect(result.data[0]).toEqual({ name: 'Alice', age: 30 });
    expect(result.columnNames).toEqual(['name', 'age']);
  });

  it('should handle missing file', async () => {
    const result = await handler({ csvFile: undefined as any });
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it('should infer types correctly', async () => {
    const input = {
      csvFile: Buffer.from('id,price,active,date\n1,9.99,true,2026-04-02'),
      hasHeader: true
    };

    const result = await handler(input);
    const row = result.data[0];

    expect(typeof row.id).toBe('number');
    expect(typeof row.price).toBe('number');
    expect(typeof row.active).toBe('boolean');
    expect(row.date).toMatch(/^\d{4}-\d{2}-\d{2}/);
  });
});
```

**6. Publicar skill**:

```bash
# 1. Criar conta Anthropic (se não tiver)
# 2. Autenticar
claude login

# 3. Publicar
claude skill publish

# 4. Disponível para uso em Claude Code:
# /install my-skill
```

**7. Boas práticas de entrada/saída**:

```typescript
// ❌ EVITAR: Muito genérico
export async function handler(input: any): Promise<any> {
  return JSON.parse(input);
}

// ✅ FAZER: Tipos explícitos, validação
interface Input {
  data: string;
  format: 'csv' | 'json' | 'yaml';
}

interface Output {
  result: any;
  warnings: string[];
  executionTimeMs: number;
}

export async function handler(input: Input): Promise<Output> {
  const startTime = Date.now();

  // Validar
  if (!input.data) throw new Error("data required");
  if (!['csv', 'json', 'yaml'].includes(input.format)) {
    throw new Error("Invalid format");
  }

  // ... processar ...

  return {
    result: parsed,
    warnings: [],
    executionTimeMs: Date.now() - startTime
  };
}
```

**8. Tratamento de erros robusto**:

```typescript
class SkillError extends Error {
  constructor(
    message: string,
    public code: string,
    public retryable: boolean = false
  ) {
    super(message);
  }
}

export async function handler(input: SkillInput) {
  try {
    // ...
  } catch (err) {
    if (err instanceof SkillError) {
      return {
        success: false,
        error: err.message,
        code: err.code,
        retryable: err.retryable
      };
    }

    // Erro inesperado
    console.error("Unexpected error:", err);
    return {
      success: false,
      error: "Internal server error",
      code: "INTERNAL_ERROR",
      retryable: true
    };
  }
}
```

## Stack e requisitos
- **Runtime**: Node.js 18+ ou Deno
- **Linguagem**: TypeScript recomendado (ou JavaScript)
- **Testing**: Jest, Vitest
- **Packaging**: zip ou Docker
- **Publicação**: Marketplace da Anthropic
- **Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH)

## Armadilhas e limitações
- **Context window**: skills rodando em Claude Code têm acesso ao contexto completo. Documentar impacto em custo de tokens.
- **Timeouts**: skills têm timeout máximo (30s padrão). Tarefas longas precisam ser async + polling.
- **Dependencies**: minimizar dependências externas reduz tamanho. Use stdlib quando possível.
- **Backwards compatibility**: ao atualizar, manter compatibilidade ou versionar adequadamente.
- **Documentação**: skills sem docs boas não serão usados. Incluir exemplos, casos de erro, limites.

## Conexões
[[Claude Code - Melhores Práticas]], [[Tool Use com LLMs]], [[Workflows com LLMs]], [[MCP - Model Context Protocol]]

## Histórico
- 2026-03-08: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
