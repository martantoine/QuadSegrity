#include <math.h>
#include <Adafruit_MPU6050.h>

#define COMMAND_BYTES_LEN 4
#define OBSERVATION_BYTES_LEN 24

#define CONTROL_DELAY 500

//0
#define VALVE_RL_K 3
#define VALVE_RL_H 2
//1
#define VALVE_FR_H 4
#define VALVE_FR_K 5
//2
#define VALVE_FL_K 6
#define VALVE_FL_H 7
//3
#define VALVE_RR_K 9
#define VALVE_RR_H 8

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
    pinMode(VALVE_RR_K, OUTPUT);
    pinMode(VALVE_RR_H, OUTPUT);
    pinMode(VALVE_FR_H, OUTPUT);
    pinMode(VALVE_FR_K, OUTPUT);
    pinMode(VALVE_FL_K, OUTPUT);
    pinMode(VALVE_FL_H, OUTPUT);
    pinMode(VALVE_RL_H, OUTPUT);
    pinMode(VALVE_RL_K, OUTPUT);
    
    /*
 	mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
 	mpu.setGyroRange(MPU6050_RANGE_250_DEG);
 	mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    calibrate();
    */

    /*
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
    */
}



void setup()
{
    Serial.begin(115200);
    init_robot();
}

int seq[] = {0, 2, 3, 1};
int lasti = 0;

void release_ik(int i)
{
    if((i == 1) || (i == 2))
        digitalWrite(2+(lasti * 2), LOW);
    else
        digitalWrite(2+(lasti * 2)+1, LOW);
}

void release_ih(int i)
{
    if((i == 0) || (i == 3))
        digitalWrite(2+(lasti * 2), LOW);
    else
        digitalWrite(2+(lasti * 2)+1, LOW);
}

void loop()
{
    for(int i=0; i < 4; i++)
    {
        switch (seq[i]) {
            case 0:
                digitalWrite(VALVE_RR_K, HIGH);
                digitalWrite(VALVE_RR_H, HIGH);
                delay(500);
                release_ik(i);
                delay(500);
                release_ih(i);
                lasti = 0;
            break;
            case 1:
                digitalWrite(VALVE_FR_K, HIGH);
                digitalWrite(VALVE_FR_H, HIGH);
                delay(500);
                release_ik(i);
                delay(500);
                release_ih(i);
                lasti = 1;
            break;
            case 2:
                digitalWrite(VALVE_FL_K, HIGH);
                digitalWrite(VALVE_FL_H, HIGH);
                delay(500);
                release_ik(i);
                delay(500);
                release_ih(i);
                lasti = 2;
                break;
            case 3:
                digitalWrite(VALVE_RL_K, HIGH);
                digitalWrite(VALVE_RL_H, HIGH);
                delay(500);
                release_ik(i);
                delay(500);
                release_ih(i);
                lasti = 3;
                break;
        }
        delay(500);
        
    }
    
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