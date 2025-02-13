# The MIT License (MIT)
#
# Copyright (c) 2018 Mark Winney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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
"""
`sh1106`
====================================================

MicroPython SH1106 OLED driver, I2C and SPI interfaces

* Author(s): Mark Winney and heavily based on work by Tony DiCola, Michael McWethy

Based on adafruit's Framebuffer library:
2018 Kattni Rembor, Melissa LeBlanc-Williams
 and Tony DiCola, for Adafruit Industries.
 Original file created by Damien P. George

 """

import time
import os
import struct

from micropython import const


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/winneymj/Adafruit_CircuitPython_SH1106.git"

# pylint: disable-msg=bad-whitespace
# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_DISP_ALLON = const(0xA5)
SET_NORM = const(0xA6)
SET_NORM_INV = const(0xA7)
SET_DISP_OFF = const(0xAE)
SET_DISP_ON = const(0xAF)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_PAGE_ADDRESS = const(0xB0)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA1)
SET_MUX_RATIO = const(0xA8)
SET_COMSCANDEC = const(0xC8)
SET_COMSCANINC = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)
SET_LOW_COLUMN = const(0x00)
SET_HIGH_COLUMN = const(0x10)
# pylint: enable-msg=bad-whitespace


class MVLSBFormat:
    """MVLSBFormat"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y >> 3) * framebuf.stride + x
        offset = y & 0x07
        framebuf.buf[index] = (framebuf.buf[index] & ~(0x01 << offset)) | (
            (color != 0) << offset
        )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y >> 3) * framebuf.stride + x
        offset = y & 0x07
        return (framebuf.buf[index] >> offset) & 0x01

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf.buf)):  # pylint: disable=consider-using-enumerate
            framebuf.buf[i] = fill

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        while height > 0:
            index = (y >> 3) * framebuf.stride + x
            offset = y & 0x07
            for w_w in range(width):
                framebuf.buf[index + w_w] = (
                    framebuf.buf[index + w_w] & ~(0x01 << offset)
                ) | ((color != 0) << offset)
            y += 1
            height -= 1


class FrameBuffer:
    """FrameBuffer object.

    :param buf: An object with a buffer protocol which must be large enough to contain every
                pixel defined by the width, height and format of the FrameBuffer.
    :param width: The width of the FrameBuffer in pixel
    :param height: The height of the FrameBuffer in pixel
    :param buf_format: Specifies the type of pixel used in the FrameBuffer; permissible values
                        are listed under Constants below. These set the number of bits used to
                        encode a color value and the layout of these bits in ``buf``. Where a
                        color value c is passed to a method, c is  a small integer with an encoding
                        that is dependent on the format of the FrameBuffer.
    :param stride: The number of pixels between each horizontal line of pixels in the
                   FrameBuffer. This defaults to ``width`` but may need adjustments when
                   implementing a FrameBuffer within another larger FrameBuffer or screen. The
                   ``buf`` size must accommodate an increased step size.

    """

    def __init__(self, buf, width, height, stride=None):
        # pylint: disable=too-many-arguments
        self.buf = buf
        self.width = width
        self.height = height
        self.stride = stride
        self._font = None
        if self.stride is None:
            self.stride = width
        self.format = MVLSBFormat()
        self._rotation = 0

    @property
    def rotation(self):
        """The rotation setting of the display, can be one of (0, 1, 2, 3)"""
        return self._rotation

    @rotation.setter
    def rotation(self, val):
        if not val in (0, 1, 2, 3):
            raise RuntimeError("Bad rotation setting")
        self._rotation = val

    def fill(self, color):
        """Fill the entire FrameBuffer with the specified color."""
        self.format.fill(self, color)

    def fill_rect(self, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments, too-many-boolean-expressions
        self.rect(x, y, width, height, color, fill=True)

    def pixel(self, x, y, color=None):
        """If ``color`` is not given, get the color value of the specified pixel. If ``color`` is
        given, set the specified pixel to the given color."""
        if self.rotation == 1:
            x, y = y, x
            x = self.width - x - 1
        if self.rotation == 2:
            x = self.width - x - 1
            y = self.height - y - 1
        if self.rotation == 3:
            x, y = y, x
            y = self.height - y - 1

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        if color is None:
            return self.format.get_pixel(self, x, y)
        self.format.set_pixel(self, x, y, color)
        return None

    def hline(self, x, y, width, color):
        """Draw a horizontal line up to a given length."""
        self.rect(x, y, width, 1, color, fill=True)

    def vline(self, x, y, height, color):
        """Draw a vertical line up to a given length."""
        self.rect(x, y, 1, height, color, fill=True)

    def circle(self, center_x, center_y, radius, color):
        """Draw a circle at the given midpoint location, radius and color.
        The ```circle``` method draws only a 1 pixel outline."""
        x = radius - 1
        y = 0
        d_x = 1
        d_y = 1
        err = d_x - (radius << 1)
        while x >= y:
            self.pixel(center_x + x, center_y + y, color)
            self.pixel(center_x + y, center_y + x, color)
            self.pixel(center_x - y, center_y + x, color)
            self.pixel(center_x - x, center_y + y, color)
            self.pixel(center_x - x, center_y - y, color)
            self.pixel(center_x - y, center_y - x, color)
            self.pixel(center_x + y, center_y - x, color)
            self.pixel(center_x + x, center_y - y, color)
            if err <= 0:
                y += 1
                err += d_y
                d_y += 2
            if err > 0:
                x -= 1
                d_x += 2
                err += d_x - (radius << 1)

    def rect(self, x, y, width, height, color, *, fill=False):
        """Draw a rectangle at the given location, size and color. The ```rect``` method draws only
        a 1 pixel outline."""
        # pylint: disable=too-many-arguments
        if self.rotation == 1:
            x, y = y, x
            width, height = height, width
            x = self.width - x - width
        if self.rotation == 2:
            x = self.width - x - width
            y = self.height - y - height
        if self.rotation == 3:
            x, y = y, x
            width, height = height, width
            y = self.height - y - height

        # pylint: disable=too-many-boolean-expressions
        if (
            width < 1
            or height < 1
            or (x + width) <= 0
            or (y + height) <= 0
            or y >= self.height
            or x >= self.width
        ):
            return
        x_end = min(self.width - 1, x + width - 1)
        y_end = min(self.height - 1, y + height - 1)
        x = max(x, 0)
        y = max(y, 0)
        if fill:
            self.format.fill_rect(self, x, y, x_end - x + 1, y_end - y + 1, color)
        else:
            self.format.fill_rect(self, x, y, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x, y, 1, y_end - y + 1, color)
            self.format.fill_rect(self, x, y_end, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x_end, y, 1, y_end - y + 1, color)

    def line(self, x_0, y_0, x_1, y_1, color):
        # pylint: disable=too-many-arguments
        """Bresenham's line algorithm"""
        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)
        x, y = x_0, y_0
        s_x = -1 if x_0 > x_1 else 1
        s_y = -1 if y_0 > y_1 else 1
        if d_x > d_y:
            err = d_x / 2.0
            while x != x_1:
                self.pixel(x, y, color)
                err -= d_y
                if err < 0:
                    y += s_y
                    err += d_x
                x += s_x
        else:
            err = d_y / 2.0
            while y != y_1:
                self.pixel(x, y, color)
                err -= d_x
                if err < 0:
                    x += s_x
                    err += d_y
                y += s_y
        self.pixel(x, y, color)

    def blit(self):
        """blit is not yet implemented"""
        raise NotImplementedError()

    def scroll(self, delta_x, delta_y):
        """shifts framebuf in x and y direction"""
        if delta_x < 0:
            shift_x = 0
            xend = self.width + delta_x
            dt_x = 1
        else:
            shift_x = self.width - 1
            xend = delta_x - 1
            dt_x = -1
        if delta_y < 0:
            y = 0
            yend = self.height + delta_y
            dt_y = 1
        else:
            y = self.height - 1
            yend = delta_y - 1
            dt_y = -1
        while y != yend:
            x = shift_x
            while x != xend:
                self.format.set_pixel(
                    self, x, y, self.format.get_pixel(self, x - delta_x, y - delta_y)
                )
                x += dt_x
            y += dt_y

    # pylint: disable=too-many-arguments
    def text(self, string, x, y, color, *, font_name="font5x8.bin", size=1):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        # determine our effective width/height, taking rotation into account
        frame_width = self.width
        frame_height = self.height
        if self.rotation in (1, 3):
            frame_width, frame_height = frame_height, frame_width

        for chunk in string.split("\n"):
            if not self._font or self._font.font_name != font_name:
                # load the font!
                self._font = BitmapFont(font_name)
            width = self._font.font_width
            height = self._font.font_height
            for i, char in enumerate(chunk):
                char_x = x + (i * (width + 1)) * size
                if (
                    char_x + (width * size) > 0
                    and char_x < frame_width
                    and y + (height * size) > 0
                    and y < frame_height
                ):
                    self._font.draw_char(char, char_x, y, self, color, size=size)
            y += height * size

    # pylint: enable=too-many-arguments

    def image(self, img):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size."""
        # determine our effective width/height, taking rotation into account
        width = self.width
        height = self.height
        if self.rotation in (1, 3):
            width, height = height, width

        if img.mode != "1":
            raise ValueError("Image must be in mode 1.")

        imwidth, imheight = img.size
        if imwidth != width or imheight != height:
            raise ValueError(
                f"Image must be same dimensions as display ({width}x{height})."
            )
        # Grab all the pixels from the image, faster than getpixel.
        pixels = img.load()
        # Clear buffer
        for i in range(len(self.buf)):  # pylint: disable=consider-using-enumerate
            self.buf[i] = 0
        # Iterate through the pixels
        for x in range(width):  # yes this double loop is slow,
            for y in range(height):  #  but these displays are small!
                if img.mode == "RGB":
                    self.pixel(x, y, pixels[(x, y)])
                elif pixels[(x, y)]:
                    self.pixel(x, y, 1)  # only write if pixel is true


# MicroPython basic bitmap font renderer.
# Author: Tony DiCola
# License: MIT License (https://opensource.org/licenses/MIT)
class BitmapFont:
    """A helper class to read binary font tiles and 'seek' through them as a
    file to display in a framebuffer. We use file access so we dont waste 1KB
    of RAM on a font!"""

    def __init__(self, font_name="font5x8.bin"):
        # Specify the drawing area width and height, and the pixel function to
        # call when drawing pixels (should take an x and y param at least).
        # Optionally specify font_name to override the font file to use (default
        # is font5x8.bin).  The font format is a binary file with the following
        # format:
        # - 1 unsigned byte: font character width in pixels
        # - 1 unsigned byte: font character height in pixels
        # - x bytes: font data, in ASCII order covering all 255 characters.
        #            Each character should have a byte for each pixel column of
        #            data (i.e. a 5x8 font has 5 bytes per character).
        self.font_name = font_name

        # Open the font file and grab the character width and height values.
        # Note that only fonts up to 8 pixels tall are currently supported.
        try:
            self._font = open(  # pylint: disable=consider-using-with
                self.font_name, "rb"
            )
            self.font_width, self.font_height = struct.unpack("BB", self._font.read(2))
            # simple font file validation check based on expected file size
            if 2 + 256 * self.font_width != os.stat(font_name)[6]:
                raise RuntimeError("Invalid font file: " + font_name)
        except OSError:
            print("Could not find font file", font_name)
            raise
        except OverflowError:
            # os.stat can throw this on boards without long int support
            # just hope the font file is valid and press on
            pass

    def deinit(self):
        """Close the font file as cleanup."""
        self._font.close()

    def __enter__(self):
        """Initialize/open the font file"""
        self.__init__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """cleanup on exit"""
        self.deinit()

    def draw_char(
        self, char, x, y, framebuffer, color, size=1
    ):  # pylint: disable=too-many-arguments
        """Draw one character at position (x,y) to a framebuffer in a given color"""
        size = max(size, 1)
        # Don't draw the character if it will be clipped off the visible area.
        # if x < -self.font_width or x >= framebuffer.width or \
        #   y < -self.font_height or y >= framebuffer.height:
        #    return
        # Go through each column of the character.
        for char_x in range(self.font_width):
            # Grab the byte for the current column of font data.
            self._font.seek(2 + (ord(char) * self.font_width) + char_x)
            try:
                line = struct.unpack("B", self._font.read(1))[0]
            except RuntimeError:
                continue  # maybe character isnt there? go to next
            # Go through each row in the column byte.
            for char_y in range(self.font_height):
                # Draw a pixel for each bit that's flipped on.
                if (line >> char_y) & 0x1:
                    framebuffer.fill_rect(
                        x + char_x * size, y + char_y * size, size, size, color
                    )

    def width(self, text):
        """Return the pixel width of the specified text message."""
        return len(text) * (self.font_width + 1)


class FrameBuffer1(FrameBuffer):  # pylint: disable=abstract-method
    """FrameBuffer1 object. Inherits from FrameBuffer."""


class _SH1106:
    """Base class for SH1106 display driver"""

    # pylint: disable-msg=too-many-arguments
    # pylint: disable-msg=too-many-instance-attributes
    def __init__(self, framebuffer, width, height, external_vcc, reset):
        self.framebuf = framebuffer
        self.fill = self.framebuf.fill
        self.pixel = self.framebuf.pixel
        self.line = self.framebuf.line
        self.text = self.framebuf.text
        self.scroll = self.framebuf.scroll
        self.blit = self.framebuf.blit
        self.vline = self.framebuf.vline
        self.hline = self.framebuf.hline
        self.fill_rect = self.framebuf.fill_rect
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        # reset may be None if not needed
        self.reset_pin = reset
        if self.reset_pin:
            self.reset_pin.switch_to_output(value=0)
        # Note the subclass must initialize self.framebuf to a framebuffer.
        # This is necessary because the underlying data buffer is different
        # between I2C and SPI implementations (I2C needs an extra byte).
        self.poweron()
        self.init_display()

    def init_display(self):
        """Base class to initialize display"""
        for cmd in (
            SET_DISP_OFF,  # Display Off
            SET_DISP_CLK_DIV,
            0xF0,  # Ratio
            SET_MUX_RATIO,
            0x3F,  # Multiplex
            SET_DISP_OFFSET,
            0x00,  # No offset
            SET_DISP_START_LINE | 0x00,  # Start line
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,  # Charge pump
            SET_MEM_ADDR,
            0x00,  # Memory mode, Horizontal
            SET_PAGE_ADDRESS,  # Page address 0
            SET_COMSCANDEC,  # COMSCANDEC
            SET_LOW_COLUMN,  # SETLOWCOLUMN
            SET_HIGH_COLUMN,  # SETHIGHCOLUMN
            SET_COM_PIN_CFG,
            0x02 if self.height == 32 else 0x12,  # SETCOMPINS
            SET_CONTRAST,
            0x9F if self.external_vcc else 0xCF,  # Contrast maximum
            SET_SEG_REMAP,  # SET_SEGMENT_REMAP
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,  # Pre Charge
            SET_VCOM_DESEL,
            0x20,  # VCOM Detect 0.77*Vcc
            SET_ENTIRE_ON,  # DISPLAYALLON_RESUME
            SET_NORM,  # NORMALDISPLAY
            SET_DISP_ON,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        """Turn off the display (nothing visible)"""
        self.write_cmd(SET_DISP_OFF)

    def contrast(self, contrast):
        """Adjust the contrast"""
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        """Invert all pixels on the display"""
        if invert:
            self.write_cmd(SET_NORM_INV)
        else:
            self.write_cmd(SET_NORM)

    def write_framebuf(self):
        """Derived class must implement this"""
        raise NotImplementedError

    def write_cmd(self, cmd):
        """Derived class must implement this"""
        raise NotImplementedError

    def poweron(self):
        "Reset device and turn on the display."
        if self.reset_pin:
            self.reset_pin.value = 1
            time.sleep(0.001)
            self.reset_pin.value = 0
            time.sleep(0.010)
            self.reset_pin.value = 1
            time.sleep(0.010)
        self.write_cmd(SET_DISP_ON)

    def show(self):
        """Update the display"""
        self.write_framebuf()


class SH1106_I2C(_SH1106):
    """
    I2C class for SH1106

    :param width: the width of the physical screen in pixels,
    :param height: the height of the physical screen in pixels,
    :param i2c: the I2C peripheral to use,
    :param addr: the 8-bit bus address of the device,
    :param external_vcc: whether external high-voltage source is connected.
    :param reset: if needed, DigitalInOut designating reset pin
    """

    def __init__(
        self, width, height, i2c, *, addr=0x3C, external_vcc=False, reset=None
    ):
        self.i2c_bus = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        framebuffer = FrameBuffer1(memoryview(self.buffer)[1:], width, height)
        super().__init__(framebuffer, width, height, external_vcc, reset)

    def write_cmd(self, cmd):
        """Send a command to the I2C device"""
        self.temp[0] = 0x00  # Co = 0, D/C = 0
        self.temp[1] = cmd
        self.i2c_bus.try_lock()
        self.i2c_bus.writeto(self.addr, self.temp)

    def write_framebuf(self):
        """write to the frame buffer via I2C"""

        self.i2c_bus.try_lock()
        write = self.i2c_bus.writeto
        write_cmd = self.write_cmd
        tmp_buf = bytearray(1)
        tmp_buf[0] = 0x40  # Co = 0, D/C = 1

        local_buffer = bytearray(self.width + 1)

        for page in range(0, 8):  # Pages
            page_mult = page << 7
            write_cmd(0xB0 + page)  # set page address
            write_cmd(0x00)  # set lower column address
            write_cmd(0x10)  # set higher column address

            # Not sure if there is a way to do this without a local buffer
            # as we need to peprend a databyte onto the framebuffer data being sent.
            local_buffer = self.buffer[page_mult : page_mult + self.width + 1]
            local_buffer[:0] = tmp_buf  # prepend Co = 0, D/C = 1

            write(self.addr, local_buffer)

        self.i2c_bus.unlock()


# pylint: disable-msg=too-many-arguments
class SH1106_SPI(_SH1106):
    """
    SPI class for SH1106

    :param width: the width of the physical screen in pixels,
    :param height: the height of the physical screen in pixels,
    :param spi: the SPI peripheral to use,
    :param dc: the data/command pin to use (often labeled "D/C"),
    :param reset: the reset pin to use,
    :param cs: the chip-select pin to use (sometimes labeled "SS").
    """

    # pylint: disable=no-member
    # Disable should be reconsidered when refactor can be tested.
    def __init__(
        self,
        width,
        height,
        spi,
        dc,
        reset,
        cs,
        *,
        external_vcc=False,
        baudrate=8000000,
        polarity=0,
        phase=0,
    ):
        self.rate = 10 * 1024 * 1024
        dc.switch_to_output(value=0)
        cs.switch_to_output(value=1)
        self.spi_bus = spi
        self.spi_bus.try_lock()
        self.spi_bus.configure(baudrate=baudrate, polarity=polarity, phase=phase)
        self.spi_bus.unlock()
        self.dc_pin = dc
        self.buffer = bytearray((height // 8) * width)
        framebuffer = FrameBuffer1(self.buffer, width, height)
        super().__init__(framebuffer, width, height, external_vcc, reset)

    def write_cmd(self, cmd):
        """Send a command to the SPI device"""
        self.dc_pin.value = 0
        self.spi_bus.try_lock()
        self.spi_bus.write(bytearray([cmd]))

    def write_framebuf(self):
        """write to the frame buffer via SPI"""

        self.spi_bus.try_lock()
        spi_write = self.spi_bus.write
        write = self.write_cmd

        for page in range(0, 8):  # Pages
            page_mult = page << 7
            write(0xB0 + page)  # set page address
            write(0x02)  # set lower column address
            write(0x10)  # set higher column address

            self.dc_pin.value = 1
            spi_write(self.buffer, start=page_mult, end=page_mult + self.width)

        self.spi_bus.unlock()
