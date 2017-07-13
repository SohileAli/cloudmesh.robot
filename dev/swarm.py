import math
from marvelmind import MarvelmindHedge
import requests
import time


class Robot(object):

    def __init__(self, number, ip, final_x, final_y, hedge=MarvelmindHedge(tty='/dev/tty.usbmodem1421'), epsilon=4):
        self.number = int(number)
        self.ip = ip
        self.fx = final_x
        self.fy = final_y
        self.epsilon = epsilon
        self.hedge = hedge
        self.addr, self.last_x, self.last_y, self.last_z, self.last_t = hedge.number_position(self.number)
        self.done = False

    def update(self):
        return self.hedge.number_position(self.number)

    def find_vectors(self, last_x, last_y, current_x, current_y, end_x, end_y):
        """
        finds the vectors that connect three points
        :param last_x: Number
        :param last_y: Number
        :param current_x: Number
        :param current_y: Number
        :param end_x: Number
        :param end_y: Number
        :return: List, List
        """
        v1 = [(current_x - last_x), (current_y - last_y)]
        v2 = [(end_x - current_x), (end_y - current_y)]
        return v1, v2

    def find_angle(self, x, y):
        """
        finds angle from the origin
        :param x: Number
        :param y: Number
        :return: Number
        """
        if x >= 0:
            if y >= 0:
                return math.degrees(math.atan(y / x))
            elif y <= 0:
                return 270 - math.degrees(math.atan(y / x))
        else:
            return 180 + math.atan(y / x)

    def find_delta(self, v1, v2):
        """
        finds the angle between two vectors
        :param v1: List
        :param v2: List
        :return: Number
        """
        unit_factor1 = math.sqrt((v1[0] ** 2) + (v1[1] ** 2))
        unit_factor2 = math.sqrt((v2[0] ** 2) + (v2[1] ** 2))
        u1 = [(v1[0] / unit_factor1), (v1[1] / unit_factor1)]
        u2 = [(v2[0] / unit_factor2), (v2[1] / unit_factor2)]
        return math.acos((u1[0] * u2[0]) + (u1[1] * u2[1]))

    def turn_direction(self, angle1, angle2):
        """
        returns the direction that the robot must turn
        :param angle1: Number
        :param angle2: Number
        :return: String
        """
        if angle1 > angle2:
            return "right"
        elif 0 <= angle1 <= 90 and 270 <= angle2 <= 360:
            return "right"
        elif 0 <= angle2 <= 90 and 270 <= angle1 <= 360:
            return "left"
        elif angle2 > angle1:
            return "left"

    def move(self, direction, value=None):
        """
        sends move commands to server
        :param direction: String
        :param value: None or Number
        """
        if direction == "right":
            payload = {'TURN': str(value)}
        elif direction == "left":
            payload = {'TURN': str(value)}
        elif direction == "forward":
            payload = {'FORWARD': str(value)}
        elif direction == "stop":
            payload = {'STOP': 'ON'}
        elif direction == "backward":
            payload = {'BACKWARD': 'ON'}
        else:
            print ("ERROR: unknown direction:", direction)

        try:
            headers = {'User-Agent': "Car"}
            r = requests.get('http://' + self.ip, headers=headers, params=payload)
        except Exception as e:
            print(type(e), e)

    def turn(self):
        """
        calculates turn angle and sends turn command to robot
        """
        addr, cx, cy, cz, ct = self.update() # get current position
        v1, v2 = self.find_vectors(self.last_x, self.last_y, cx, cy, self.fx, self.fy)  # get vector positions
        delta_angle = self.find_delta(v1, v2)  # get angle change
        angle1 = self.find_angle(v1[0], v1[2])  # get unit vector angles
        angle2 = self.find_angle(v2[0], v2[1])
        direction = self.turn_direction(angle1, angle2)  # get turn direction
        self.move(direction, delta_angle)  # turn robot
        self.last_x = cx  # redefine previous positions
        self.last_y = cy

    def go(self):
        """
        sends forward command to robot or turns robot off
        """
        a, cx, cy, cz, ct = self.update()
        if abs(cx - self.fx) < self.epsilon and abs(cy - self.fy) < self.epsilon:
            self.done = True
        else:
            self.move('forward', .5)


class RobotSwarm(object):

    def __init__(self, file):
        """
        Holds multiple robots.
        :param robots:
        """
        self.file = file
        self.done = False

    def make_robots(self):
        filename = self.file
        f = open(filename)
        lines = f.readlines()
        f.close()
        robots = []
        for line in lines:
            name, position = line.split(":")
            number, ip = name.split(" ")
            endx, endy = position.split(",")
            robots.append(Robot(number, ip, endx, endy))
        self.robots = robots

    def done_check(self):
        for robot in self.robots:
            if not robot.done:
                self.done = False
                break
            else:
                self.done = True

    def run(self):
        self.make_robots()
        self.robots[0].hedge.start()
        time.sleep(2)
        for robot in self.robots:
            robot.move("forward", .5)
        while not self.done:
            for robot in self.robots:
                robot.turn()
            for robot in self.robots:
                robot.go()
            self.done_check()
