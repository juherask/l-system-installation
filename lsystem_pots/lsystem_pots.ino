int ledPin = 13;   // select the pin for the LED
int buttonPin = 12;


#define MOVING_AVERAGE_LENGTH 10
// According to the section 6.7.8.21 of the C specification, this should set the array to 0
int value_buffers[4][MOVING_AVERAGE_LENGTH]={0};
int value_buffer_idxs[4]={0,0,0,0};
float moving_averages[4]={0.0f,0.0f,0.0f,0.0f};

bool button_down = false;
bool button_update_sent = false;
unsigned long button_down_time;

void setup() {
  pinMode(ledPin, OUTPUT);  // declare the ledPin as an OUTPUT

  pinMode(buttonPin, INPUT);    // button as input
  digitalWrite(buttonPin, HIGH); // turns on pull-up resistor after input

  Serial.begin(9600);
}

void loop() {
  for(int i=0; i<4; i++)
  {
    // read value
    int val = analogRead(i);
    value_buffers[i][value_buffer_idxs[i]] = val;
    
    value_buffer_idxs[i]++;
    if (value_buffer_idxs[i]==MOVING_AVERAGE_LENGTH)
      value_buffer_idxs[i]=0;

    //update the average
    moving_averages[i] = 0.0f;
    for(int j=0; j<MOVING_AVERAGE_LENGTH ; j++)
      moving_averages[i]+=(float)value_buffers[i][j]/(float)MOVING_AVERAGE_LENGTH;
  }

  bool print_values = false;
  if (digitalRead(buttonPin) == LOW)
  {
    if (!button_down)
    {
      button_down_time = millis();
    }
    else if (millis()-button_down_time>1000)
    {
      button_down_time+=200;
      button_update_sent=true;
      
      // update command
      Serial.print("u");
      print_values=true;
    }
      
    // button was pressed (or is pressed)
    button_down = true;
  }
  else if (button_down)
  {
    // button was released
    button_down = false;

    if (!button_update_sent)
    {
      // redraw command
      Serial.print("n");
      print_values = true;
    }
    button_update_sent = false;
  }

  if (print_values)
  {
    for(int i=0; i<4; i++)
    {
      Serial.print(";");
      char buffer[50];
      int out_len=sprintf (buffer, "%04d", (int)moving_averages[i]);
      for(int l= 0; l<=out_len-1; l++) 
        Serial.print(buffer[l]);
    }
    Serial.println();
  }
  
  // avoid static and bounce
  delay(50);
}

