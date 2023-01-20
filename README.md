# kipye-lcd (AKA the "AIDA64" LCDs sold on lazada or aliexpress that don't actually interface with AIDA64)

## Quick start
### Dependencies
The python code requires the following:
 - pyserial
 - pillow

### Display test image
You can use the test image that came with the repo:
```
$ python main.py --image=nijika.png -vv
```

### COM Port
The COM port is auto-detected, but that may not work all the time. To specify a COM port:
```
$ python main.py --image=nijika.png -vv --com-port=/dev/ttyACM0
```

### Set Backlight/Brightness
You can set the brightness when displaying a picture. You can also set it without changing the picture.
Mine came with values from ~1-1000
```
$ python main.py --image=nijika.png -vv --com-port=/dev/ttyACM0 --set-backlight=20
OR
$ python main.py -vv --set-backlight=20
```

### STDIN display (pass image from curl)
You can display an image directly from a curl command with the --stdin option
```
$ curl -k -l -s "https://www/link-to-image" | python main.py --stdin
```
 

## Compatibility
Shold work with the following screens: (ad description)
```
3.5 Inch IPS Type-C Secondary Screen Computer CPU GPU RAM HDD MonitorUSB Display For Freely AIDA64 mini monitor
or
Mini ITX Case Moniror 3.5 Inch IPS TYPE-C Secondary Ccreen Computer CPU GPU RAM HDD Monitoring USB Display Free Drive AIDA64
```

The specific one this code was tested with: https://www.lazada.com.ph/products/mini-itx-case-moniror-35-inch-ips-type-c-secondary-ccreen-computer-cpu-gpu-ram-hdd-monitoring-usb-display-free-drive-aida64-i3124326242.html


## Demo Images
Running the first command:
![alt text](https://github.com/amyeo/kipye-lcd/blob/master/sample.jpg?raw=true)

Using curl and --stdin to display a rendered image from Grafana:
![alt text](https://github.com/amyeo/kipye-lcd/blob/master/sample_grafana.jpg?raw=true)

## Troubleshooting
### Serial port error despite correct COM port
Check first that the cdc_acm driver is used (if on Linux)
```
cdc_acm 1-2:1.0: ttyACM0: USB ACM device
```

If it is, the default baud rate may not be supported.

Edit the following line in the kipye_lcd.py file to change the baud rate:
```
BAUD_RATE = 119200 #based on manufacturer code. some devices may not support (other baud rate will work)
```