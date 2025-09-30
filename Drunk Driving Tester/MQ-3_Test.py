import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 1000000

def read_channel(channel):
    if not (0 <= channel <= 7):
        return -1
    command = 0b11000000 | (channel << 3)
    response = spi.xfer2([1, command, 0])
    value = ((response[1] & 0x0F) << 8) | response[2]
    return value

THRESHOLD = 2650

try:
    while True:
        raw_value = read_channel(0)
        
        if raw_value > THRESHOLD:
            print(f"{raw_value} Drunk dirver")
        else:
            print(f"{raw_value} PASS")
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()

