#include <TinyMLShield.h>

// Image buffer for QCIF: 176x144 x 2 bytes per pixel (RGB565)
byte image[176 * 144 * 2];
int bytesPerFrame;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  initializeShield();

  // Initialize the OV7675 camera
  if (!Camera.begin(QCIF, RGB565, 1, OV7675)) {
    //Serial.println("Failed to initialize camera");
    while (1);
  }
  
  bytesPerFrame = Camera.width() * Camera.height() * Camera.bytesPerPixel();
  
  //Serial.println("Camera initialized - Starting auto video capture...");
  delay(2000); // Give Python time to connect
}

void loop() {
  // Continuously capture and send frames
  Camera.readFrame(image);
  Serial.write(image, bytesPerFrame);
  
  // Small delay to control frame rate (adjust as needed)
  delay(100); // ~10 FPS
}