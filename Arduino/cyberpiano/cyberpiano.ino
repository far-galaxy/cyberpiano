// CYBERPIANO Arduino sketch
// https://github.com/far-galaxy/cyberpiano

#define OCTAVES 4               // octaves count
#define KEYS 12                 // keys count (in 1 octave)
#define COUNT (KEYS*OCTAVES)
#define KEY_PIN 2               // first pin of keys
#define OCT_PIN 14              // first pin of octaves (A0)
#define FIRST_NOTE 36           // first note on keyboard (C3)

bool key_state[COUNT];


void setup() {

  Serial.begin(115200); // init serial

  // Init pins
  for (byte i = KEY_PIN ; i < KEY_PIN + KEYS; i++) {pinMode(i, OUTPUT); digitalWrite(i, HIGH);}
  for (byte i = OCT_PIN ; i < OCT_PIN + OCTAVES; i++){pinMode(i, INPUT_PULLUP);}
  


}


void loop() {  
  
   for (byte key = 0; key < KEYS; key++){
    
    digitalWrite(KEY_PIN + key, LOW); // enable key
    
    for (byte oct = 0; oct < OCTAVES; oct++){
      
      byte note = oct * KEYS + key;

      // check state in octaves
      if (digitalRead(OCT_PIN + oct) == LOW && key_state[note] == false){
        key_state[note] = true;
        sendMidi(note + FIRST_NOTE, 127); }
        
      if (digitalRead(OCT_PIN + oct) == HIGH && key_state[note] == true){
        key_state[note] = false;
        sendMidi(note + FIRST_NOTE, 0); }
    }
    
    digitalWrite(KEY_PIN + key, HIGH); // disable key
   }

}

// Midi signal
void sendMidi(byte note, byte velocity) {
  Serial.write(0x90); // MIDI Note-on channel 1 
  Serial.write(note); // MIDI note pitch 60 
  Serial.write(velocity); // MIDI note velocity 0
}
