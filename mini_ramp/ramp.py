from __future__ import division
import collections
import math
import sympy
from turtle import *

class Board(object):
    def __init__(self):
        self.length = 0.787
        self.height = 0.08
        self.kick = 0.152
        self.truck = 0.102
        self.center = self.length - 2 * self.kick - 2 * self.truck

    def draw(self, x, y, angle, scale):
        penup()
        goto(x * scale, y * scale)
        pendown()

        x += math.cos(angle) * (self.kick + self.truck / 2)
        y += math.sin(angle) * (self.kick + self.truck / 2)
        goto(x * scale, y * scale)

        x += math.sin(angle) * self.height
        y -= math.cos(angle) * self.height
        goto(x * scale, y * scale)

        x -= math.sin(angle) * self.height
        y += math.cos(angle) * self.height
        goto(x * scale, y * scale)

        x += math.cos(angle) * (self.center + self.truck)
        y += math.sin(angle) * (self.center + self.truck)
        goto(x * scale, y * scale)

        x += math.sin(angle) * self.height
        y -= math.cos(angle) * self.height
        goto(x * scale, y * scale)

        x -= math.sin(angle) * self.height
        y += math.cos(angle) * self.height
        goto(x * scale, y * scale)

        x += math.cos(angle) * (self.kick + self.truck / 2)
        y += math.sin(angle) * (self.kick + self.truck / 2)

        goto(x * scale, y * scale)


class Transition(object):
    CIRCULAR = 0
    ELLIPTICAL = 1
    def __init__(self, width, height, x_radius=None,
                 curve=CIRCULAR):
        self.width = width
        self.height = height
        self.x_radius = x_radius
        self.curve = curve

        self.x, self.y, dx, dy = sympy.symbols("x y dx dy", real=True)
        a, b = sympy.symbols("a b", positive=True, real=True)

        self.ellipse = ((self.x - dx) / a) ** 2 + ((self.y - dy) / b) ** 2 - 1

        self.ellipse = self.ellipse.subs([(dx, self.width),
                                          (dy, b)])

        if curve == Transition.CIRCULAR:
            self.ellipse = self.ellipse.subs([(a, b)])

        ellipse = self.ellipse.subs([(self.x, 0),
                                     (self.y, self.height)])

        if curve == Transition.CIRCULAR:
            self.x_radius = self.y_radius = max(sympy.solve(ellipse, b))
            self.angle = math.asin(self.width / self.x_radius)
            self.arc_length = self.x_radius * self.angle

        elif curve == Transition.ELLIPTICAL:
            self.y_radius = max(sympy.solve(ellipse, b))
            # TODO: Fix me
            self.angle = 0
            self.arc_length = 0


        self.ellipse = self.ellipse.subs([(a, self.x_radius),
                                          (b, self.y_radius)])


    def draw(self, x, y, scale, steps=20, inverse=False):
        penup()
        goto(x * scale, y * scale)
        pendown()

        increment = self.width / (steps - 1)
        x_pos = 0
        for i in range(steps):
            actual_x = x_pos if not inverse else self.width - x_pos
            ellipse =  self.ellipse.subs([(self.x, actual_x)])
            y_pos = min(sympy.solve(ellipse, self.y))

            goto((x + x_pos) * scale, (y + y_pos) * scale)
            x_pos += increment


class PalletHBlock(object):
    def __init__(self):
        self.pallets = []
        self.width = 0
        self.height = 0

    def add_pallet(self, pallet):
        self.pallets.append(pallet)
        self.width += pallet.width
        self.height = max(self.height, pallet.height)

    def draw(self, x, y, scale):
        for pallet in self.pallets:
            pallet.draw(x, y, scale)
            x += pallet.width

class Pallet(object):
    SIZE = [1.2, 0.8, 0.15]
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, x, y, scale):
        penup()
        goto(x * scale, y * scale)
        pendown()
        goto((x + self.width) * scale, y * scale)
        goto((x + self.width) * scale, (y + self.height) * scale)
        goto(x * scale, (y + self.height) * scale)
        goto(x * scale, y * scale)


class Ramp(object):
    def __init__(self):
        self.transition = Transition(2 * (Pallet.SIZE[1] - Pallet.SIZE[2]),
                                     Pallet.SIZE[1])

        self.deck = PalletHBlock()
        for i in range(2):
            self.deck.add_pallet(Pallet(Pallet.SIZE[2], Pallet.SIZE[1]))

        self.base = PalletHBlock()
        for i in range(6):
            self.base.add_pallet(Pallet(Pallet.SIZE[1], Pallet.SIZE[2]))

        self.board = Board()


    def draw(self, scale):
        self.base.draw(-self.base.width / 2, -self.base.height, scale)
        self.deck.draw(-self.base.width / 2, 0, scale)
        self.deck.draw(self.base.width / 2 - self.deck.width, 0, scale)

        self.transition.draw(-self.base.width / 2 + self.deck.width, 0, scale)
        self.transition.draw(self.base.width / 2 - self.deck.width -
                             self.transition.width, 0, scale, inverse=True)

        angle = -math.pi / 7
        x_offset = self.board.length * math.cos(angle) / 2
        y_offset = self.board.length * math.sin(angle) / 2
        self.board.draw(-self.base.width / 2 + self.deck.width - x_offset,
                        self.transition.height - y_offset, angle, scale)
        exitonclick()

    def print_details(self):
        print "Ramp Details"
        print "------------"
        print ""

        details = collections.OrderedDict()
        details["Total length:"] = self.base.width
        details["Total width:"]  = Pallet.SIZE[0]
        details["Total height:"] = self.base.height + self.deck.height
        details["Sep1"] = None
        details["Deck height:"] = self.deck.height
        details["Deck length:"] = self.deck.width
        details["Flat length:"] = (self.base.width -
                       2 * (self.deck.width + self.transition.width))
        details["Wood length:"] = (self.base.width -
                                   2 * self.transition.width +
                                   2 * self.transition.arc_length)
        details["Sep2"] = None
        if self.transition.curve == Transition.CIRCULAR:
            details["Tranny radius:"] = self.transition.x_radius
        elif self.transition.curve == Transition.ELLIPTICAL:
            details["Tranny x radius:"] = self.transition.x_radius
            details["Tranny y radius:"] = self.transition.y_radius
        details["Tranny length:"] = self.transition.width

        for name, value in details.iteritems():
            if value == None:
                print ""
                continue
            value = float(value)
            print "{:15} {:>4.2f} m {:>8.2f} ft".format(name, value,
                                                        value * 3.328)

        print "{:15} {:>4.2f} deg".format("Maximum angle:", self.transition.angle * 180 / math.pi)


