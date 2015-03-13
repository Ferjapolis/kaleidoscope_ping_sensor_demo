#!/usr/bin/python
#
import time
import RPi.GPIO as GPIO
from neopixel import *

PING_TRIGGER    = 11      # Ping sensor trigger pin 
PING_ECHO       = 7       # Ping sensor echo pin
LED_COUNT 	= 14 	  # 2 x 7 NeoPixel Jewels
LED_PIN		= 18	  # Hardware PCM pin
LED_FREQ_HZ	= 800000  # LED frequency (800Khz)
LED_DMA		= 5	  # DMA channel
LED_BRIGHTNESS	= 15	  # Can go up to 255, but it's good to keep power usage low
LED_INVERT	= False	  # I believe this is for ws2811's

MAX_DISTANCE = 75
distance_buffer = []

# get a distance measurement from the ping sensor:
def measure():
  try:
    GPIO.output(PING_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(PING_TRIGGER, False)
    start = time.time()
    signaloff = start
    signalon = start
    while GPIO.input(PING_ECHO) == 0 and signaloff-start < 0.1:
      signaloff = time.time()
    while GPIO.input(PING_ECHO) == 1 and signalon-start < 0.1:
      signalon = time.time()
    timepassed = signalon - signaloff
    distance = timepassed * 17000
    return distance
  except UnboundLocalError, e:
    # Uh oh! Problem reading ping sensor... We probably go too close!
    return None

# average out the last few readings:
def reading():
  # add reading to the start of our buffer:
  reading = measure()
  if reading != None:
    distance_buffer.insert(0,reading)
  if len(distance_buffer) > 20:
    distance_buffer.pop()
  distance = sum(distance_buffer) / len(distance_buffer)
  return distance

# generate rainbow colors:
def wheel(pos, intensity=100):
  if pos < 85:
    r = ((pos * 3) * intensity ) / 100
    g = ((255 - pos * 3) * intensity ) / 100
    return Color(r, g, 0)
  elif pos < 170:
    pos -= 85
    r = ((255 - pos * 3) * intensity ) / 100
    b = ((pos * 3) * intensity ) / 100
    return Color(r, 0, b)
  else:
    pos -= 170
    g = ((pos * 3) * intensity ) / 100
    b = ((255 - pos * 3) * intensity ) / 100
    return Color(0, g, b)

if __name__ == '__main__':
  try: 
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PING_TRIGGER,GPIO.OUT)
    GPIO.setup(PING_ECHO,GPIO.IN)
    GPIO.output(PING_TRIGGER, False)
    step = 255/MAX_DISTANCE
    step2 = 255/7
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    while True:
      distance = reading()
      if distance > MAX_DISTANCE:
        distance = MAX_DISTANCE
      increment = step * distance
      for x in range(0,7):
        val = increment + (x * step2)
        if val > 255:
          val -= 255
        color = wheel( int(val), 100 )
        strip.setPixelColor( x, color )
        strip.setPixelColor( x+7, color )
      strip.show()
      time.sleep(0.01)

  finally:
    for x in range(0,14):
      strip.setPixelColor(x, Color(0,0,0))
    strip.show()
    GPIO.cleanup()
