import os
import time
from multiprocessing import Process, Queue
from display_objects import DisplayObject
from PIL import Image

# Handle multiple versions of Adafruit library
device = 'unknown'
try:
    from Adafruit_LED_Backpack.Matrix8x8 import Matrix8x8
    device='pi-old'
except ImportError:
    import board
    import busio
    from adafruit_ht16k33 import matrix
    device='pi'

class Display():
    """Displays queue of DisplayObject's on Adafruit LED backpack"""

    def __init__(self, brightness=5, delay=0.01, **kwargs):
        if device=='pi-old':
            self.display = Matrix8x8()
            self.display.begin()

        if device=='pi':
            i2c = busio.I2C(board.SCL, board.SDA)

            self.display = matrix.Matrix8x8(i2c)
            self.display.auto_write = False
            self.display.brightness = brightness
            self.display.blink_rate = 0

        self.delay = delay
        self.frames = Queue()

    def __enter__(self):
        self.p = Process(target=self.__update__)
        self.p.start()
        return self

    def __process_frame__(self, image, start_time, delay = None):
        if delay is None: delay = self.delay
        if image.size[0] != 8 or image.size[1] != 8:
            print('Image must be an 8x8 pixels in size.')
            return

        if device is 'pi-old':
            self.display.set_image(image)
            if time.time()-start_time < delay: time.sleep(delay - (time.time()-start_time))
            self.display.write_display()

        if device is 'pi':
            pix = image.convert('1').load()

            for x in [0, 1, 2, 3, 4, 5, 6, 7]:
                for y in [0, 1, 2, 3, 4, 5, 6, 7]:
                    color = pix[(x, y)]
                    if color == 0:
                        self.display.pixel(x, y, 0)
                    else:
                        self.display.pixel(x, y, 1)
            if time.time()-start_time < delay: time.sleep(delay - (time.time()-start_time))
            self.display.show()

    def __update__(self):
        while True:
            start_time = time.time()

            if self.frames.empty():
                self.frames.put(Image.new('1', (8,8),0))

            frame  = self.frames.get()

            if frame is None: break
            elif isinstance(frame, DisplayObject):
                frame.display(self)

    def __exit__(self, exc_type, exc_value, traceback):
        self.frames.put(Image.new('1', (8,8),0))
        self.frames.put(None)
        self.p.join()

    def restart(self):
        self.p.terminate()
        while not self.frames.empty():
            self.frames.get()
        self.frames.put(Image.new('1', (8,8),0))
        self.p.join()
        self.__enter__()
        return self
