---
tags: [conceito, metricas, machine-learning, classificacao]
date: 2026-04-02
tipo: conceito
aliases: [F1, Harmonic Mean, Precision-Recall]
---

# F1-Score: Métrica Balanceada para Classificação Desbalanceada

## O que é

F1-score é a média harmônica entre precisão e recall. Mais útil que acurácia quando classes são desbalanceadas (ex: 95% negativos, 5% positivos).

Fórmulas:
- **Precisão**: De todas as predições positivas, quantas foram corretas? TP / (TP + FP)
- **Recall**: De todos os exemplos positivos reais, quantos foram encontrados? TP / (TP + FN)
- **F1**: 2 * (Precisão * Recall) / (Precisão + Recall)

## Como funciona

```python
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

# Exemplo: detectar fraude (95% legítimo, 5% fraude)
y_true = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # 10 negativo, 2 positivo
y_pred = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]  # Modelo acertou 1, errou 1

# Métricas
accuracy = (10 + 1) / 12  # 91.7% (enganoso!)
precision = 1 / 1  # 100% (de 1 predição positiva, foi correta)
recall = 1 / 2  # 50% (de 2 fraudes reais, encontrou apenas 1)
f1 = 2 * (1.0 * 0.5) / (1.0 + 0.5)  # 66.7%

print(f"Accuracy: {accuracy:.1%}")
print(f"Precision: {precision:.1%}")
print(f"Recall: {recall:.1%}")
print(f"F1-Score: {f1:.1%}")

# Com sklearn
print(f"F1 (sklearn): {f1_score(y_true, y_pred):.1%}")
```

**Matriz de confusão:**
```
           Pred Neg  Pred Pos
Real Neg      9         1   (FP)
Real Pos      1         1   (TP)
           (TN)       (FN)
```

## Para que serve

- **Classes desbalanceadas**: Fraude, doença rara, outliers. Acurácia é inútil.
- **Trade-off Precisão/Recall**: F1 balanceia. Útil quando ambos importam.
- **Comparar modelos**: F1 é métrica única para decisão.

Exemplos:
- **Spam detection**: Precisão alta (não enviar email legítimo para spam), mas recall também importa (não deixar spam in inbox)
- **Médico diagnóstico**: Recall alto (encontrar doença), precisão (não alarmar falsamente)

## Exemplo prático

```python
# Dataset desbalanceado
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X, y = make_classification(n_samples=1000, weights=[0.95, 0.05])  # 95% neg
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Comparar métricas
print(f"Accuracy: {(y_pred == y_test).mean():.1%}")
print(f"F1-Score: {f1_score(y_test, y_pred):.1%}")

# F1 maior peso ao recall (penaliza falsos negativos)
# Útil quando falso negativo é caro
```

**Variações:**
- **Macro F1**: F1 por classe, depois média (cada classe importa igual)
- **Weighted F1**: F1 por classe, ponderado pelo suporte (natural)
- **Micro F1**: F1 global (equivalente a accuracy em multiclass)

## Aparece em

- [[16_github_repos_melhor_curso_ml]] - Métrica essencial em ML
- [[spec-driven-ai-coding]] - Validação de modelos gerados

---
*Conceito extraído em 2026-04-02*
