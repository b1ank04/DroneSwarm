import random

from model.Vector import Vector
from config import Constants


class Drone:
    """Класс-исполнитель. Хранит состояние одного дрона."""

    def __init__(self, x, y):
        self.position = Vector(x, y)
        # Случайная начальная скорость
        self.velocity = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = Vector(0, 0)

    def update(self):
        """Обновление физики: Позиция += Скорость += Ускорение"""
        self.velocity = self.velocity.add(self.acceleration)
        self.velocity = self.velocity.limit(Constants.MAX_SPEED)
        self.position = self.position.add(self.velocity)
        self.acceleration = Vector(0, 0)  # Сброс ускорения на каждом кадре

        # Граничные условия (вылет за экран возвращает с другой стороны)
        if self.position.x > Constants.WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = Constants.WIDTH
        if self.position.y > Constants.HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = Constants.HEIGHT

    def apply_force(self, force):
        """Получение команды (силы) от центральной системы"""
        self.acceleration = self.acceleration.add(force)