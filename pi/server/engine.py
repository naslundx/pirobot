import RPi.GPIO as GPIO

class Engine:
    def __init__(self):
        self.PIN_MOTOR1_SPEED = 12
        self.PIN_MOTOR1_DIRECTION = 26
        self.PIN_MOTOR2_SPEED = 13
        self.PIN_MOTOR2_DIRECTION = 24
        self.SPEED = 20

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_MOTOR1_SPEED, GPIO.OUT)
        GPIO.setup(self.PIN_MOTOR2_SPEED, GPIO.OUT)
        GPIO.setup(self.PIN_MOTOR1_DIRECTION, GPIO.OUT)
        GPIO.setup(self.PIN_MOTOR2_DIRECTION, GPIO.OUT)

        self.MOTOR_1 = GPIO.PWM(self.PIN_MOTOR1_SPEED, 1000)
        self.MOTOR_2 = GPIO.PWM(self.PIN_MOTOR2_SPEED, 1000)

        self.status = ""
        self.stop()

    def stop(self):
        self.MOTOR_1.stop()
        self.MOTOR_2.stop()
        self.status = "stopped"

    def _power(self):
        self.MOTOR_1.start(self.SPEED)
        self.MOTOR_2.start(self.SPEED)
        self.status = "running"

    def setSpeed(self, value):
        if 0 <= value <= 100:
            self.SPEED = value / 2

    def forward(self):
        GPIO.output(self.PIN_MOTOR1_DIRECTION, GPIO.HIGH)
        GPIO.output(self.PIN_MOTOR2_DIRECTION, GPIO.HIGH)
        self._power()

    def turn(self, direction):
        if direction == "left":
            GPIO.output(self.PIN_MOTOR1_DIRECTION, GPIO.HIGH)
            GPIO.output(self.PIN_MOTOR2_DIRECTION, GPIO.LOW)

        elif direction == "right":
            GPIO.output(self.PIN_MOTOR1_DIRECTION, GPIO.LOW)
            GPIO.output(self.PIN_MOTOR2_DIRECTION, GPIO.HIGH)

        self._power()

    def reverse(self):
        GPIO.output(self.PIN_MOTOR1_DIRECTION, GPIO.LOW)
        GPIO.output(self.PIN_MOTOR2_DIRECTION, GPIO.LOW)
        self._power()
