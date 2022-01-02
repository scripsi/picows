
import time
import board
import digitalio
from analogio import AnalogIn
import adafruit_rgbled
import busio
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
import math

# Press "B" to speed up the LED cycling effect.
# Press "A" to slow it down again.
# Press "Boot" to reset the speed back to default.

# Set how many LEDs you have
NUM_LEDS = 60

# The speed that the LEDs will start cycling at
DEFAULT_GAMMA = 2.1

# How many times the LEDs will be updated per second
UPDATES = 2

# How bright the LEDs will be (between 0.0 and 1.0)
BRIGHTNESS = 0.5

# Pick *one* LED type by uncommenting the relevant line below:

# APA102 / DotStar™ LEDs
# led_strip = dotstar.DotStar(board.CLK, board.DATA, NUM_LEDS, brightness=BRIGHTNESS)

# WS2812 / NeoPixel™ LEDs
led_strip = neopixel.NeoPixel(board.DATA, NUM_LEDS, brightness=BRIGHTNESS, auto_write=False)

user_sw = digitalio.DigitalInOut(board.USER_SW)
user_sw.direction = digitalio.Direction.INPUT
user_sw.pull = digitalio.Pull.UP

sw_a = digitalio.DigitalInOut(board.SW_A)
sw_a.direction = digitalio.Direction.INPUT
sw_a.pull = digitalio.Pull.UP

sw_b = digitalio.DigitalInOut(board.SW_B)
sw_b.direction = digitalio.Direction.INPUT
sw_b.pull = digitalio.Pull.UP

led = adafruit_rgbled.RGBLED(board.LED_R, board.LED_G, board.LED_B, invert_pwm = True)

sense = AnalogIn(board.CURRENT_SENSE)

# Constants used for current conversion
ADC_GAIN = 50
SHUNT_RESISTOR = 0.015 # Yes, this is 0.015 Ohm

def get_voltage(pin):
  return (pin.value * 3.3) / 65536

def get_current(pin):
  return get_voltage(pin) / (ADC_GAIN * SHUNT_RESISTOR)

def button_read(button):
  return not button.value

gamma = DEFAULT_GAMMA
angle = 0.0
delta_angle = 360/(UPDATES * 60)
pixels_on = True

count = 0
# Make a gradient
while True:
  sw = not user_sw.value
  a = not sw_a.value
  b = not sw_b.value

  if sw:
    pixels_on = not pixels_on
  else:
    if a:
      gamma -= 0.1
    if b:
      gamma += 0.1

  gamma = min(4.0, max(1, gamma))

  if pixels_on:
    # build clock face
    for i in range(NUM_LEDS):
      led_color = fancy.CRGB(50,50,100)
      led_strip[i] = fancy.gamma_adjust(led_color).pack()
    for i in range(0,NUM_LEDS,5):
      led_color = fancy.CRGB(150,150,150)
      led_strip[i] = fancy.gamma_adjust(led_color).pack()
    s = int((angle/360)*NUM_LEDS)
    led_color = fancy.CRGB(255,0,0)
    led_strip[s] = fancy.gamma_adjust(led_color).pack()
  else:
    for i in range(NUM_LEDS):
      led_strip[i] = (0,0,0)
  led_strip.show()

  count += 1
  if count >= UPDATES:
    # Display the current value once every second
    print("Current =", get_current(sense), "A")
    print("angle =", angle)
    count = 0
  angle += delta_angle
  if angle > 360:
    angle -= 360
  time.sleep(1.0 / UPDATES)
