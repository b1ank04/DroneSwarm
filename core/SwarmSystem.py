import math
import random
import pygame

from config import Constants
from model.Drone import Drone
from model.Vector import Vector

class SwarmSystem:
    """Manages the swarm logic and individual drone behaviors."""

    def __init__(self, num_drones):
        self.drones = [Drone(random.randint(0, Constants.WIDTH), random.randint(0, Constants.HEIGHT)) for _ in range(num_drones)]
        self.show_vision_radius = False

    def toggle_vision(self):
        """Toggle vision radius display."""
        self.show_vision_radius = not self.show_vision_radius

    def update(self, target_pos):
        target_vec = Vector(target_pos[0], target_pos[1])

        for drone in self.drones:
            dist_to_target = math.sqrt((drone.position.x - target_vec.x) ** 2 +
                                       (drone.position.y - target_vec.y) ** 2)

            neighbors = self._get_neighbors(drone)

            # --- 1. РЕЖИМ ПАРКОВКИ (Parking State) ---
            if dist_to_target < Constants.PARKING_RADIUS:
                # Усиленное разделение, чтобы не "склеиваться" в точке финиша
                separation = self._separation(drone, neighbors)
                separation = separation.mul(Constants.W_SEPARATION * 2.0)

                drone.apply_force(separation)
                drone.update()

                # Сильное трение (тормоза) для остановки
                drone.velocity = drone.velocity.mul(0.85)

            # --- 2. РЕЖИМ ПОЛЕТА (Flight State) с Адаптивным Интеллектом ---
            else:
                # A. Анализ контекста (Context Awareness)
                neighbor_count = len(neighbors)

                # Берем базовые веса из констант как отправную точку
                curr_w_sep = Constants.W_SEPARATION
                curr_w_align = Constants.W_ALIGNMENT
                curr_w_coh = Constants.W_COHESION
                curr_w_target = Constants.W_TARGET

                # B. Адаптация весов (Fuzzy Rules)
                # Сценарий 1: Плотная толпа / Опасность столкновения
                if neighbor_count > 3:
                    curr_w_sep *= 2.5  # Приоритет: избегать столкновений
                    curr_w_align *= 1.5  # Приоритет: двигаться синхронно с потоком
                    curr_w_target *= 0.5  # Уменьшаем желание рваться к цели любой ценой

                # Сценарий 2: Одиночный полет
                elif neighbor_count == 0:
                    curr_w_coh = 0.0  # Отключаем сплоченность (не с кем кучковаться)
                    curr_w_target *= 1.2  # Можно лететь к цели быстрее

                # C. Расчет сил с учетом адаптивных весов
                separation = self._separation(drone, neighbors).mul(curr_w_sep)
                alignment = self._alignment(drone, neighbors).mul(curr_w_align)
                cohesion = self._cohesion(drone, neighbors).mul(curr_w_coh)
                seek_target = self._seek(drone, target_vec).mul(curr_w_target)

                # D. Сумма сил
                total_force = separation.add(alignment).add(cohesion).add(seek_target)

                drone.apply_force(total_force)
                drone.update()

    def _get_neighbors(self, drone):
        """Find all drones within neighbor radius."""
        neighbors = []
        for other in self.drones:
            if other == drone: continue
            # Distance between points
            d = math.sqrt((drone.position.x - other.position.x) ** 2 + (drone.position.y - other.position.y) ** 2)
            if d < Constants.NEIGHBOR_RADIUS:
                neighbors.append(other)
        return neighbors

    # --- BEHAVIOR ALGORITHMS ---

    def _seek(self, drone, target):
        """Seek target with Arrival behavior."""
        desired = target.sub(drone.position)
        distance = desired.mag()  # Distance to target

        desired = desired.normalize()

        # --- ARRIVAL LOGIC ---
        if distance < Constants.SLOWING_RADIUS:
            # Inside slowing radius, speed proportional to distance
            # Map: distance [0...100] -> speed [0...MAX_SPEED]
            m = (distance / Constants.SLOWING_RADIUS) * Constants.MAX_SPEED
            desired = desired.mul(m)
        else:
            # Otherwise full speed
            desired = desired.mul(Constants.MAX_SPEED)
        # ----------------------

        steer = desired.sub(drone.velocity)
        return steer.limit(Constants.MAX_FORCE)

    def _separation(self, drone, neighbors):
        """Rule 1: Separation (avoid collisions)."""
        steering = Vector(0, 0)
        count = 0
        for other in neighbors:
            d = math.sqrt((drone.position.x - other.position.x) ** 2 + (drone.position.y - other.position.y) ** 2)
            if d == 0: continue
            # Vector away from neighbor
            diff = drone.position.sub(other.position)
            diff = diff.normalize().div(d)  # Weight by distance
            steering = steering.add(diff)
            count += 1

        if count > 0:
            steering = steering.div(count)
            steering = steering.normalize().mul(Constants.MAX_SPEED)
            steering = steering.sub(drone.velocity)
            steering = steering.limit(Constants.MAX_FORCE)
        return steering

    def _alignment(self, drone, neighbors):
        """Rule 2: Alignment (match velocity)."""
        steering = Vector(0, 0)
        count = 0
        for other in neighbors:
            steering = steering.add(other.velocity)
            count += 1

        if count > 0:
            steering = steering.div(count)  # Average velocity
            steering = steering.normalize().mul(Constants.MAX_SPEED)
            steering = steering.sub(drone.velocity)
            steering = steering.limit(Constants.MAX_FORCE)
        return steering

    def _cohesion(self, drone, neighbors):
        """Rule 3: Cohesion (stay with group)."""
        center_mass = Vector(0, 0)
        count = 0
        for other in neighbors:
            center_mass = center_mass.add(other.position)
            count += 1

        if count > 0:
            center_mass = center_mass.div(count)
            return self._seek(drone, center_mass)  # Steer towards center
        return Vector(0, 0)

    def draw(self, screen):
        for drone in self.drones:
            if self.show_vision_radius:
                pygame.draw.circle(screen, (50, 50, 50),
                                   (int(drone.position.x), int(drone.position.y)),
                                   Constants.NEIGHBOR_RADIUS, 1)

            # Draw drone (triangle oriented by velocity)
            angle = math.atan2(drone.velocity.y, drone.velocity.x)
            x, y = drone.position.x, drone.position.y
            r = 6  # Drone size

            # Triangle vertices (2D rotation)
            p1 = (x + r * math.cos(angle), y + r * math.sin(angle))  # Nose
            p2 = (x + r * math.cos(angle + 2.5), y + r * math.sin(angle + 2.5))  # Left wing
            p3 = (x + r * math.cos(angle - 2.5), y + r * math.sin(angle - 2.5))  # Right wing

            pygame.draw.polygon(screen, Constants.DRONE_COLOR, [p1, p2, p3])