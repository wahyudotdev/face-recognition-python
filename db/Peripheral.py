import I2C_LCD_driver
from mlx90614 import MLX90614
from smbus2 import SMBus

class Peripheral(object):
    def __init__(self):
        self.lcd = I2C_LCD_driver.lcd()
        self.bus = SMBus(1)
        self.mlx = MLX90614(bus, address=0x5A)
    
    def getTemp(self, name):
        temp = str(int(self.mlx.get_object_1()))
        self.lcd.lcd_display_string(f'Nama : {name}',1)
        self.lcd.lcd_display_string(f'Suhu : {temp}C')
        return temp

p = Peripheral()
print(p.getTemp('tes'))