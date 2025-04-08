from filefifo import Filefifo
from fifo import Fifo
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import micropython
micropython.alloc_emergency_exception_buf(200)

data = Filefifo(10, name='capture_250Hz_03.txt')
data_list=[]
for _ in range (1000):
    value = data.get()
    data_list.append(value)

min_value = min(data_list)
max_value= max(data_list)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)   

start_point = 0
oled_size = 128


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
    if rot.fifo.has_data():
        direction=rot.fifo.get()
        start_point +=direction*128
        if start_point<0:
            start_point=0
        if start_point>(1000-oled_size):
            start_point=(1000-oled_size)
           
    oled.fill(0)
    for i in range(oled_size):
        value=data_list[start_point+i]
        y=int((value-min_value)/(max_value-min_value)*64)
        y = max(0, min(63,y)) 
        oled.pixel(i,y,1)
    oled.show()
    time.sleep(0.05)
  
