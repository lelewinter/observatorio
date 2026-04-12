---
tags: [arduino, esp32, raspberry-pi, emulador, browser, open-source, hardware]
source: https://x.com/_vmlops/status/2041160898866483402
date: 2026-04-06
tipo: aplicacao
---
# Velxio: Emulador de Arduino/ESP32/Raspberry Pi no Browser (Zero Install)

## O que é
Velxio é um emulador open-source que roda Arduino, ESP32 e Raspberry Pi inteiramente no navegador, sem instalação local de ferramentas de hardware. Suporta 19+ placas (Arduino Uno, ESP32, ESP32-C3, RPi Pico, RPi 3, etc) com emulação real de CPU (AVR8 para Arduino, RP2040 para Pi Pico, QEMU fork para ESP32 Xtensa). Oferece 48+ componentes eletrônicos interativos (LEDs, botões, sensores, displays LCD). Código escrito em C++ nativo ou Python é compilado e simulado com precisão de clock cycle. Disponível gratuitamente em velxio.dev, self-hostable, e com licença comercial disponível.

## Como implementar

### Setup: Rodar Localmente (2 minutos)

Acesse velxio.dev direto no browser (zero install):

```
https://velxio.dev
```

Ou self-host:

```bash
# Clone repositório
git clone https://github.com/velxio/velxio
cd velxio

# Instalar dependências
npm install

# Build emuladores (compila binários QEMU/AVR8)
npm run build:emulators

# Rodar servidor
npm start

# Acessa em http://localhost:3000
```

### Primeiro Projeto: Blink LED no Arduino Uno

1. **Criar novo sketch**:
   - Placa: Arduino Uno
   - Linguagem: C++

2. **Escrever código**:

```cpp
#define LED_PIN 13

void setup() {
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    delay(1000);
}
```

3. **Componentes virtuais**:
   - Clicar em "+" → adicionar LED
   - Conectar LED ao pino 13 do Arduino
   - Adicionar ground

4. **Compilar e rodar**:
   - Botão "Upload"
   - Velxio compila código com `avr-gcc` (emulado no browser)
   - Simula execução em tempo real: LED pisca a cada 1 segundo

### Projeto Intermediário: ESP32 com WiFi Virtual

```cpp
#include <WiFi.h>
#include "secrets.h"  // SSID, password

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

WebServer server(80);

void handleRoot() {
    server.send(200, "text/html", "<h1>ESP32 está rodando!</h1>");
}

void setup() {
    Serial.begin(115200);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi conectado");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        
        server.on("/", handleRoot);
        server.begin();
    } else {
        Serial.println("\nFalha ao conectar WiFi");
    }
}

void loop() {
    server.handleClient();
}
```

**Emular no Velxio**:
- Placa: ESP32
- WiFi está simulado: acessa rede "VelxioNet" virtual
- WebServer responde localmente
- Serial output aparece no console do emulador

### Projeto Avançado: Raspberry Pi Pico com PWM + Sensor

Cenário: controlar velocidade de motor com potenciômetro analógico.

```python
# MicroPython no RPi Pico
from machine import Pin, PWM, ADC
import time

# GPIO 15 = PWM output (motor)
# GPIO 26 = ADC input (potenciômetro)

motor_pin = Pin(15, Pin.OUT)
pwm = PWM(motor_pin)
pwm.freq(1000)  # 1kHz

pot_pin = ADC(Pin(26))

while True:
    # Ler potenciômetro (0-65535)
    pot_value = pot_pin.read_u16()
    
    # Mapear para 0-65535 (duty cycle)
    pwm.duty_u16(pot_value)
    
    print(f"PWM: {pot_value // 256}%")
    
    time.sleep(0.1)
```

**Setup no Velxio**:
1. Adicionar Raspberry Pi Pico
2. Componentes:
   - Potenciômetro → GPIO 26 (com ground e 3.3V)
   - Motor DC com transistor → GPIO 15
   - LED em série (ver PWM control)

3. Compilar e simular:
   - Velxio executa Python com RP2040 emulator
   - Lê valor do potenciômetro virtual
   - Ajusta PWM em tempo real
   - Motor girar mais rápido conforme roda potenciômetro

### Integração com Claude Code

Usar Velxio com Claude Code para gerar + testar firmware automaticamente:

```python
# Script de automação: gera código ESP32 via Claude, testa no Velxio

import anthropic
import subprocess
import json
import time

class VelxioAutomatedTesting:
    def __init__(self, velxio_api_url: str = "http://localhost:3000/api"):
        self.client = anthropic.Anthropic()
        self.velxio_url = velxio_api_url
    
    def generate_firmware(self, requirement: str, board: str = "esp32") -> str:
        """Claude gera código ESP32 baseado em requisito"""
        
        prompt = f"""
Você é especialista em firmware embedded. Gere código {board.upper()} que:
{requirement}

Requisitos:
- Código em C++ nativo (Arduino IDE compatible)
- Inclua setup() e loop()
- Adicione Serial.begin(115200) para debug
- Comente cada seção
- Máximo 150 linhas

Responda APENAS com código, nada mais.
"""
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def upload_and_test(self, code: str, board: str, test_duration_seconds: int = 5) -> Dict:
        """
        Upload código para Velxio via API e monitora output
        """
        
        # 1. Upload
        response = requests.post(
            f"{self.velxio_url}/sketch/upload",
            json={
                "code": code,
                "board": board,
                "compiler_optimization": "O2"
            }
        )
        
        if response.status_code != 200:
            return {"status": "error", "message": response.text}
        
        sketch_id = response.json()["sketch_id"]
        
        # 2. Rodar simulação
        requests.post(
            f"{self.velxio_url}/sketch/{sketch_id}/run"
        )
        
        # 3. Monitorar serial output por N segundos
        serial_logs = []
        start_time = time.time()
        
        while time.time() - start_time < test_duration_seconds:
            log_response = requests.get(
                f"{self.velxio_url}/sketch/{sketch_id}/serial"
            )
            
            if log_response.status_code == 200:
                logs = log_response.json().get("logs", [])
                serial_logs.extend(logs)
            
            time.sleep(0.1)
        
        # 4. Parar simulação
        requests.post(
            f"{self.velxio_url}/sketch/{sketch_id}/stop"
        )
        
        return {
            "status": "success",
            "sketch_id": sketch_id,
            "serial_output": "\n".join(serial_logs),
            "test_duration": test_duration_seconds
        }
    
    def validate_output(self, serial_output: str, expected_patterns: List[str]) -> bool:
        """Verifica se output contém patterns esperados"""
        return all(pattern in serial_output for pattern in expected_patterns)
    
    def full_pipeline(self, requirement: str, expected_output: List[str], board: str = "esp32"):
        """Gera → testa → valida automaticamente"""
        
        print(f"[1] Gerando firmware para: {requirement}")
        code = self.generate_firmware(requirement, board)
        
        print(f"[2] Upload e teste no Velxio")
        result = self.upload_and_test(code, board, test_duration_seconds=10)
        
        if result["status"] != "success":
            return {"status": "failed", "error": result["message"]}
        
        print(f"[3] Validando output")
        is_valid = self.validate_output(result["serial_output"], expected_output)
        
        return {
            "status": "passed" if is_valid else "failed",
            "code": code,
            "serial_output": result["serial_output"],
            "expected": expected_output,
            "matches": is_valid
        }

# Uso
tester = VelxioAutomatedTesting()

result = tester.full_pipeline(
    requirement="Pisque LED no pino 2. Escreva 'LED ON' ou 'LED OFF' no serial",
    expected_output=["LED ON", "LED OFF"],
    board="esp32"
)

print(result)
```

### Comparação: Velxio vs Hardware Real

| Aspecto | Velxio | Hardware Real |
|---------|--------|---------------|
| **Setup** | 0 min (velxio.dev) | 30 min (drivers, IDE) |
| **Custo** | Free | $5-50 por placa |
| **Ambiente** | Qualquer browser | Windows/Mac/Linux |
| **Debugging** | Excelente (step, breakpoints) | Limitado (serial apenas) |
| **Sensores** | Simulados, sem variância real | Ruído real, variações |
| **IoT/Rede** | Simulado (localhost) | Real (WiFi, 4G) |
| **Velocidade** | ~10x mais lento que real | Tempo real |
| **Múltiplas placas** | Sim (projeto complexo) | Caríssimo |
| **CI/CD** | Excelente (headless) | Difícil (precisa hardware) |

**Quando usar Velxio**:
- Prototipagem rápida
- Aprendizado (sem medo de danificar)
- CI/CD automatizado
- Testes de lógica antes de hardware
- Projetos com múltiplas placas

**Quando usar hardware real**:
- Produção
- Timing crítico (real-time)
- Sensores precisam de ruído realista
- IoT com rede real

## Stack e Requisitos

### Software
- **Browser**: Chrome, Firefox, Safari, Edge (moderno, WebAssembly support)
- **Node.js**: v16+ (apenas se self-host)
- **Emuladores internos**:
  - **AVR8**: `simavr` compilado para JavaScript via Emscripten
  - **RP2040** (Pi Pico): QEMU fork compilado para JS
  - **Xtensa** (ESP32): QEMU com suporte Xtensa

### Placas Suportadas (19+)
- **Arduino**: Uno, Nano, Mega, Pro Mini, Due, MKR WiFi 1010
- **ESP**: ESP32, ESP32-C3, ESP32-S3, ESP8266
- **Raspberry Pi**: Pi Pico, Pi 3, Pi 4, Pi Zero
- **Teensy**: 3.2, 4.0, 4.1
- **STM32**: BluePill (STM32F103)

### Componentes Eletrônicos Simulados (48+)
- **Input**: Botões, joystick, sensores (luz, temperatura, distância)
- **Output**: LED (single + RGB), buzzer, servo, motor DC
- **Display**: LCD 16x2, OLED, 7-segment
- **Comunicação**: UART (serial), I2C, SPI
- **Potência**: Bateria, divisor de tensão, transistor

### Hardware Requerido (Self-Host)
- **CPU**: Qualquer (browser executa JS/WASM)
- **RAM**: 2GB mínimo (emuladores não são leves)
- **Armazenamento**: 500MB para dependências Node
- **Rede**: Nenhuma (tudo local)

### Custo
- **Velxio.dev hosted**: Gratuito
- **Self-host**: Gratuito (AGPLv3)
- **Commercial license**: Contatar Velxio team

## Armadilhas e Limitações

### 1. Emulação Não é 100% Precisa em Timing
Velxio emula corretamente, mas browser JS tem variabilidade:
- Pode executar mais lento ou mais rápido que hardware real
- Não é adequado para protocolos que exigem timing nanossegundo

**Mitigação**:
```cpp
// ✓ OK: delays genéricos
delay(1000);  // ±50ms aceitável

// ✗ RUIM: timing critico
while (micros() < target_micros);  // Pode ser 10x errado

// Usar flag "fast mode" ou "precise timing" nas settings
```

### 2. Sensores Virtuais Não Têm Ruído Real
Potenciômetro virtual sempre retorna valor exato. Hardware real tem variação.

**Mitigação**:
```cpp
// Adicionar simulação de ruído (jitter)
int noisy_reading = pot_value + random(-5, 6);

// Usar filtro exponencial (funciona melhor no Velxio)
const float ALPHA = 0.1;
filtered = (ALPHA * raw_reading) + ((1 - ALPHA) * filtered);
```

### 3. Rede/WiFi é Simulada com Latência Artificial
Conexões WiFi no Velxio são localhost (0ms). Real é 50-500ms.

**Mitigação**:
```cpp
// Verificar comportamento com latência:
// - Timeouts devem ser >>100ms
// - Usar connection pooling/reuse
// - Testar edge case: WiFi desconecta mid-request
```

### 4. Compilação Lenta em Primeiro Upload
Tree-sitter parsing + LLVM backend = 3-5 segundos primeira vez.

**Mitigação**:
- Cache é automático (segunda compilação: <500ms)
- Pre-compile estilo gulpfile if workflow é muito iterativo

### 5. Algumas Bibliotecas Arduino Não Funcionam
Bibliotecas que chamam asm direto ou acessam hardware baixo nível pode não funcionar.

**Mitigação**:
```cpp
// Verificar suporte em velxio.dev/docs/libraries

// ✓ Suportadas
#include <Wire.h>        // I2C
#include <SPI.h>         // SPI
#include <Servo.h>       // Servo control
#include <LiquidCrystal.h>  // LCD

// ⚠ Parciais
#include <WiFi.h>        // WiFi simulado
#include <EEPROM.h>      // Armazenamento virtual

// ✗ Não suportadas
#include <driver/gpio.h>  // ESP-IDF (use Arduino API)
#include <assembly>       // Assembly inline
```

### 6. Consumo de Memória Emulador
Emular múltiplas placas simultaneamente = uso alto de RAM.

**Mitigação**:
```javascript
// No Velxio console
// Monitorar aba DevTools → Memory
// Se >500MB, fechar sketches não usados
```

## Conexões
- [[arduino-programming-beginner]] - Tutoriais Arduino básico
- [[esp32-wifi-mqtt]] - Projetos IoT com ESP32
- [[raspberry-pi-pico-micropython]] - MicroPython no RP2 Pico
- [[embedded-testing-ci-cd]] - Testing automatizado com Velxio
- [[hardware-emulation-techniques]] - Como emuladores funcionam
- [[web-assembly-wasm-performance]] - WebAssembly no browser

## Histórico
- 2026-04-06: Nota criada com projetos desde blink até WiFi + automação de teste
