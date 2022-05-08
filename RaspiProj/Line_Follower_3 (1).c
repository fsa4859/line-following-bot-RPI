#include "simpletools.h"
#include "servo.h"
#include <stdbool.h>
#include <stdio.h>
#include "ping.h"

#define RIGHT_WHEEL_PIN             12
#define LEFT_WHEEL_PIN              13
#define LEFT_IR_PIN                 16
#define RIGHT_IR_PIN                17

#define ULTRASONIC_PIN              11
//#define LEFT_ULTRASONIC_PIN       0

#define OBJECT_DETECTION_LED        3
#define OBSTACLE_DETECTION_LED      5
#define INTERSECTION_DETECTION_LED  4

#define MAX_OBJECT_DISTANCE         15
#define MAX_OBSTACLE_DISTANCE       25

#define FORWARD_SPEED               40
#define STOP_SPEED                  0
#define ADJUST_SPEED                20
#define ADJUST_DELAY                10
#define TURN_SPEED                  50
#define TURN_DELAY                  1500
#define EXTRA_RIGHT_TURN_DELAY      300
#define REVERSE_DELAY               1500

// Headers
void followLine();
void detectObject();
void detectObstacle();
void handleIntersectionDetected();
void intersectionBlink();
void driveForward();
void adjustRight();
void adjustLeft();
void turnRight();
void turnLeft();
void stopWheels();
//void stopDriving();
void reverseDirection();
void reachObstacle();
void atA4();
void path_one();
void path_two();
void path_three();
void path_four();

// Cogs
volatile int *followLineCog;
//volatile int *detectObjectCog;
volatile int *detectObstacleCog;
volatile int *intersectionBlinkCog;
volatile int *pathDecisionCog;

static volatile int numIntersection = 0;
static volatile int numObjectsDetected = 0;
static volatile int numPath=0;
static volatile bool obstacleDetected = false;
static volatile bool lookForObstacle = true;
 
int main() {  
  followLineCog = cog_run(followLine, 128);
  //pathDecisionCog=cog_run(pathDecision,128);
  
  // Home to obstacle
  detectObstacleCog = cog_run(detectObstacle, 128);
  do    //decide path when you reach the obstacle
  {
    //Intersectionhandler will make it drive forward
    if(obstacleDetected)
    {
      if(numIntersection==3)
      {
        numPath=1;
      }
      else if(numIntersection==4)
      {
        numPath=2;
      }
      else if(numIntersection==6)
      {
        numPath=3;
      }
    }                             
  }while(!obstacleDetected);
 // for the next time
}  

void followLine() {
  while(1) {
    int leftIR = input(LEFT_IR_PIN);
    int rightIR = input(RIGHT_IR_PIN);
         
    if(leftIR == 1 && rightIR == 0) {
      adjustLeft();
    } else if(leftIR == 0 && rightIR == 1) {
      adjustRight();
    } else if(leftIR == 1 && rightIR == 1) {
      handleIntersectionDetected();
    } else {
      driveForward();
    }     
  }         
}  

void detectObstacle() 
{
  while(1) 
  {
    int cmDist=ping_cm(ULTRASONIC_PIN);
    obstacleDetected = cmDist != 0 && cmDist < MAX_OBSTACLE_DISTANCE;
    
    if(obstacleDetected) {
        high(OBSTACLE_DETECTION_LED);
        pause(750);
        low(OBSTACLE_DETECTION_LED);
        cog_end(detectObstacleCog);
        stopWheels();
        reverseDirection();
    } 
  }
}         

void handleIntersectionDetected() {
  numIntersection++;
  
  if(numIntersection==1) //clear the merge (change this later, the comparisions dont make sense)
  {
    driveForward();
    pause(110);
  }    
  else if(numIntersection > 1) {
    intersectionBlinkCog = cog_run(intersectionBlink, 128);
  }
  
  // after path has been decided in main use it to take correct turns
  //its a nested switch but broken up to look better
  switch(numPath) {
    
    // after a4 can add common path
    case 1:
      path_one();
      break;
      
    case 2:
      path_two();
      break;
      
    case 3:
      path_three();
      break;
    
    case 4:
      path_four();
      break;
    
    default:
      driveForward();
      pause(550);
      break;
    
  }
}

void intersectionBlink() {
  high(INTERSECTION_DETECTION_LED);
  pause(500);
  low(INTERSECTION_DETECTION_LED);
  
  cog_end(intersectionBlinkCog);
}

void driveForward() {
  servo_speed(RIGHT_WHEEL_PIN, FORWARD_SPEED * -1);
  servo_speed(LEFT_WHEEL_PIN, FORWARD_SPEED - 7);
}

void adjustRight() {
  servo_speed(RIGHT_WHEEL_PIN, STOP_SPEED);
  servo_speed(LEFT_WHEEL_PIN, ADJUST_SPEED);
  pause(ADJUST_DELAY);
}

void adjustLeft() {
  servo_speed(RIGHT_WHEEL_PIN, ADJUST_SPEED * -1);
  servo_speed(LEFT_WHEEL_PIN, STOP_SPEED);
  pause(ADJUST_DELAY);
}

void turnRight() {
  servo_speed(RIGHT_WHEEL_PIN, STOP_SPEED);
  servo_speed(LEFT_WHEEL_PIN, TURN_SPEED);
  pause(TURN_DELAY + EXTRA_RIGHT_TURN_DELAY);
}
 
void turnLeft() {
  servo_speed(RIGHT_WHEEL_PIN, TURN_SPEED * -1);
  servo_speed(LEFT_WHEEL_PIN, STOP_SPEED);
  pause(TURN_DELAY);
}
 
void stopWheels() {
  servo_speed(RIGHT_WHEEL_PIN, STOP_SPEED);
  servo_speed(LEFT_WHEEL_PIN, STOP_SPEED);
}

void reverseDirection(){
  servo_speed(RIGHT_WHEEL_PIN, TURN_SPEED);
  servo_speed(LEFT_WHEEL_PIN, TURN_SPEED);
  pause(REVERSE_DELAY); //play with this delay
  //todo
}  

void reachObstacle()
{
  driveForward();
  pause(400);
  obstacleDetected=false;
  detectObstacleCog = cog_run(detectObstacle, 128);
}   

void atA4()
{
  numIntersection=1;
  numPath=4;
} 

// obstacle at i2
void path_one(){
  
   switch(numIntersection) {
     
     case 4: // Back at i1
      turnRight();
      break;
     
     case 5: // B1
      turnRight();
      break;
      
     case 8: // B4
      turnRight();
      break;
     
     case 9: // i4
     // goto i5 and come back
      turnLeft();
      break;
     
     case 10:
      stopWheels();
      reverseDirection();
      break;

     case 12:
      // goto obstacle and turn
      reachObstacle();
      break;
     
     case 14:
      turnRight();
      atA4();
      break;
      //its all common after this can set numPath to 4
      
             
     default:
      driveForward();
      pause(550); // Clear intersection
      break;
  }
}   
  
  

// obstacle at i3
void path_two() 
{
  switch(numIntersection){
    case 6: // Back at i1
      turnRight();
      break;
    
    case 7: // B1
      turnRight();
      break;
    
    case 10 : // B4
      turnRight();
      break;
    
    case 11: // i4
      turnLeft();
      break;
      
    case 12:
      stopWheels();
      reverseDirection();
      break;
    
    case 13:
      reachObstacle();
      break;
    
    case 14:
      turnRight();
      atA4();
      break;
           
    default:
      driveForward();
      pause(550); // Clear intersection
      break;
  }  
}

// obstalce at i5
void path_three(){
  switch(numIntersection){
   
   case 10: // Back at i1
     turnRight();
     break;
   
   case 11: // B1
     turnRight();
     break;
   
   case 14: // B4
      turnRight();
      break;
      
   case 15:
      driveForward();
      pause(550);
      atA4();
      break;
            
  default:
      driveForward();
      pause(550); // Clear intersection
      break;
  } 
}        

void path_four()
{
  switch(numIntersection)
  {
    case 2:
      turnRight();
      break;
    case 5:
      turnRight();
      break;
      
    case 7:
      turnRight();
      break;
      
    case 11:
      stopWheels();  
      cog_end(followLineCog);
      break;
             
    default:
      driveForward();
      pause(550); // Clear intersection
      break;
  }
}