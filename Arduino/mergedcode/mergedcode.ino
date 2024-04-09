#include <Temperature_LM75_Derived.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
// include the library code:
#include <LiquidCrystal.h>

const int buttonPin = 7;

int buttonState = 0;

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 50, en = 51, d4 = 5, d5 = 4, d6 = 3, d7 = 2;

//moisture variables
const int OpenAirReading = 590;   //calibration data 1 (calibrating for 0 value)
const int WaterReading = 390;     //calibration data 2 (calibrating for 100 value)
int MoistureLevel = 0;
int SoilMoisturePercentage = 0;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// The Generic_LM75 class will provide 9-bit (±0.5°C) temperature for any
// LM75-derived sensor. More specific classes may provide better resolution.
Generic_LM75 temperature;

// For brightness
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(0x29, 12345);

byte smileyFace[8] = {
  0b00000,
  0b00000,
  0b01010,
  0b00000,
  0b00000,
  0b10001,
  0b01110,
  0b00000
};

byte sadFace[8] = {
  0b00000,
  0b00000,
  0b01010,
  0b00000,
  0b01110,
  0b10001,
  0b00000,
  0b00000
};

byte neutralFace[8] = {
  0b00000,
  0b00000,
  0b01010,
  0b00000,
  0b00000,
  0b11111,
  0b00000,
  0b00000
};

/**************************************************************************/
/*
    Arduino setup function (automatically called at startup)
*/
/**************************************************************************/
void setup() {
  while(!Serial) {}
  
  Serial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);

  //lcd setup
  // initialize LCD and set up the number of columns and rows:
  lcd.begin(16, 2);
  // create a new character
  lcd.createChar(0, smileyFace);

  // create a new character
  lcd.createChar(1, sadFace);

  // create a new character
  lcd.createChar(2, neutralFace);

  // lcd setup
  lcd.setCursor(0, 0);
  lcd.print("TEMP ");
  lcd.print("LIGHT ");
  lcd.print("MOIST ");

  lcd.write(byte(0)); // when calling lcd.write() '0' must be cast as a byte

  //end of lcd setup

  Wire.begin();

  /* Initialise the sensor */
  //use tsl.begin() to default to Wire, 
  //tsl.begin(&Wire2) directs api to use Wire2, etc.
  if(!tsl.begin())
  {
    /* There was a problem detecting the TSL2561 ... check your connections */
    Serial.print("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
}

void lcdDisplay() {
  //temperature sensor reading
  float temp = temperature.readTemperatureC();

  //brightness sensor reading
  /* Get a new sensor event */ 
  sensors_event_t event;
  tsl.getEvent(&event);
  lcd.setCursor(5, 1);

  /* Display the results (light is measured in lux) */
  float lux = event.light;

  //moisture sensor reading
  MoistureLevel = analogRead(A0);  //update based on the analog Pin selected
  SoilMoisturePercentage = map(MoistureLevel, OpenAirReading, WaterReading, 0, 100);

  // temperature section
    lcd.setCursor(0, 1);
    
    if(temp < 10) {
      //low temperature
      lcd.write((byte)1); //sad face
    }
    else if(temp < 18) {
      //low temperature
      lcd.write((byte)2); //neutral face
    }
    else if(temp >= 18 && temp <= 24) {
      //medium temperature
      lcd.write((byte)0); //happy face
    }
    else if(temp > 24 && temp < 30) {
      //high temperature
      lcd.write((byte)2); //neutral face
    }
    else if(temp >= 30) {
      //high temperature
      lcd.write((byte)1); //sad face
    }
    //======================

    // brightness LCD display //TODO: check
    lcd.setCursor(5, 1);

    if (event.light)
    {
      if(lux < 200) {
        lcd.write((byte)1); //sad face
      }
      else if(lux < 500) {
        lcd.write((byte)2); //neutral face
      }
      else if(lux >= 500 && lux <= 800) {
        lcd.write((byte)0); //happy face
      }
      else if(lux >= 800 && lux <= 2500) {
        lcd.write((byte)2); //neutral face
      }
      else if(lux > 2500) {
        lcd.write((byte)1); //sad face
      }
    }

    //moisture LCD display
    lcd.setCursor(11, 1);

    if (SoilMoisturePercentage <= 10)
    {
      lcd.write((byte)1); //sad face
    }
    else if (SoilMoisturePercentage <= 20)
    {
      lcd.write((byte)2); //neutral face
    }
    else if (SoilMoisturePercentage > 20 && SoilMoisturePercentage < 80)
    {
      lcd.write((byte)0); //smiley face
    }
    else if (SoilMoisturePercentage >= 80 && SoilMoisturePercentage < 90)
    {
      lcd.write((byte)2); //neutral face
    }
    else if (SoilMoisturePercentage >= 90)
    {
      lcd.write((byte)1); //sad face
    }

    delay(200);
}

void loop() {
  // button testing
  //Serial.println(digitalRead(buttonPin));
  int currentButtonState = digitalRead(buttonPin);

  // variable for temperature reading
  String tempReading;

  // variable for light reading
  String lightReading;

  //variable for moisture reading
  String moistureReading;

  //show emoticons on LCD display
  lcdDisplay();

  if (currentButtonState == 0) {
    //temperature sensor reading
    float temp = temperature.readTemperatureC();

    //brightness sensor reading
    /* Get a new sensor event */ 
    sensors_event_t event;
    tsl.getEvent(&event);
    lcd.setCursor(5, 1);

    /* Display the results (light is measured in lux) */
    float lux = event.light;

    //moisture sensor reading
    MoistureLevel = analogRead(A0);  //update based on the analog Pin selected
    SoilMoisturePercentage = map(MoistureLevel, OpenAirReading, WaterReading, 0, 100);

    // temperature section
    if(temp < 10) {
      //low temperature
      tempReading = "Temp: TOO LOW";
    }
    else if(temp < 18) {
      //low temperature
      tempReading = "Temp: SLIGHTLY LOW";
    }
    else if(temp >= 18 && temp <= 24) {
      //medium temperature
      tempReading = "Temp: GOOD";
    }
    else if(temp > 24 && temp < 30) {
      //high temperature
      tempReading = "Temp: SLIGHTLY HIGH";
    }
    else if(temp >= 30) {
      //high temperature
      tempReading = "Temp: TOO HIGH";
    }
    //======================

    // brightness section
    if (event.light)
    {
      if(lux < 200) {
        lightReading = "Light: TOO LOW";
      }
      else if(lux < 500) {
        lightReading = "Light: SLIGHTLY LOW";
      }
      else if(lux >= 500 && lux <= 800) {
        lightReading = "Light: GOOD";
      }
      else if(lux >= 800 && lux <= 2500) {
        lightReading = "Light: SLIGHTLY HIGH";
      }
      else if(lux > 2500) {
        lightReading = "Light: TOO HIGH";
      }
    }

    //moisture section
    if (SoilMoisturePercentage <= 10)
    {
      moistureReading = "Moisture: TOO LOW";
    }
    else if (SoilMoisturePercentage <= 20)
    {
      moistureReading = "Moisture: SLIGHTLY LOW";
    }
    else if (SoilMoisturePercentage > 20 && SoilMoisturePercentage < 80)
    {
      moistureReading = "Moisture: GOOD";
    }
    else if (SoilMoisturePercentage >= 80 && SoilMoisturePercentage < 90)
    {
      moistureReading = "Moisture: SLIGHTLY HIGH";
    }
    else if (SoilMoisturePercentage >= 90)
    {
      moistureReading = "Moisture: TOO HIGH";
    }

    //print out all readings
    Serial.println(tempReading + " " + lightReading + " " + moistureReading);
    
    while(digitalRead(buttonPin) == 0);
    delay(200);
  }
  //======================

}
