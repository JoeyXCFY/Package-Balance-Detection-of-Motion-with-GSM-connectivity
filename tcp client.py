import socket   
import sys
import smbus
import math
import time
    

SERVER_IP = "140.122.79.84"

SERVER_PORT = 1234

logic= 0
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
diff_x=-1
diff_y=-1
x1=0
y1=0
x0=0
y0=0

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)
 

print("Starting socket: TCP...")

server_addr = (SERVER_IP, SERVER_PORT)

socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#gyroscope
accel_xout = read_word_2c(0x3b)
accel_yout = read_word_2c(0x3d)
accel_zout = read_word_2c(0x3f)

accel_xout_scaled = accel_xout / 16384.0
accel_yout_scaled = accel_yout / 16384.0
accel_zout_scaled = accel_zout / 16384.0

#get diff
x1= get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
y1= get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

if diff_x< 0:
    diff_x= 0
    diff_y= 0
else:
    diff_x=int(abs(x1-x0))
    diff_y=int(abs(y1-y0))

x0= x1
y0= y1    
    

while True:  

    try:

        print("Connecting to server @ %s:%d..." %(SERVER_IP, SERVER_PORT))

        socket_tcp.connect(server_addr)  

        break  

    except Exception:

        print("Can't connect to server, try it later!")

        time.sleep(1)

        continue  

 

print("Receiving package...")  

while True:
    
    #send diff
    diff_x_bytes= diff_x.to_bytes(2, 'big')
    diff_y_bytes= diff_y.to_bytes(2, 'big') 

    data = socket_tcp.recv(512)
    
    if len(data)>0:
        
        if logic== 0:
            
            #gyroscope
            ccel_xout = read_word_2c(0x3b)
            accel_yout = read_word_2c(0x3d)
            accel_zout = read_word_2c(0x3f)

            accel_xout_scaled = accel_xout / 16384.0
            accel_yout_scaled = accel_yout / 16384.0
            accel_zout_scaled = accel_zout / 16384.0

            #get diff
            x1= get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
            y1= get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

            if diff_x< 0:
                diff_x= 0
                diff_y= 0
            else:
                diff_x=int(abs(x1-x0))
                diff_y=int(abs(y1-y0))

            x0= x1
            y0= y1  
            
            print("Received: %s" %data)

            socket_tcp.send(diff_x_bytes)
            
            logic= 1
            
            continue
            
        if logic== 1:
            
            print("Received: %s" %data)

            socket_tcp.send(diff_y_bytes)
            
            logic= 0          
        
            continue

