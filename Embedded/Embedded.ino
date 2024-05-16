#include <math.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

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
float aX = 0.0f, aY = 0.0f, aZ = 0.0f, gX = 0.0f, gY = 0.0f, gZ = 0.0f;

typedef union {
  float floatingPoint;
  byte binary[4];
} binaryFloat;


Adafruit_MPU6050 mpu;


#define MPU6050_I2C_ADDRESS 0x68
#define FREQ  20.0 // sample freq in Hz

#define gSensitivity 131
static float ax, ay, az;
static float pitch = 0.0, yaw = 0.0, roll = 0.0;
static float gyrXoffs, gyrYoffs, gyrZoffs;

static unsigned long start_time = 0;

void loop()
{
    unsigned long old_start_time = start_time;
    start_time = micros();
    digitalWrite(3, digitalRead(3) ^ 1);
    sensors_event_t a, g, temp;
 	mpu.getEvent(&a, &g, &temp);
    
    // angles based on accelerometer
    ax = a.acceleration.x;
    ay = a.acceleration.y;
    az = a.acceleration.z;

    // angles based on gyro (deg/s)
    float dt = float(start_time - old_start_time);
    //Serial.println(dt);
    roll  = roll  + (g.gyro.x) *180 / M_PI * dt / 1.0e6;
    pitch = pitch - (g.gyro.y) *180 / M_PI * dt / 1.0e6;
    yaw   = yaw   + (g.gyro.z) *180 / M_PI * dt / 1.0e6;

    float gravity_y = atan2(ax, sqrt(pow(ay, 2) + pow(az, 2))) * 180 / M_PI;
    float gravity_x = atan2(ay, sqrt(pow(ax, 2) + pow(az, 2))) * 180 / M_PI;
    // complementary filter, tau = DT*(A)/(1-A) = 0.48sec
    roll = roll * 0.96 + gravity_x * 0.04;
    pitch = pitch * 0.96 + gravity_y * 0.04;
    
    unsigned int st = 20 - (micros() - start_time) / 1000;
    delay(st);
}


void calibrate()
{
    float xSum = 0.0, ySum = 0.0, zSum = 0.0;
 	sensors_event_t a, g, temp;
    
    for (int x = 0; x < 100; x++)
    {
        mpu.getEvent(&a, &g, &temp);
        delay(10);

        xSum += g.gyro.x;
        ySum += g.gyro.y;
        zSum += g.gyro.z;
    }
    
    gyrXoffs = xSum / 100;
    gyrYoffs = ySum / 100;
    gyrZoffs = zSum / 100;  
}

void init_robot(void)
{
    pinMode(4, OUTPUT);
    pinMode(3, OUTPUT);/*/
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
    pinMode(PRESSURE_SENSOR_1, INPUT);*/
    Serial.begin(115200);

    if (!mpu.begin(0x68)) { // Change address if needed
        Serial.println("Failed to find MPU6050 chip");
        while (1) {
                delay(10);
        }
 	}
 	mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
 	mpu.setGyroRange(MPU6050_RANGE_250_DEG);
 	mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    calibrate();
    
    TCCR3A = 0;
    TCCR3B = 0;
    TCNT3 = 0;

    // 2 Hz (16000000/((31249+1)*256))
    OCR3A = 6250;

    // CTC
    TCCR3B |= (1 << WGM32);
    // Prescaler 256
    TCCR3B |= (1 << CS32);
    // Output Compare Match A Interrupt Enable
    TIMSK3 |= (1 << OCIE3A);
    interrupts();

    Serial.println("Reset successful");
    start_time = micros();
}

ISR(TIMER3_COMPA_vect) 
{
    TCNT3 = 0;
    comm();
}

void setup()
{
    init_robot();
}

binaryFloat observationf[6];
int i = 0;

void comm()
{
    digitalWrite(4, HIGH);
    
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
    }
    uint8_t observation[4];
    uint16_t p0 = 0;//analogRead(PRESSURE_SENSOR_0);
    uint16_t p1 = 0;//analogRead(PRESSURE_SENSOR_1);
    observation[0] = 0;//valve_command & 0b11111111;
    observation[1] = 0;//((valve_command >> 8) & 0b11) | ((p0 << 2) & 0b11111100);
    observation[2] = 0;//((p0 >> 6) & 0b1111) | ((p1 << 4) & 0b11110000);
    observation[3] = 0;//((p1 >> 4) & 0b111111);
    Serial.print("i");
    Serial.write(observation, 4);
    
    observationf[0].floatingPoint = 0;
    observationf[1].floatingPoint = 0;
    observationf[2].floatingPoint = 0;
    
    observationf[3].floatingPoint = roll;
    observationf[4].floatingPoint = pitch;
    observationf[5].floatingPoint = yaw;
 
    for (int i = 0; i < 6; i++)
    {
        //Serial.print("f");
        Serial.write(observationf[i].binary, 4);
        //Serial.print(observationf[i].floatingPoint);
        
    }
    Serial.println(i, DEC);
    i+=1; 
    auto end_time = millis();
    digitalWrite(4, LOW);
 }