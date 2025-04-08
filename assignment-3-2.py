from machine import Pin, I2C
import time
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import micropython
micropython.alloc_emergency_exception_buf(200)

button=Pin(12, Pin.IN, Pin.PULL_UP)
led1=Pin(20, Pin.OUT)
led2=Pin(21, Pin.OUT)
led3=Pin(22, Pin.OUT)
led_state=[False, False, False]


selected=0
last_pressed=0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a=Pin(rot_a,Pin.IN, Pin.PULL_UP)
        self.b=Pin(rot_b, Pin.IN, Pin.PULL_UP)
        self.fifo=Fifo(50, typecode='i')
        self.a.irq(handler= self.handler, trigger=Pin.IRQ_RISING, hard=True)
    def handler(self, pin):
        if self.b.value():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
rot =Encoder(10,11)


def update_display():
    oled.fill(0)
    menu = ['LED1','LED2','LED3']
    for i in range(3):
        if led_state[i]:
            state='ON'
        else:
            state='OFF'

        oled.text(f'{menu[i]} - {state}',20, 10 + i * 10)
    oled.text("=>",0, 10 + selected * 10)
    oled.show()
    
def led_toggle():
    global selected
    led_state[selected]= not led_state[selected]
    if selected == 0:
        led1.value(led_state[0])
    elif selected == 1:
        led2.value(led_state[1])
    elif selected == 2:
        led3.value(led_state[2])
    update_display()    

def button_handler(pin):
    global last_pressed
    current_time=time.ticks_ms()
    if time.ticks_diff(current_time, last_pressed) >50:
        last_pressed=current_time
        led_toggle()
button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

update_display()
while True:
    if rot.fifo.has_data():
        direction=rot.fifo.get()
        selected+=direction
        if selected <0:
            selected=0
        elif selected>=3:
            selected=2
        update_display()

    time.sleep(0.01) 