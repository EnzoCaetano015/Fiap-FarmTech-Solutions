/**
 * FarmTech Solutions – Fase 2 (Sistema de Irrigação Inteligente)
 *
 * Sistema com ESP32:
 * - Botões simulam nutrientes N, P e K
 * - LDR simula pH
 * - DHT22 simula umidade do solo e temperatura
 * - Relé simula a bomba de irrigação
 *
 * Lógica adotada:
 * - A bomba liga apenas quando a umidade estiver abaixo de 40%
 * - N, P, K e pH são usados para monitoramento e geração de alerta
 */

#include <DHT.h>

const int BTN_N_PIN = 13;
const int BTN_P_PIN = 12;
const int BTN_K_PIN = 14;

const int LDR_PIN = 34;

const int RELAY_PIN = 26;

const int DHT_PIN = 4;
#define DHTTYPE DHT22

DHT dht(DHT_PIN, DHTTYPE);

// 0 = sem chuva
// 1 = chuva fraca/moderada
// 2 = chuva forte
int nivelChuva = 0;

void setup() {
  Serial.begin(115200);

  pinMode(BTN_N_PIN, INPUT_PULLUP);
  pinMode(BTN_P_PIN, INPUT_PULLUP);
  pinMode(BTN_K_PIN, INPUT_PULLUP);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  dht.begin();

  delay(2000);

  Serial.println("==============================================");
  Serial.println("Sistema de Irrigacao Inteligente - FarmTech");
  Serial.println("Digite no Serial:");
  Serial.println("0 = sem chuva");
  Serial.println("1 = chuva fraca/moderada");
  Serial.println("2 = chuva forte");
  Serial.println("==============================================");
}

void loop() {
  lerNivelChuvaSerial();

  bool nPresent = digitalRead(BTN_N_PIN) == LOW;
  bool pPresent = digitalRead(BTN_P_PIN) == LOW;
  bool kPresent = digitalRead(BTN_K_PIN) == LOW;

  int rawLdr = analogRead(LDR_PIN);
  float pH = 3.0 + ((rawLdr - 200) * (10.0 - 3.0) / (2600.0 - 200.0));

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  bool dhtOk = !isnan(humidity) && !isnan(temperature);

  bool phOk = (pH >= 5.5 && pH <= 7.5);
  bool npkOk = nPresent && pPresent && kPresent;

  bool pumpOn = false;

  if (dhtOk) {
    if (nivelChuva == 2) {
      pumpOn = false;
    } 
    else if (nivelChuva == 1) {
      if (humidity < 30.0 && phOk && npkOk) {
        pumpOn = true;
      }
    } 
    else {
      if (humidity < 40.0 && phOk && npkOk) {
        pumpOn = true;
      }
    }
  } else {
    pumpOn = false;
  }

  digitalWrite(RELAY_PIN, pumpOn ? HIGH : LOW);

  exibirStatus(humidity, temperature, dhtOk, pH, nPresent, pPresent, kPresent, phOk, npkOk, pumpOn);

  delay(2500);
}

// FUNÇÕES

void lerNivelChuvaSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '0') {
      nivelChuva = 0;
      Serial.println("Nivel de chuva atualizado: 0 = SEM CHUVA");
    } 
    else if (c == '1') {
      nivelChuva = 1;
      Serial.println("Nivel de chuva atualizado: 1 = CHUVA FRACA/MODERADA");
    } 
    else if (c == '2') {
      nivelChuva = 2;
      Serial.println("Nivel de chuva atualizado: 2 = CHUVA FORTE");
    }
  }
}

void exibirStatus(
  float humidity,
  float temperature,
  bool dhtOk,
  float pH,
  bool nPresent,
  bool pPresent,
  bool kPresent,
  bool phOk,
  bool npkOk,
  bool pumpOn
) {
  Serial.println("--------------------------------------------------");

  Serial.print("Chuva prevista: ");
  if (nivelChuva == 0) {
    Serial.println("SEM CHUVA");
  } else if (nivelChuva == 1) {
    Serial.println("CHUVA FRACA/MODERADA");
  } else {
    Serial.println("CHUVA FORTE");
  }

  Serial.print("Umidade: ");
  if (dhtOk) {
    Serial.print(humidity, 1);
    Serial.print("%  ");
  } else {
    Serial.print("Erro  ");
  }

  Serial.print("Temperatura: ");
  if (dhtOk) {
    Serial.print(temperature, 1);
    Serial.print("C  ");
  } else {
    Serial.print("Erro  ");
  }

  Serial.print("pH: ");
  Serial.print(pH, 2);

  Serial.print("  N: ");
  Serial.print(nPresent ? "OK" : "Falta");

  Serial.print("  P: ");
  Serial.print(pPresent ? "OK" : "Falta");

  Serial.print("  K: ");
  Serial.print(kPresent ? "OK" : "Falta");

  Serial.print("  Solo: ");
  Serial.print((phOk && npkOk) ? "OK" : "ALERTA");

  Serial.print("  Bomba: ");
  Serial.println(pumpOn ? "LIGADA" : "DESLIGADA");

  if (!npkOk) {
    Serial.println("Alerta: nutrientes NPK fora do ideal.");
  }

  if (!phOk) {
    Serial.println("Alerta: pH fora da faixa adequada.");
  }

  if (!dhtOk) {
    Serial.println("Alerta: falha na leitura do DHT22.");
  }
}
 