import network
import ubinascii
import time
import utime
import machine
# import socket
from machine import Pin, PWM



class motor(object):
    def __init__(self, name):
        self.forward_speed = 1023
        if name == "left":
            self.pin_speed = 4
            self.pin_direction = 2
        elif name == "right":
            self.pin_speed = 5
            self.pin_direction = 0

        self.speed = PWM(Pin(self.pin_speed), freq=1000, duty=0)
        self.direction = Pin(self.pin_direction, Pin.OUT)
        self.name = name
        self.d = 1023

    def forward(self):
        self.direction.low()
        self.duty(self.d)

    def backward(self):
        self.direction.high()
        self.duty(self.d)

    def stop(self):
        self.duty(0)

    def duty(self, d):
        PWM(Pin(self.pin_speed), freq=1000, duty=d)




class speed_meter(object):
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.status = Pin.value(self.pin)
        self.counter = 0

    def update(self):
        self.status = Pin.value(self.pin)

    def tick_up(self):
        if self.status == 1:
            self.counter += 1

    def get(self):
        print ("GET")
        turn = True
        t0 = utime.ticks_us()
        delta_t = 0
        count_start = self.counter
        print ("CN", self.counter)
        while delta_t < 200000:
            self.update()
            print ("L", delta_t, self.status, self.counter)
            if self.status == 1 and turn:
                print("A")
                turn = False
                self.counter += 1
            elif self.status == 0:
                print ("B")
                turn = True
                delta_t = utime.ticks_diff(utime.ticks_us(), t0)
        count_dt = self.counter - count_start
        print (count_dt)
        return count_dt, self.counter

    def rpm(self):
        return (self.get() / 20) * 300

smr = speed_meter(16)

sml = speed_meter(15)

right = motor("right")
left = motor("left")
led = LED(2)
led.blink(5)

print("hello")

for i in range(0, 1):
    # while True:
    print ("I:", i)
    print(smr.get())
    time.sleep(0.5)
    print("R:", i)
    print(sml.get())
    time.sleep(.5)


def motor_adjuster(right_meter, left_meter):
    rpm_right = right_meter.get()
    rpm_left = left_meter.get()
    rl_ratio = rpm_right / rpm_left
    if rl_ratio < .99:             #if right wheel speed is less than 99% left wheel
        left.d = left.d * rl_ratio #lower left duty to accomodate
    elif rl_ratio > 1.01:
        right.d = (rpm_left / rpm_right) * right.d
    else:
        pass



    
