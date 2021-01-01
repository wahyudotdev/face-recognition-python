from I2C_LCD_driver import I2C_LCD_driver
from mlx90614 import MLX90614
from smbus2 import SMBus

class Peripheral(object):
    def __init__(self):
        self.lcd = I2C_LCD_driver.lcd()
        self.bus = SMBus(1)
        self.mlx = MLX90614(self.bus, address=0x5A)
    def getTemp(self, name):
        temp = str(int(self.mlx.get_object_1()))
        if(name != None and name != '' and name != 'unknown'):
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string(f'Nama : {name}',1)
            self.lcd.lcd_display_string(f'Suhu : {temp}C',2)
        return temp
