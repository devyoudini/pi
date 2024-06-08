import time
import OPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials, db


# class for database
class Database:
    def __init__(self) -> None:
        if not firebase_admin._apps:
            self.credentials = credentials.Certificate("./secret.json")
            firebase_admin.initialize_app(
                self.credentials,
                {"databaseURL": "https://ejeep-cffe9-default-rtdb.firebaseio.com/"},
            )

        self.db = db.reference(
            path="locations/Trn29IZ8DZNiqNhQKsRlgTWZNqM2",
        )
        self.passengerCountRef = self.db.child("passengerCount")
        self.count = self.getPassengerCount()

    def getPassengerCount(self) -> int:
        try:
            count = self.passengerCountRef.get()

            return count["passengerCount"] if count["passengerCount"] is not None else 0
        except Exception as e:
            print(f"Failed to get the passenger count: {e}")
            return 0

    def updatePassengerCount(self, increment: dict):
        try:
            passengerCount = self.getPassengerCount()
            newCount = passengerCount + increment

            if newCount is None:
                newCount = 0

            # Ensure count doesn't go negative or exceed max limit of 30
            if newCount < 0:
                newCount = 0
            elif newCount > 30:
                newCount = 30

            self.passengerCountRef.set({"passengerCount": newCount})
        except Exception as e:
            print(f"Failed to update passenger count: {e}")

    def addPassenger(self):
        self.updatePassengerCount(1)

    def takePassenger(self):
        self.updatePassengerCount(-1)


rdb = Database()

# GPIO pin definitions
ENTRANCE_SENSOR_PIN = "PA6"  # Replace with the correct pin for entrance sensor
EXIT_SENSOR_PIN = "PA20"  # Replace with the correct pin for exit sensor

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.SUNXI)
GPIO.setup(ENTRANCE_SENSOR_PIN, GPIO.IN)
GPIO.setup(EXIT_SENSOR_PIN, GPIO.IN)

# Passenger count
passenger_count = 0


def log_event(event):
    """Simple event logging."""
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}")


try:
    print("Passenger counter started. Press CTRL+C to exit.")
    while True:
        if GPIO.input(ENTRANCE_SENSOR_PIN):
            log_event("Passenger Enter")
            # passenger_count += 1
            # print(f"Count: {passenger_count}")
            rdb.addPassenger()
            time.sleep(2)
            pass
        elif GPIO.input(EXIT_SENSOR_PIN):
            log_event("Passenger Leave")
            # passenger_count -= 1
            # print(f"Count: {passenger_count}")
            rdb.takePassenger()
            time.sleep(2)
            pass
        time.sleep(1)  # Adjust delay as necessary

except KeyboardInterrupt:
    print("Exiting passenger counter.")
finally:
    GPIO.cleanup()
