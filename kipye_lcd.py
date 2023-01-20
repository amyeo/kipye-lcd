import serial

COM_PORT_DEFAULT = '/dev/ttyACM0'
LCD_HEIGHT = 480
LCD_WIDTH = 320
BAUD_RATE = 119200 #based on manufacturer code. some devices may not support (other baud rate will work)
OUT_OF_BOUNDS_DEFAULT = [0,0,0] #RGB pixel to put if image is less than LCD dimensions
BRIGHTNESS_MIN = 0
BRIGHTNESS_MAX = 1000
BRIGHTNESS_DEFAULT = 500

def get_color16(rgb_arr):
    """
    conversion code lifted from the manufacturer
    alpha is discarded if present
    """
    R = rgb_arr[0]
    G = rgb_arr[1]
    B = rgb_arr[2]
    num = 0
    num2 = 0

    num = (num | (R >> 3))
    num2 = (num2 | (num << 11))

    num = 0
    num = (num | (G >> 2))
    num2 = (num2 | (num << 5))

    num = 0
    num = (num | (B >> 3))
    num2 = (num2 | num)

    return num2

class kipye_lcd:
    serial_object = None
    image_buffer = None #2d array when initialized
    verbose_level = 0
    com_port = None

    def __init__(self, verbose_level=0, com_port=COM_PORT_DEFAULT, backlight=BRIGHTNESS_DEFAULT):
        """
        Initialize device
        """
        if verbose_level is not None:
            self.verbose_level = verbose_level
        else:
            self.verbose_level = 0
        
        if com_port is not None:
            self.com_port = com_port
        else:
            self.com_port = COM_PORT_DEFAULT

        if self.verbose_level >= 1:
            print(f"INFO: Serial port {self.com_port} with baud rate: {BAUD_RATE}")

        self.serial_object = serial.Serial(self.com_port, BAUD_RATE, timeout=10, rtscts=True, dsrdtr=True)
        self.flush_input_buffer()

        if backlight is not None:
            if backlight >= BRIGHTNESS_MIN and backlight <= BRIGHTNESS_MAX:
                self.set_brightness(backlight)
            else:
                print("Error: Brightness value out of range. See help (-h) for details. (using default)")
                self.set_brightness(BRIGHTNESS_DEFAULT)
        else:
            self.set_brightness(BRIGHTNESS_DEFAULT)
        self.flush_input_buffer()
        

    def set_brightness(self, bval):
        assert self.serial_object.is_open
        self.write_data([67, 67, ((bval >> 8) & 0xFF), (bval & 0xFF)]) #split into 2 bytes

    def flush_input_buffer(self):
        """
        The device expects the input buffer cleared
        This is done periodically (esp. when writing images)
        Failure to do so will cause a crash
        """
        assert self.serial_object.is_open
        while self.serial_object.in_waiting > 0:
            read_byte = self.serial_object.read(1)
            if self.verbose_level >= 2:
                print("Debug: Serial received data: ", read_byte)
        self.serial_object.flush()
    
    def write_data(self, input_array):
        assert self.serial_object.is_open
        self.flush_input_buffer()
        self.serial_object.write(bytearray(input_array))
        self.flush_input_buffer()
    
    def load_pil_image(self, pil_im_object):
        """
        Take a PIL image and load to image_buffer
        Pixel values in the format specific to the device are pre-computed here
        """
        self.image_buffer = []
        for i in range(0,LCD_HEIGHT):
            row_data = []
            for j in range(0,LCD_WIDTH):
                pixel_rbg = OUT_OF_BOUNDS_DEFAULT
                if i < pil_im_object.size[1] and j < pil_im_object.size[0]:
                    pixel_rbg = pil_im_object.getpixel((j, i))
                row_data.append(get_color16(pixel_rbg))
            self.image_buffer.append(row_data)
    
    def display_image(self):
        """
        Take the pre-computed image from the image_buffer variable and draw to screen
        """
        if self.image_buffer is None:
            print("ERROR: You need to load an image first")
            return
        assert len(self.image_buffer) == LCD_HEIGHT
        self.write_data([67, 65 , 0, 0, 1, 63, 0, 0, 1, 223])
        self.write_data([68,0,0,0])
        picarr = [80]
        for i in range(0,LCD_HEIGHT):
            for j in range(0,LCD_WIDTH):
                pixel = self.image_buffer[i][j]
                for byte in [(int((pixel & 0xFF00)) >> 8), (int(pixel & 0xFF))]: #split 16 into two 8s
                    picarr.append(byte)
                    assert not len(picarr) > 64
                    if len(picarr) == 64:
                        self.write_data(picarr)
                        picarr = [80]
        
        if len(picarr) > 0:
            self.write_data(picarr)

    def __del__(self):
        """
        destructor
        """
        if self.verbose_level >= 2:
            print("LCD object destructor called.")
        self.serial_object.close()