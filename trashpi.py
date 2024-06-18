import I2C_LCD_driver
import RPi.GPIO as GPIO
import time
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trashpi-db-default-rtdb.firebaseio.com/'
})

TRIG_PIN_1 = 23
ECHO_PIN_1 = 24
LED_PIN_1 = 18
TRIG_PIN_2 = 25
ECHO_PIN_2 = 8
LED_PIN_2 = 12

MAX_DISTANCE = 100.0

lcd = I2C_LCD_driver.lcd()

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN_1, GPIO.OUT)
    GPIO.setup(ECHO_PIN_1, GPIO.IN)
    GPIO.setup(LED_PIN_1, GPIO.OUT)
    GPIO.setup(TRIG_PIN_2, GPIO.OUT)
    GPIO.setup(ECHO_PIN_2, GPIO.IN)
    GPIO.setup(LED_PIN_2, GPIO.OUT)
    GPIO.output(TRIG_PIN_1, GPIO.LOW)
    GPIO.output(TRIG_PIN_2, GPIO.LOW)
    print("Mohon tunggu...")
    time.sleep(2)

def get_distance(TRIG_PIN, ECHO_PIN):
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return distance

def send_to_firebase(trash_can_1_percentage, trash_can_2_percentage):
    ref = db.reference('measurements')
    new_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "trash_can_1": trash_can_1_percentage,
        "trash_can_2": trash_can_2_percentage
    }
    ref.push(new_data)

def main():
    setup()
    try:
        while True:
            distance_1 = get_distance(TRIG_PIN_1, ECHO_PIN_1)
            distance_2 = get_distance(TRIG_PIN_2, ECHO_PIN_2)
            print(f"Kapasitas Tersisa 1: {distance_1:.2f} cm, Kapasitas Tersisa 2: {distance_2:.2f} cm")
            
            fill_percentage_1 = ((MAX_DISTANCE - distance_1) / MAX_DISTANCE) * 100
            fill_percentage_2 = ((MAX_DISTANCE - distance_2) / MAX_DISTANCE) * 100
            print(f"Kapasitas Terpakai 1: {fill_percentage_1:.2f}%, Kapasitas Terpakai 2: {fill_percentage_2:.2f}%")

            if fill_percentage_1 >= :
                GPIO.output(LED_PIN_1, GPIO.HIGH)
            else:
                GPIO.output(LED_PIN_1, GPIO.LOW)

            if fill_percentage_2 >= 100:
                GPIO.output(LED_PIN_2, GPIO.HIGH)
            else:
                GPIO.output(LED_PIN_2, GPIO.LOW)

            send_to_firebase(fill_percentage_1, fill_percentage_2)

            lcd.lcd_clear()
            fill_percentage_1_str = format(fill_percentage_1, ".1f")
            fill_percentage_2_str = format(fill_percentage_2, ".1f")
            lcd.lcd_display_string("TS 1: " + str(fill_percentage_1_str) + "%", 1, 0)
            lcd.lcd_display_string("TS 2: " + str(fill_percentage_2_str) + "%", 2, 0)

            time.sleep(20)
    except KeyboardInterrupt:
        print("Pengukuran Selesai!")
        lcd.lcd_clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
