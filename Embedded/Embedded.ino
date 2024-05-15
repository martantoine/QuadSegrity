#define COMMAND_BYTES_LEN 4
#define OBSERVATION_BYTES_LEN 24

#define CONTROL_DELAY 500

#define VALVE_0 2
#define VALVE_1 2
#define VALVE_2 2
#define VALVE_3 2
#define VALVE_4 2
#define VALVE_5 2
#define VALVE_6 2
#define VALVE_7 2
#define VALVE_8 2
#define VALVE_9 2

#define REGULATOR_0 3
#define REGULATOR_1 4

#define PRESSURE_SENSOR_0 A0
#define PRESSURE_SENSOR_1 A1

static uint8_t regulator0 = 0;
static uint8_t regulator1 = 0;

#ifdef USE_IMU
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* This driver uses the Adafruit unified sensor library (Adafruit_Sensor),
   which provides a common 'type' for sensor data and some helper functions.

   To use this driver you will also need to download the Adafruit_Sensor
   library and include it in your libraries folder.

   You should also assign a unique ID to this sensor for use with
   the Adafruit Sensor API so that you can identify this particular
   sensor in any data logs, etc.  To assign a unique ID, simply
   provide an appropriate value in the constructor below (12345
   is used by default in this example).

   Connections
   ===========
   Connect SCL to analog 5
   Connect SDA to analog 4
   Connect VDD to 3.3-5V DC
   Connect GROUND to common ground

   History
   =======
   2015/MAR/03  - First release (KTOWN)
*/

/* Set the delay between fresh samples */
uint16_t BNO055_SAMPLERATE_DELAY_MS = 100;
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28, &Wire);
#endif

void init_robot(void)
{
    pinMode(VALVE_0, OUTPUT);
    pinMode(VALVE_1, OUTPUT);
    pinMode(VALVE_2, OUTPUT);
    pinMode(VALVE_3, OUTPUT);
    pinMode(VALVE_4, OUTPUT);
    pinMode(VALVE_5, OUTPUT);
    pinMode(VALVE_6, OUTPUT);
    pinMode(VALVE_7, OUTPUT);
    pinMode(VALVE_8, OUTPUT);
    pinMode(VALVE_9, OUTPUT);
    pinMode(REGULATOR_0, OUTPUT);
    pinMode(REGULATOR_1, OUTPUT);

    pinMode(PRESSURE_SENSOR_0, INPUT);
    pinMode(PRESSURE_SENSOR_1, INPUT);
    Serial.begin(115200);

#ifdef USE_IMU
    if (!bno.begin())
    {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!\n");
        while (1);
    }

#endif
    Serial.println("Reset successful");
    delay(1000);
}

void setup()
{
    init_robot();
}

void loop()
{
    uint8_t command_bytes[COMMAND_BYTES_LEN];
    
    // Always take the last order sent (consisting of 4 bytes)
    while(Serial.available() > COMMAND_BYTES_LEN)
        Serial.readBytes(command_bytes, COMMAND_BYTES_LEN);
    uint32_t command = (command_bytes[3] << 8*3) | (command_bytes[2] << 8*2) | (command_bytes[1] << 8) | command_bytes[0];
    // 16 bits for the regulators, 10 bits for the valves
    uint16_t valve_command = command & 0xFF;

    if(command == 0xFFFFFFFF)
        init_robot();
    else
    {
        digitalWrite(VALVE_0, (valve_command >> 0) & 0x1);
        digitalWrite(VALVE_1, (valve_command >> 1) & 0x1);
        digitalWrite(VALVE_2, (valve_command >> 2) & 0x1);
        digitalWrite(VALVE_3, (valve_command >> 3) & 0x1);
        digitalWrite(VALVE_4, (valve_command >> 4) & 0x1);
        digitalWrite(VALVE_5, (valve_command >> 5) & 0x1);
        digitalWrite(VALVE_6, (valve_command >> 6) & 0x1);
        digitalWrite(VALVE_7, (valve_command >> 7) & 0x1);
        digitalWrite(VALVE_8, (valve_command >> 8) & 0x1);
        digitalWrite(VALVE_9, (valve_command >> 9) & 0x1);
     
        regulator0 = (command >> 10) & 0xFF;
        regulator1 = (command >> 18) & 0xFF;
        
	    delay(CONTROL_DELAY);
    }
    uint16_t observation[int(OBSERVATION_BYTES_LEN/2)];
    observation[0] = 0;//valve_command;
    observation[1] = 0;//analogRead(PRESSURE_SENSOR_0);
    observation[2] = 0;//analogRead(PRESSURE_SENSOR_1);
    
#ifdef USE_IMU
    sensors_event_t orientationData , angVelocityData , linearAccelData;
    bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
    bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
    bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);

    observation[3] = orientationData.orientation.x;
    observation[4] = orientationData.orientation.y;
    observation[5] = orientationData.orientation.z;
    
    observation[6] = orientationData.gyro.x;
    observation[7] = orientationData.gyro.y;
    observation[8] = orientationData.gyro.z;
    
    observation[9] = orientationData.acceleration.x;
    observation[10] = orientationData.acceleration.y;
    observation[11] = orientationData.acceleration.z;
#endif
    Serial.write((uint8_t*)observation, OBSERVATION_BYTES_LEN);
}