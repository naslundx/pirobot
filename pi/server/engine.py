from dataclasses import dataclass
from enum import IntFlag, auto
import RPi.GPIO as GPIO


class Direction(IntFlag):
    FORWARD = auto()
    BACKWARD = auto()


@dataclass
class EngineData:
    pin_speed: int
    pin_direction: int
    _speed: int = 0
    _direction: Direction = Direction.FORWARD
    _controller: GPIO.PWM = None

    def setup(self):
        GPIO.setup(self.pin_speed, GPIO.OUT)
        GPIO.setup(self.pin_direction, GPIO.OUT)
        self.setDirection(Direction.FORWARD)
        self._controller = GPIO.PWM(self.pin_speed, 1000)

    def setSpeed(self, speed):
        self._speed = speed
        self._power()

    def setDirection(self, direction: Direction):
        self._direction = direction
        if self._direction == Direction.FORWARD:
            GPIO.output(self.pin_direction, GPIO.HIGH)
        else:
            GPIO.output(self.pin_direction, GPIO.LOW)

    def _power(self):
        self._controller.stop()
        self._controller.start(self._speed)

    def __str__(self):
        sign = '-' if self._direction == Direction.BACKWARD else ''
        return f"Speed: {sign}{self._speed}"


class Engine:
    def __init__(self):
        self.DEFAULT_SPEED = 15
        self.MOTOR_1 = EngineData(pin_speed=12, pin_direction=26)
        self.MOTOR_2 = EngineData(pin_speed=13, pin_direction=24)
        self.MOTOR_1.setup()
        self.MOTOR_2.setup()
        self.stop()

    @property
    def status(self):
        return f"{str(self.MOTOR_1)}, {str(self.MOTOR_2)}"

    def stop(self):
        self.setSpeed(0)

    def setSpeed(self, speed):
        if 0 <= speed <= 100:
            self.MOTOR_1.setSpeed(speed)
            self.MOTOR_2.setSpeed(speed)

    def forward(self):
        self.MOTOR_1.setDirection(Direction.FORWARD)
        self.MOTOR_2.setDirection(Direction.FORWARD)
        self.setSpeed(self.DEFAULT_SPEED)

    def turnLeft(self):
        self.MOTOR_1.setDirection(Direction.FORWARD)
        self.MOTOR_2.setDirection(Direction.BACKWARD)
        self.setSpeed(self.DEFAULT_SPEED)

    def turnRight(self):
        self.MOTOR_1.setDirection(Direction.BACKWARD)
        self.MOTOR_2.setDirection(Direction.FORWARD)
        self.setSpeed(self.DEFAULT_SPEED)

    def reverse(self):
        self.MOTOR_1.setDirection(Direction.BACKWARD)
        self.MOTOR_2.setDirection(Direction.BACKWARD)
        self.setSpeed(self.DEFAULT_SPEED)
