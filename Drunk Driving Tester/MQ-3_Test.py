import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def read_channel(channel):
    if not (0 <= channel <= 7):
        return -1

    start_bit = 0b00000110
    second_byte = (channel & 0b111) << 6
    response = spi.xfer2([start_bit, second_byte, 0x00])
    print(response)
    
    result = ((response[1] & 0x0F) << 8) | response[2]
    return result

THRESHOLD = 1500

try:
    while True:
        raw_value = read_channel(0)
        
        if raw_value > THRESHOLD:
            print(f"{raw_value} Drunk driver")
        else:
            print(f"{raw_value} PASS")
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
