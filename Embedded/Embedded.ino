#include <math.h>
#include <Adafruit_MPU6050.h>

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

typedef union {
    float floatingPoint;
    byte binary[4];
} binaryFloat;



static Adafruit_MPU6050 mpu;

#define MPU6050_I2C_ADDRESS 0x68
#define FREQ  20.0 // sample freq in Hz
#define gSensitivity 131

static float ax, ay, az;
static float pitch = 0.0, yaw = 0.0, roll = 0.0;
static float gyrXoffs, gyrYoffs, gyrZoffs;

static unsigned long start_time = 0;

void calibrate()
{
    float xSum = 0.0, ySum = 0.0, zSum = 0.0;
 	sensors_event_t a, g, temp;
    
    for (int x = 0; x < 100; x++)
    {
        mpu.getEvent(&a, &g, &temp);
        //delay(10);

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
    pinMode(3, OUTPUT);
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);
    pinMode(8, OUTPUT);

    /*
 	mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
 	mpu.setGyroRange(MPU6050_RANGE_250_DEG);
 	mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    calibrate();
    */

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
    Serial.print("Reset successful\n");

    interrupts();
    start_time = micros();
}



void setup()
{
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);

    Serial.begin(115200);
    //init_robot();
}

void loop()
{
    digitalWrite(5, HIGH);
    digitalWrite(7, HIGH);
    delay(3000);
    digitalWrite(5, LOW);
    digitalWrite(7, LOW);
    delay(5000);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
    delay(3000);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    
    /*if (Serial.available() > 0) {
        long myInt = Serial.parseInt(SKIP_WHITESPACE);
        if(myInt != -1)
        {
            // prints the received integer
            Serial.print("I received: ");
            Serial.println(myInt);
        }
    }*/
    // digitalW
    // unsigned long old_start_time = start_time;
    // start_time = micros();
    // digitalWrite(3, digitalRead(3) ^ 1);
    // //sensors_event_t a, g, temp;
    // //mpu.getEvent(&a, &g, &temp);
    
    // // angles based on accelerometer
    // ax = 0;//a.acceleration.x;
    // ay = 0;//a.acceleration.y;
    // az = 0;//a.acceleration.z;

    // // angles based on gyro (deg/s)
    // float dt = float(start_time - old_start_time);
    
    // roll  = roll  + (0 - gyrXoffs) *180 / M_PI * dt / 1.0e6;
    // pitch = pitch - (0 - gyrYoffs) *180 / M_PI * dt / 1.0e6;
    // yaw   = yaw   + (0 - gyrZoffs) *180 / M_PI * dt / 1.0e6; // helplessly drifting away through time

    // float gravity_pitch = atan2(ax, sqrt(pow(ay, 2) + pow(az, 2))) * 180 / M_PI; 
    // float gravity_roll  = atan2(ay, sqrt(pow(ax, 2) + pow(az, 2))) * 180 / M_PI;
    // float gravity_yaw   = atan2(az, sqrt(pow(ax, 2) + pow(az, 2))) * 180 / M_PI;
    // // complementary filter, tau = DT*(A)/(1-A) = 0.48sec
    // roll  = roll  * 0.96 + gravity_roll  * 0.04;
    // pitch = pitch * 0.96 + gravity_pitch * 0.04;
    
    // unsigned int st = 20 - (micros() - start_time) / 1000;
    // delay(st);
}


void comm()
{/*
    if (Serial.available() > 0) {
        long myInt = Serial.parseInt(SKIP_ALL);

        // prints the received integer
        Serial.print("I received: ");
        Serial.println(myInt);
    }*/
    // digitalWrite(4, digitalRead(4) ^ 1);
    
    // uint32_t command = 0;
    
    // digitalWrite(8, LOW);
    // while(Serial.available() > 0) // Always take the last order sent (consisting of 4 bytes)
    // {
    //     digitalWrite(8, HIGH);
    //     command = Serial.parseInt(SKIP_ALL, '\n');
    //     Serial.println(command);
    // }
    // // while(Serial.available())
    //     Serial.read();
    //uint32_t command = (command_bytes[3] << 8*3) | (command_bytes[2] << 8*2) | (command_bytes[1] << 8) | command_bytes[0];
    
    // if((command >> 26) == 0b10)
    // {
    //     init_robot();
    //     return;
    // }
    // else if((command >> 26) == 0b1)
    // {
    //     digitalWrite(5, digitalRead(5) ^ 1);
    //     //digitalWrite(5, (command >> 0) & 1);
    //     digitalWrite(6, (command >> 1) & 1);
    //     digitalWrite(7, (command >> 2) & 1);
    // }
    
    uint8_t observation[4] = {0, 0, 0, 0};
    binaryFloat observationf[6];
    observationf[0].floatingPoint = ax;
    observationf[1].floatingPoint = ay;
    observationf[2].floatingPoint = az;

    observationf[3].floatingPoint = roll;
    observationf[4].floatingPoint = pitch;
    observationf[5].floatingPoint = yaw; // better not to use this one

    /*Serial.print("start\n");
    Serial.write(observation, 4);
    for (int i = 0; i < 6; i++)
        Serial.write(observationf[i].binary, 4);*/
}

ISR(TIMER3_COMPA_vect) 
{
    TCNT3 = 0;
    comm();
}