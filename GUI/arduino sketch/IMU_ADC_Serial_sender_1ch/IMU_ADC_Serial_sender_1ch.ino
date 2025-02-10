#include <math.h>

#include <Wire.h>
//#include <LSM6.h>
#include <Kalman.h>

///
#include "MPU6050.h"
MPU6050 accelgyro;
int16_t accX, accY, accZ;
int16_t gyroX, gyroY, gyroZ;
//int16_t ax, ay, az;
//int16_t gx, gy, gz;
#define OUTPUT_READABLE_ACCELGYRO

#define LED_PIN 13
bool blinkState = false;

//Filter
//Angle
Kalman kalmanX;
Kalman kalmanY;

double gyroXangle, gyroYangle; // Angle calculate using the gyro only
double compAngleX, compAngleY; // Calculated angle using a complementary filter
double kalAngleX, kalAngleY; // Calculated angle using a Kalman filter
double kalDAngleX, kalDAngleY;

uint32_t timer;

//Velocity
double velX, velY, velZ = 0;
double comVelX, comVelY, comVelZ = 0;

double comAccX,comAccY,comAccZ=0;  
double gravityX, gravityY, gravityZ=0;

const double alpha = 0.8;//lowpassfilter

//Log
char report[80];

double vec[3];

double a[10] = {0,0,0,0,0,0,0,0,0,0};
double b[10] = {0,0,0,0,0,0,0,0,0,0};
double AVERAGEX = 0;
double AVERAGEY = 0;


void setup() {
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
  #endif

  Serial.begin(115200);

  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();

  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

  // configure Arduino LED pin for output
  pinMode(LED_PIN, OUTPUT);


  ///
  accelgyro.getMotion6(&accX, &accY, &accZ, &gyroX, &gyroY, &gyroZ);
  

  double roll  = atan2(accY, accZ) * RAD_TO_DEG;
  double pitch = -atan2(accX, sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;

  kalmanX.setAngle(roll); // Set starting angle
  kalmanY.setAngle(pitch);
  gyroXangle = roll;
  gyroYangle = pitch;
  compAngleX = roll;
  compAngleY = pitch;

  timer = micros();


}

void loop() {
  accelgyro.getMotion6(&accX, &accY, &accZ, &gyroX, &gyroY, &gyroZ);
  //

    double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
  timer = micros();

  /*角度を求める kalman Filter*/
  double roll  = atan2(accY, accZ) * RAD_TO_DEG;
  double pitch = -atan2(accX, sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
  
  double gyroXrate = gyroX / 131.0; // Convert to deg/s
  double gyroYrate = gyroY / 131.0; // Convert to deg/s

  if ((roll < -90 && kalAngleX > 90) || (roll > 90 && kalAngleX < -90)) {
    kalmanX.setAngle(roll);
    compAngleX = roll;
    kalAngleX = roll;
    gyroXangle = roll;
  } else
    kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleX) > 90)
    gyroYrate = -gyroYrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt);

  gyroXangle += gyroXrate * dt; // Calculate gyro angle without any filter
  gyroYangle += gyroYrate * dt;
//  gyroXangle += kalmanX.getRate() * dt; // Calculate gyro angle using the unbiased rate
//  gyroYangle += kalmanY.getRate() * dt;

  compAngleX = 0.93 * (compAngleX + gyroXrate * dt) + 0.07 * roll; // Calculate the angle using a Complimentary filter
  compAngleY = 0.93 * (compAngleY + gyroYrate * dt) + 0.07 * pitch;

  // Reset the gyro angle when it has drifted too much
  if (gyroXangle < -180 || gyroXangle > 180)
    gyroXangle = kalAngleX;
  if (gyroYangle < -180 || gyroYangle > 180)
    gyroYangle = kalAngleY;

  /*速度を求める*/
  // 重力加速度を求める
  gravityX = alpha * gravityX + (1 - alpha) * accX;
  gravityY = alpha * gravityY + (1 - alpha) * accY;
  gravityZ = alpha * gravityZ + (1 - alpha) * accZ;

  // 補正した加速度
  comAccX = accX - gravityX;
  comAccY = accY - gravityY;
  comAccZ = accZ - gravityZ;

  if(abs(comAccX) < 100)comAccX = 0;
  if(abs(comAccY) < 100)comAccY = 0;
  if(abs(comAccZ) < 100)comAccZ = 0;

  velX = velX + comAccX*dt;
  velY = velY + comAccY*dt;
  velZ = velZ + comAccZ*dt;

  kalAngleX = kalAngleX + 90;
  kalAngleY = kalAngleY + 90;

  if(pitch > 0){
    pitch = pitch +90; //50
  }
  if(pitch <= 0){
    pitch = pitch +90;
  }

  a[9] = kalAngleX;
      for(int j=0; j<9; j++){
        a[j] = a[j+1];
        //Serial.print(a[j]);
        
        AVERAGEX = AVERAGEX + a[j];
      }
      //Serial.println("end");
    
        AVERAGEX = AVERAGEX + a[9];

        //Serial.println(a[0][1]);
        AVERAGEX = AVERAGEX/11;
  
      b[9] = pitch;
      
      if(isnan(b[9])){
        b[9] = b[8];
      }
  
      for(int j=0; j<9; j++){
        b[j] = b[j+1];
        //Serial.print(a[j]);
        
        AVERAGEY = AVERAGEY + b[j];
      }
      //Serial.println("end");
    
        AVERAGEY = AVERAGEY + b[9];

        //Serial.println(a[0][1]);
        AVERAGEY = AVERAGEY/11;


  /*print*/
  //Serial.print(velX); Serial.print("\t");
  //Serial.print(velY); Serial.print("\t");
  //Serial.print(velZ); Serial.print("\t");
  //Serial.print(comAccX); Serial.print("\t");
  //Serial.print(comAccY); Serial.print("\t");
  //Serial.print(comAccZ); Serial.print("\t");
    
  //Serial.print(roll); Serial.print("\t");
  //Serial.print(gyroXangle); Serial.print("\t");
  //Serial.print(compAngleX); Serial.print("\t");
  //Serial.print(kalAngleX); Serial.print("\t");
  Serial.print(AVERAGEX); Serial.print("\t");

  Serial.print("\t");

 // Serial.print(pitch); Serial.print("\t");
  Serial.print(AVERAGEY); Serial.print("\t");
  //Serial.print(gyroYangle); Serial.print("\t");
  //Serial.print(compAngleY); Serial.print("\t");
  //Serial.print(kalAngleY); Serial.print("\t");

  Serial.print("\r\n");

  delay(50);



  // read the input on analog pin 0:
  // analog reading (which goes from 0 - 1023)
  //int sensorValue0 = analogRead(A0);
  // if you read more data
  // int sensorValue1 = analogRead(A1);

  // print out the value you read:
  //Serial.println(sensorValue0);
  // if you read more data
  // Serial.print(",");
  // Serial.println(sensorValue1);

  // sampling rate 1 / 10 milli seconds = 100Hz
  
}
