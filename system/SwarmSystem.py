import math
import random
import pygame

from config import Constants
from model.Drone import Drone
from model.Vector import Vector

class SwarmSystem:
    """Центральная интеллектуальная подсистема (Мозг)."""

    def __init__(self, num_drones):
        self.drones = [Drone(random.randint(0, Constants.WIDTH), random.randint(0, Constants.HEIGHT)) for _ in range(num_drones)]
        self.show_vision_radius = False

    def toggle_vision(self):
        """Переключатель режима отображения радиуса"""
        self.show_vision_radius = not self.show_vision_radius

    def update(self, target_pos):
        target_vec = Vector(target_pos[0], target_pos[1])

        # Радиус, внутри которого дрон переходит в режим "парковки"
        # Он должен быть достаточно большим, чтобы вместить всех дронов
        PARKING_RADIUS = 100

        for drone in self.drones:
            # Считаем дистанцию до цели
            dist_to_target = math.sqrt((drone.position.x - target_vec.x) ** 2 +
                                       (drone.position.y - target_vec.y) ** 2)

            # Получаем соседей (нужны всегда для избегания столкновений)
            neighbors = self._get_neighbors(drone)

            # --- ЛОГИКА ПАРКОВКИ (Внутри радиуса) ---
            if dist_to_target < PARKING_RADIUS:
                # 1. Считаем ТОЛЬКО силу разделения (чтобы не наезжать друг на друга)
                separation = self._separation(drone, neighbors)

                # Усиливаем разделение, чтобы они активнее освобождали место
                separation = separation.mul(Constants.W_SEPARATION * 2.0)

                # 2. Применяем силу
                drone.apply_force(separation)

                # 3. Обновляем физику
                drone.update()

                # 4. СИЛЬНОЕ ТОРМОЖЕНИЕ (Трение)
                # Вместо обычного движения, мы гасим скорость очень сильно (0.8)
                # Это не дает им разлететься, когда их толкает сила Separation
                drone.velocity = drone.velocity.mul(0.85)

            # --- ЛОГИКА ПОЛЕТА (Снаружи радиуса) ---
            else:
                separation = self._separation(drone, neighbors)
                alignment = self._alignment(drone, neighbors)
                cohesion = self._cohesion(drone, neighbors)
                seek_target = self._seek(drone, target_vec)

                separation = separation.mul(Constants.W_SEPARATION)
                alignment = alignment.mul(Constants.W_ALIGNMENT)
                cohesion = cohesion.mul(Constants.W_COHESION)
                seek_target = seek_target.mul(Constants.W_TARGET)

                total_force = separation.add(alignment).add(cohesion).add(seek_target)

                drone.apply_force(total_force)
                drone.update()

    def _get_neighbors(self, drone):
        """Находит всех дронов в радиусе видимости"""
        neighbors = []
        for other in self.drones:
            if other == drone: continue
            # Расстояние между точками
            d = math.sqrt((drone.position.x - other.position.x) ** 2 + (drone.position.y - other.position.y) ** 2)
            if d < Constants.NEIGHBOR_RADIUS:
                neighbors.append(other)
        return neighbors

    # --- АЛГОРИТМЫ ПОВЕДЕНИЯ ---

    def _seek(self, drone, target):
        """Стремление к цели с учетом плавного торможения (Arrival)"""
        desired = target.sub(drone.position)
        distance = desired.mag()  # Дистанция до цели

        desired = desired.normalize()

        # --- ЛОГИКА ARRIVAL ---
        if distance < Constants.SLOWING_RADIUS:
            # Если мы внутри радиуса торможения, скорость пропорциональна расстоянию
            # Map: distance [0...100] -> speed [0...MAX_SPEED]
            m = (distance / Constants.SLOWING_RADIUS) * Constants.MAX_SPEED
            desired = desired.mul(m)
        else:
            # Иначе летим на полной скорости
            desired = desired.mul(Constants.MAX_SPEED)
        # ----------------------

        steer = desired.sub(drone.velocity)
        return steer.limit(Constants.MAX_FORCE)

    def _separation(self, drone, neighbors):
        """Правило 1: Избегание столкновений"""
        steering = Vector(0, 0)
        count = 0
        for other in neighbors:
            d = math.sqrt((drone.position.x - other.position.x) ** 2 + (drone.position.y - other.position.y) ** 2)
            if d == 0: continue
            # Вектор ОТ соседа к дрону
            diff = drone.position.sub(other.position)
            diff = diff.normalize().div(d)  # Чем ближе, тем сильнее отталкивание
            steering = steering.add(diff)
            count += 1

        if count > 0:
            steering = steering.div(count)
            steering = steering.normalize().mul(Constants.MAX_SPEED)
            steering = steering.sub(drone.velocity)
            steering = steering.limit(Constants.MAX_FORCE)
        return steering

    def _alignment(self, drone, neighbors):
        """Правило 2: Согласование скорости (лететь туда же, куда и остальные)"""
        steering = Vector(0, 0)
        count = 0
        for other in neighbors:
            steering = steering.add(other.velocity)
            count += 1

        if count > 0:
            steering = steering.div(count)  # Средняя скорость соседей
            steering = steering.normalize().mul(Constants.MAX_SPEED)
            steering = steering.sub(drone.velocity)
            steering = steering.limit(Constants.MAX_FORCE)
        return steering

    def _cohesion(self, drone, neighbors):
        """Правило 3: Сплоченность (лететь в центр группы)"""
        center_mass = Vector(0, 0)
        count = 0
        for other in neighbors:
            center_mass = center_mass.add(other.position)
            count += 1

        if count > 0:
            center_mass = center_mass.div(count)
            return self._seek(drone, center_mass)  # Используем _seek к центру масс
        return Vector(0, 0)

    def draw(self, screen):
        """Отрисовка дронов"""
        for drone in self.drones:
            # --- Добавляем этот блок ---
            if self.show_vision_radius:
                # Рисуем тонкий круг вокруг дрона
                # (цвет серый, координаты int, радиус NEIGHBOR_RADIUS, толщина 1)
                pygame.draw.circle(screen, (50, 50, 50),
                                   (int(drone.position.x), int(drone.position.y)),
                                   Constants.NEIGHBOR_RADIUS, 1)
            # ---------------------------
            # Рисуем треугольник, ориентированный по скорости
            angle = math.atan2(drone.velocity.y, drone.velocity.x)
            x, y = drone.position.x, drone.position.y
            r = 6  # Размер дрона

            # Вершины треугольника (математика поворота 2D)
            p1 = (x + r * math.cos(angle), y + r * math.sin(angle))  # Нос
            p2 = (x + r * math.cos(angle + 2.5), y + r * math.sin(angle + 2.5))  # Левое крыло
            p3 = (x + r * math.cos(angle - 2.5), y + r * math.sin(angle - 2.5))  # Правое крыло

            pygame.draw.polygon(screen, Constants.DRONE_COLOR, [p1, p2, p3])