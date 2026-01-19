import random

from model.Vector import Vector
from config import Constants


class Drone:
    """Agent class representing a single drone."""

    def __init__(self, x, y):
        self.position = Vector(x, y)
        self.velocity = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = Vector(0, 0)

    def update(self):
        """Update physics: Postion += Velocity += Acceleration"""
        self.velocity = self.velocity.add(self.acceleration)
        self.velocity = self.velocity.limit(Constants.MAX_SPEED)
        self.position = self.position.add(self.velocity)
        self.acceleration = Vector(0, 0)

        # Boundary wrap-around
        if self.position.x > Constants.WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = Constants.WIDTH
        if self.position.y > Constants.HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = Constants.HEIGHT

    def apply_force(self, force):
        """Apply a force (acceleration) to the drone."""
        self.acceleration = self.acceleration.add(force)