import math

class Vector:
    """Helper class for vector math (to avoid numpy dependency)."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def mul(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def div(self, scalar):
        if scalar == 0: return Vector(0, 0)
        return Vector(self.x / scalar, self.y / scalar)

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        m = self.mag()
        if m > 0:
            return self.div(m)
        return Vector(0, 0)

    def limit(self, max_val):
        if self.mag() > max_val:
            return self.normalize().mul(max_val)
        return self

