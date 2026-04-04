---
tags: [arquitetura-de-software, sistemas-distribuidos, filosofia, holons, microservicos]
source: https://github.com/Felipeness/the-whole-and-the-part
date: 2026-04-02
tipo: aplicacao
---

# Aplicar Holos (Holons) em Arquitetura de Microsserviços

## O que é

Um holon é uma unidade que funciona simultaneamente como entidade autônoma *e* como parte de um sistema maior. Na arquitetura de software, cada microsserviço deve ser holônico: autonomia interna (dados próprios, lógica encapsulada) + integração externa (eventos assíncronos, contratos bem definidos).

## Como implementar

**Princípio 1: Autonomia interna (tendência auto-assertiva)**

```typescript
// RUIM: Serviço de Pagamento sem autonomia
class PaymentService {
  async processPayment(paymentId: string) {
    // Chama outro serviço diretamente (acoplamento forte)
    const user = await userService.getUser(paymentId);
    const invoice = await invoiceService.getInvoice(user.id);
    // Processamento...
  }
}

// BOM: Serviço holônico com dados próprios
class PaymentService {
  private db: Database; // Banco próprio
  private cache: Redis;
  private circuitBreaker: CircuitBreaker;

  async processPayment(paymentData: PaymentEvent) {
    try {
      // Usar dados locais ou cache, nunca chamar outro serviço synchronously
      const payment = await this.db.createPayment(paymentData);

      // Autoregulação: circuit breaker previne cascata de falhas
      const result = await this.circuitBreaker.execute(() =>
        this.validateWithExternalService(payment)
      );

      await this.publishEvent('PaymentProcessed', { paymentId: payment.id });
      return result;
    } catch (error) {
      await this.publishEvent('PaymentFailed', { paymentId: paymentData.id, error });
      throw error;
    }
  }

  private async validateWithExternalService(payment: any) {
    // Única comunicação externa: query read-only, timeout curto
    return await fetch('https://fraud-service/validate', {
      method: 'POST',
      timeout: 2000, // 2 segundos máximo
      body: JSON.stringify(payment)
    });
  }
}
```

**Princípio 2: Integração via eventos (tendência integrativa)**

```typescript
// RUIM: Saga com chamadas RPC síncronas
class OrderService {
  async placeOrder(order: Order) {
    const payment = await paymentService.processPayment(order.amount); // Acoplado!
    const shipping = await shippingService.createShipment(order.id); // Acoplado!
    return { order, payment, shipping };
  }
}

// BOM: Saga com eventos
class OrderService {
  private eventBus: EventBus;
  private db: Database;

  async placeOrder(order: Order) {
    // 1. Persistir order no banco local
    const savedOrder = await this.db.saveOrder(order);

    // 2. Publicar evento (não esperar resposta)
    await this.eventBus.publish('OrderPlaced', {
      orderId: savedOrder.id,
      customerId: order.customerId,
      amount: order.amount,
      items: order.items
    });

    // 3. Retornar imediatamente (async completion)
    return { orderId: savedOrder.id, status: 'pending' };
  }

  // Listener assincronamente — não é chamado por outros serviços
  async onPaymentConfirmed(event: PaymentConfirmedEvent) {
    const order = await this.db.getOrder(event.orderId);
    order.paymentStatus = 'confirmed';
    await this.db.updateOrder(order);

    // Publicar próximo evento na cadeia
    await this.eventBus.publish('OrderReadyForShipping', { orderId: order.id });
  }

  async onShippingFailed(event: ShippingFailedEvent) {
    // Tratamento de fallback
    const order = await this.db.getOrder(event.orderId);
    order.status = 'failed';
    await this.eventBus.publish('OrderCancelled', { orderId: order.id });
  }
}

// Implementação de EventBus (Kafka, RabbitMQ, ou AWS SNS)
class KafkaEventBus implements EventBus {
  async publish(topic: string, event: any) {
    await this.producer.send({
      topic,
      messages: [{ value: JSON.stringify(event) }]
    });
  }

  async subscribe(topic: string, handler: (event: any) => Promise<void>) {
    this.consumer.subscribe({ topic });
    this.consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        await handler(JSON.parse(message.value.toString()));
      }
    });
  }
}
```

**Princípio 3: Holarchy (hierarquia de holons)**

```typescript
// Nível 1: Holon "Order Management"
class OrderManagementHolon {
  private paymentHolon: PaymentHolon;
  private shippingHolon: ShippingHolon;
  private eventBus: EventBus;

  // Govern abaixo, serve acima
  async orchestrateSaga(order: Order) {
    // Coordena sem acoplar
    await this.eventBus.publish('SagaStarted', { orderId: order.id });
  }
}

// Nível 2: Holon "Payment"
class PaymentHolon {
  private fraudDetector: FraudDetectorHolon; // Govern próprio holon
  private db: Database;

  async processPayment(event: OrderPlacedEvent) {
    // Auto-assertividade
    const isFraudulent = await this.fraudDetector.check(event.customerId);

    if (isFraudulent) {
      await this.eventBus.publish('PaymentRejected', { orderId: event.orderId });
    } else {
      // Integração: publicar para OrderManagementHolon
      await this.eventBus.publish('PaymentConfirmed', { orderId: event.orderId });
    }
  }
}

// Nível 3: Holon "Fraud Detector" (especializado)
class FraudDetectorHolon {
  private mlModel: MLModel; // Treina e governa modelo próprio
  private cache: RedisCache;

  async check(customerId: string): Promise<boolean> {
    // Autonomia completa: seu modelo, seus thresholds
    const features = await this.extractFeatures(customerId);
    const riskScore = await this.mlModel.predict(features);
    return riskScore > 0.8;
  }
}
```

**Princípio 4: Desacoplamento com contratos bem-definidos**

```typescript
// 1. Definir contrato (event schema)
interface PaymentConfirmedEvent {
  orderId: string;
  paymentId: string;
  amount: number;
  timestamp: ISO8601;
  // Versionamento para compatibilidade futura
  version: '1.0';
}

// 2. Publicar (contrato garantido)
await eventBus.publish('PaymentConfirmed', {
  orderId: 'ORD-123',
  paymentId: 'PAY-456',
  amount: 99.99,
  timestamp: new Date().toISOString(),
  version: '1.0'
});

// 3. Consumir (assumir apenas contrato)
eventBus.subscribe('PaymentConfirmed', async (event: PaymentConfirmedEvent) => {
  // Não chama PaymentService diretamente
  // Não assume detalhes internos de Payment
  // Apenas reage ao evento público
  await orderService.confirmPayment(event.orderId);
});
```

## Stack e requisitos

- **Event Bus**: Kafka (distribuído, durável), RabbitMQ (flexible), ou AWS SNS/SQS
- **Database per service**: PostgreSQL, MongoDB (um DB por holon)
- **Circuit Breaker**: Resilience4j (Java), Polly (C#), ou customizado
- **Monitoring**: Prometheus + Grafana para ver saúde dos holons
- **Service Mesh (opcional)**: Istio para observabilidade de comunicação

Requisitos conceituais:
- Entender que "holon" é padrão, não ferramenta
- Implementar mesmo se usar REST (não exige Kafka)

## Armadilhas e limitações

1. **Armadilha: "evento" como RPC disfarçado**: Não fazer isso:
   ```typescript
   // ERRADO: Esperar resposta no evento
   await eventBus.request('PaymentRequest', payload); // Isso é RPC!
   ```

2. **Limitação: eventual consistency**: Eventos são assíncronos. Se A publica e B não consome, B fica desincronizado. Exige estratégia de retry e reconciliação.

3. **Armadilha: database sharing**: Múltiplos serviços acessando mesmo DB = perda de autonomia. Cada holon precisa DB próprio.

4. **Limitação: debugging**: Fluxo através de eventos é mais difícil de rastrear. Exige distributed tracing (Jaeger, Datadog).

5. **Armadilha: cascade failures**: Se event bus cai, ninguém se comunica. Exige queue durável e replay.

## Conexões

- [[spec-driven-ai-coding]] - Gerar código de holon com Claude
- [[etl-elt-pipelines]] - Padrão Kappa (stream-only) é holônico
- [[producao-criativa-como-processo-estatistico]] - Emergência de propriedades em sistemas holônicos
- [[10-repositorios-github-data-engineering-essenciais]] - Streaming é fundamentalmente holônico

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com padrões práticos
