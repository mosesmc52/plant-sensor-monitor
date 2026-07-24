# *****************************************************************************
# * | File        :\t  epd7in5.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version: V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
from . import epdconfig

EPD_WIDTH = 800
EPD_HEIGHT = 480
GRAY1 = 0xff
GRAY2 = 0xC0
GRAY3 = 0x80
GRAY4 = 0x00
logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.GRAY1 = GRAY1
        self.GRAY2 = GRAY2
        self.GRAY3 = GRAY3
        self.GRAY4 = GRAY4

    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.SPI.writebytes2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = epdconfig.digital_read(self.busy_pin)
        while busy == 0:
            self.send_command(0x71)
            busy = epdconfig.digital_read(self.busy_pin)
        epdconfig.delay_ms(20)
        logger.debug("e-Paper busy release")

    def init(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.send_command(0x06)
        for data in (0x17, 0x17, 0x28, 0x17):
            self.send_data(data)
        self.send_command(0x01)
        for data in (0x07, 0x07, 0x28, 0x17):
            self.send_data(data)
        self.send_command(0x04)
        epdconfig.delay_ms(100)
        self.ReadBusy()
        self.send_command(0x00)
        self.send_data(0x1F)
        self.send_command(0x61)
        for data in (0x03, 0x20, 0x01, 0xE0):
            self.send_data(data)
        self.send_command(0x15)
        self.send_data(0x00)
        self.send_command(0x50)
        self.send_data(0x10)
        self.send_data(0x07)
        self.send_command(0x60)
        self.send_data(0x22)
        return 0

    def init_fast(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.send_command(0x00)
        self.send_data(0x1F)
        self.send_command(0x50)
        self.send_data(0x10)
        self.send_data(0x07)
        self.send_command(0x04)
        epdconfig.delay_ms(100)
        self.ReadBusy()
        self.send_command(0x06)
        for data in (0x27, 0x27, 0x18, 0x17):
            self.send_data(data)
        self.send_command(0xE0)
        self.send_data(0x02)
        self.send_command(0xE5)
        self.send_data(0x5A)
        return 0

    def init_part(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.send_command(0x00)
        self.send_data(0x1F)
        self.send_command(0x04)
        epdconfig.delay_ms(100)
        self.ReadBusy()
        self.send_command(0xE0)
        self.send_data(0x02)
        self.send_command(0xE5)
        self.send_data(0x6E)
        return 0

    def init_4Gray(self):
        return self.init_part()

    def getbuffer(self, image):
        if image.size == (self.width, self.height):
            image = image.convert("1")
        elif image.size == (self.height, self.width):
            image = image.rotate(90, expand=True).convert("1")
        else:
            logger.warning("Wrong image dimensions: must be %sx%s", self.width, self.height)
            return [0x00] * (self.width // 8 * self.height)
        buffer = bytearray(image.tobytes("raw"))
        for index in range(len(buffer)):
            buffer[index] ^= 0xFF
        return buffer

    def getbuffer_4Gray(self, image):
        return self.getbuffer(image)

    def display(self, image):
        width = (self.width + 7) // 8
        image1 = [0xFF] * (width * self.height)
        for row in range(self.height):
            for column in range(width):
                image1[column + row * width] = ~image[column + row * width]
        self.send_command(0x10)
        self.send_data2(image1)
        self.send_command(0x13)
        self.send_data2(image)
        self.send_command(0x12)
        epdconfig.delay_ms(100)
        self.ReadBusy()

    def Clear(self):
        size = self.width * self.height // 8
        self.send_command(0x10)
        self.send_data2([0xFF] * size)
        self.send_command(0x13)
        self.send_data2([0x00] * size)
        self.send_command(0x12)
        epdconfig.delay_ms(100)
        self.ReadBusy()

    def display_Partial(self, image, x_start, y_start, x_end, y_end):
        self.display(self.getbuffer(image))

    def display_4Gray(self, image):
        self.display(image)

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.ReadBusy()
        self.send_command(0x07)
        self.send_data(0xA5)
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
