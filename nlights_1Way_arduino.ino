// Traffic Light Basic Code adaptado para Arduino Uno
// Basado en el original de Kat Nelms, Manchester Robotics

// ----------------- CONFIGURACIÓN INICIAL -------------------
#include <Adafruit_NeoPixel.h>

// Pin de datos del LED (ajusta según conexión)
#define LED_PIN 6  

// Temporizadores (en segundos)
#define GREEN_TIME   8
#define RED_TIME     8
#define YELLOW_TIME  6

// Brillo de los LEDs (0 a 255)
#define BRIGHTNESS 50  

// Número de semáforos
int LIGHT_COUNT = 2; // Cambia a 1 si solo usarás un semáforo
int LED_COUNT;
int lightState = 1; // 1 = verde, 2 = amarillo, 3 = rojo
int MAX_LIGHTS = 2;

// Declarar objeto de tira Neopixel
Adafruit_NeoPixel strip(0, LED_PIN, NEO_GRBW + NEO_KHZ800);

// Estados
#define GREEN 1
#define YELLOW 2
#define RED 3
#define ERROR 4

// ---------------------- SETUP -----------------------------
void setup() {
  Serial.begin(9600); // Depuración

  LED_COUNT = 3 * LIGHT_COUNT; // 3 LEDs por cada semáforo
  strip.updateLength(LED_COUNT); // Actualiza longitud de la tira
  strip.begin(); 
  strip.setBrightness(BRIGHTNESS);
  strip.show(); // Apagar todos los LEDs
}

// ---------------------- LOOP PRINCIPAL ----------------------
void loop() {
  if (LIGHT_COUNT == 1) {
    if (lightState == GREEN) {
      Serial.println("Semáforo 1: Verde");
      greenLight(1);
      strip.show();
      delay(GREEN_TIME * 1000);

      Serial.println("Semáforo 1: Amarillo");
      yellowLight(1);
      strip.show();
      delay(YELLOW_TIME * 1000);
      lightState = RED;

    } else if (lightState == RED) {
      Serial.println("Semáforo 1: Rojo");
      redLight(1);
      strip.show();
      delay(RED_TIME * 1000);

      Serial.println("Semáforo 1: Amarillo");
      yellowLight(1);
      strip.show();
      delay(YELLOW_TIME * 1000);
      lightState = GREEN;

    } else {
      errorLight(1);
      Serial.println("Error en semáforo 1");
    }
  }

  if (LIGHT_COUNT == 2) {
    if (lightState == GREEN) {
      Serial.println("Semáforo 1: Verde, Semáforo 2: Rojo");
      greenLight(1);
      redLight(2);
      strip.show();
      delay(GREEN_TIME * 1000);

      Serial.println("Semáforo 1: Amarillo");
      yellowLight(1);
      strip.show();
      delay(YELLOW_TIME * 1000);
      lightState = RED;

    } else if (lightState == RED) {
      Serial.println("Semáforo 2: Verde, Semáforo 1: Rojo");
      redLight(1);
      greenLight(2);
      strip.show();
      delay(RED_TIME * 1000);

      Serial.println("Semáforo 2: Amarillo");
      yellowLight(2);
      strip.show();
      delay(YELLOW_TIME * 1000);
      lightState = GREEN;

    } else {
      errorLight(1);
      errorLight(2);
      Serial.println("Error en semáforos");
    }
  }
}

// ---------------------- FUNCIONES DE LUZ ----------------------

void clearLight(int lightNumber) {
  int redLED = lightNumber * 2 + (lightNumber - 3);
  strip.setPixelColor(redLED,     strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 1, strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 2, strip.Color(0, 0, 0, 0));
}

void redLight(int lightNumber) {
  int redLED = lightNumber * 2 + (lightNumber - 3);
  strip.setPixelColor(redLED,     strip.Color(255, 0, 0, 0));
  strip.setPixelColor(redLED + 1, strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 2, strip.Color(0, 0, 0, 0));
}

void yellowLight(int lightNumber) {
  int redLED = lightNumber * 2 + (lightNumber - 3);
  strip.setPixelColor(redLED,     strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 1, strip.Color(255, 255, 0, 0));
  strip.setPixelColor(redLED + 2, strip.Color(0, 0, 0, 0));
}

void greenLight(int lightNumber) {
  int redLED = lightNumber * 2 + (lightNumber - 3);
  strip.setPixelColor(redLED,     strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 1, strip.Color(0, 0, 0, 0));
  strip.setPixelColor(redLED + 2, strip.Color(0, 255, 0, 0));
}

void errorLight(int lightNumber) {
  int redLED = lightNumber * 2 + (lightNumber - 3);
  strip.setPixelColor(redLED,     strip.Color(0, 0, 255, 0));
  strip.setPixelColor(redLED + 1, strip.Color(0, 0, 255, 0));
  strip.setPixelColor(redLED + 2, strip.Color(0, 0, 255, 0));
}
