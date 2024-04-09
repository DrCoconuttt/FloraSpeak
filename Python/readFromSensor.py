import serial #may need to install with pip3 install pyserial 
import time

# Configure the serial connection
ser = serial.Serial(
    port='COM3',  # have to change this depending on if windows/linux/macos, for me it's  '/dev/ttyUSB0'
    baudrate=9600,
    timeout=1   # wait 1 second between each read from serial port
)

time.sleep(2)

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()  # read a line from the serial port and decode it
            print(line)  
            
            # storing sensor data 
            # will be in format:
            #Temperature = <VALUE> C
            #Temp: <LOW/MEDIUM/HIGH>
            #<VALUE> lux
            #Light: <LOW/MEDIUM/HIGH>
            sensor_data = line
            
            # can do api calls or here
            
except KeyboardInterrupt:
    print("Program terminated by user")

finally:
    ser.close()  