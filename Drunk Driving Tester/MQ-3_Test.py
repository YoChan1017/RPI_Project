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

print("Measuring baseline for 10 seconds...")

samples = []
start_time = time.time()
while time.time() - start_time < 10:
    value = read_channel(0)
    samples.append(value)
    voltage = (value / 4095.0) * 5.0
    print(f"[Baseline] Raw: {value} | Voltage: {voltage:.2f} V")
    time.sleep(1)
THRESHOLD = (sum(samples) // len(samples)) + 500

print(f"\n=== Baseline THRESHOLD set to: {THRESHOLD} ===\n")

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
