"""
The main program that utilizes the "library" functions inside kipye-lcd.py
This is different from the demo examples as this is a general purpose program to draw to the screen
It is also a utility to set things like screen brightness
"""

import kipye_lcd
from PIL import Image
import sys
import os
import serial
import argparse

DEVICE_AUTODETECT_ID = 'VID:PID=454D:4E41'

def auto_detect_port(verbose_level=0):
    """
    Attempt auto detect
    Uses the code from pyserial tools (https://github.com/pyserial/pyserial/blob/master/serial/tools/list_ports.py)
    """
    if os.name == 'nt':  # sys.platform == 'win32':
        from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    else:
        return None

    iterator = sorted(comports())
    for n, (port, desc, hwid) in enumerate(iterator, 1):
        if DEVICE_AUTODETECT_ID in hwid:
            if verbose_level >= 1:
                print(f"INFO: Auto-Detect port: {port}")
            return str(port)
    
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description = """
                    Utility to write images to a "kipye" USB LCD
                    (the "aida64" LCDs sold on lazada or aliexpress that don\'t actually interface with aida64)""",
                    epilog = 'Input can be a file path or image piped from STDIN')
    parser.add_argument('--image', type=str, help='Path to image file to display.')
    parser.add_argument('--com-port', type=str, help='Set COM port. Omit for auto-detection. (Fallback: /dev/ttyACM0)')
    parser.add_argument('--stdin', action=argparse.BooleanOptionalAction, help='Read image to display from stdin (ex: pipe from curl)')
    parser.add_argument('--set-backlight', type=int, help=f"Set screen brightness. Minimum: {kipye_lcd.BRIGHTNESS_MIN} Max: {kipye_lcd.BRIGHTNESS_MAX} Default: {kipye_lcd.BRIGHTNESS_DEFAULT}")
    parser.add_argument('--verbose', '-v', action='count', default=0, help="set verbose: level1 - info (-v), level2-debug (-vv)")
    args = parser.parse_args()

    com_port = args.com_port
    if com_port is None:
        com_port = auto_detect_port(verbose_level=args.verbose)

    im = None
    if args.stdin:
        im = Image.open((sys.stdin.buffer))
    elif args.image:
        im = Image.open(args.image)

    lcd = kipye_lcd.kipye_lcd(verbose_level=args.verbose, com_port=com_port, backlight=args.set_backlight)

    if im is not None:    
        lcd.load_pil_image(im)
        lcd.display_image()
    else:
        if not args.set_backlight:
            #if this point was reached, most likely the script did nothing.
            parser.print_help()
