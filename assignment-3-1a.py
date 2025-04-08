from machine import Pin, PWM
from fifo import Fifo
import time
import micropython
micropython.alloc_emergency_exception_buf(200)

led=PWM(Pin(22))
led.freq(1000)
button=Pin(12, Pin.IN, Pin.PULL_UP)
brightness=0
led_on=False
last_pressed=0

class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a=Pin(rot_a,Pin.IN, Pin.PULL_UP)
        self.b=Pin(rot_b, Pin.IN, Pin.PULL_UP)
        self.fifo=Fifo(30, typecode='i')
        self.a.irq(handler= self.handler, trigger=Pin.IRQ_RISING, hard=True)
    def handler(self, pin):
        if self.b.value():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
rot =Encoder(10,11)
while True:
    now=time.ticks_ms()
    if button.value()==0: #pressed
        if time.ticks_diff(now, last_pressed)>100:
            last_pressed=now
            led_on= not led_on
            if led_on:
                led.duty_u16(brightness)  
            else:
                led.duty_u16(0)
                
    if rot.fifo.has_data():
        direction= rot.fifo.get()
        if led_on:
            if direction == 1 and brightness < 65535:  
                brightness += 1000
                brigghtness =min(brightness, 65535)
            elif direction == -1 and brightness > 0:  
                brightness -= 1000
                brightness = max(0, brightness)
            led.duty_u16(brightness)

    
    
        