#!/usr/bin/python
#
import time
import RPi.GPIO as GPIO
from neopixel import *

PING_TRIGGER     = 11		# Ping sensor trigger pin 
PING_ECHO        = 7		# Ping sensor echo pin
PING_BUFFER_SIZE = 15		# How many distance measurements to average against
LED_COUNT 	 = 14		# 2 x 7 NeoPixel Jewels
LED_PIN		 = 18		# Hardware PCM pin
LED_FREQ_HZ	 = 800000	# LED frequency (800Khz)
LED_DMA		 = 5		# DMA channel
LED_BRIGHTNESS	 = 15		# Can go up to 255, but it's good to keep power usage low
LED_INVERT	 = False	# I believe this is for ws2811's

MAX_DISTANCE = 50 
signaloff = 0
signalon = 0
distance_buffer = []

def echoCallback(channel):
  global distance_buffer
  global signalon
  global signaloff
  if GPIO.input(channel) == 1:
    signalon = time.time()
    return
  signaloff = time.time()
  timepassed = signaloff - signalon
  distance = timepassed * 17000
  if distance > 0 and distance < 300:
    distance_buffer.insert(0,distance)
  if len(distance_buffer) > PING_BUFFER_SIZE:
    distance_buffer.pop()

# average out the last few readings:
def reading():
  if distance_buffer != []:
    distance = sum(distance_buffer) / len(distance_buffer)
    return distance
  else: 
    return None

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
    GPIO.add_event_detect(PING_ECHO, GPIO.BOTH, callback=echoCallback)
    step = 255.0/MAX_DISTANCE
    step2 = 255.0/7.0
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    while True:
      GPIO.output(PING_TRIGGER, True)
      time.sleep(0.00001)
      GPIO.output(PING_TRIGGER, False)
      time.sleep(0.05) # allow callbacks to process
      distance = reading()
      #print "Distance: %s" % distance
      if distance != None:
        if distance > MAX_DISTANCE:
          distance = MAX_DISTANCE
        increment = step * distance
        for x in range(1,7):
          val = increment + ((x+1) * step2)
          if val > 255:
            val -= 255
          color = wheel( int(val), 100 )
          strip.setPixelColor( x, color )
          strip.setPixelColor( x+7, color )
        strip.show()
  except Exception, e:
    print "Exception: %s" % e
    raise
  finally:
    for x in range(0,14):
      strip.setPixelColor(x, Color(0,0,0))
    strip.show()
    GPIO.cleanup()
