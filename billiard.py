from __future__ import annotations
import pygame
from sys import exit
from typing import Union
from math import dist, radians, cos, sin
from itertools import combinations


class Vector:
    def __init__(self, end_pos: tuple[float, float], start_pos: tuple[float, float] = (.0, .0)):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.length = dist(self.end_pos, self.start_pos)

    def normalize(self) -> Vector:
        return Vector(
            end_pos=(
                (self.end_pos[0] - self.start_pos[0]) / self.length,
                (self.end_pos[1] - self.start_pos[1]) / self.length
            )
        )

    def __repr__(self):
        return f'Vector({self.length=}, {self.end_pos=}, {self.start_pos=})'

    def __mul__(self, other: Union[Vector, float]) -> Union[Vector, float]:
        return self.end_pos[0] * other.end_pos[0] + self.end_pos[1] * self.end_pos[1] if isinstance(other, Vector) else Vector(
            end_pos=(
                self.end_pos[0] * other, self.end_pos[1] * other
            )
        )

    def __sub__(self, other: Vector) -> Vector:
        return Vector(
            end_pos=(
                self.end_pos[0] - self.end_pos[0],
                self.end_pos[1] - self.end_pos[1]
            )
        )

    def __add__(self, other: Vector) -> Vector:
        return Vector(
            end_pos=(
                self.end_pos[0] + self.end_pos[0],
                self.end_pos[1] + self.end_pos[1]
            )
        )


class Ball:
    def __init__(
            self,
            window,
            center: tuple[Union[int, float], Union[int, float]],
            radius: float,
            velocity: float,
            angle: float,
            color: tuple = (255, 255, 255, 100),
            width: int = 0
    ):
        self._window = window
        self.x = center[0]
        self.y = center[1]
        self.radius = radius
        self.angle = angle
        self.mass = 50
        self.color = color
        self.width = width
        self.velocity = velocity
        self.velocity_x = cos(radians(self.angle))
        self.velocity_y = sin(radians(self.angle))
        self.vector = Vector(end_pos=(self.velocity * self.velocity_x, self.velocity * self.velocity_y))

    @staticmethod
    def _calculate_velocity(ball: Ball, other: Ball) -> Vector:
        unit_normal = Vector(start_pos=(ball.x, ball.y), end_pos=(other.x, other.y)).normalize()
        unit_tangent = Vector(end_pos=(-unit_normal.end_pos[1], unit_normal.end_pos[0]))
        return (unit_normal * ((unit_normal * ball.vector * (ball.mass - other.mass) + other.vector * unit_normal * 2 * other.mass) / ball.mass + other.mass) + ball.vector * (unit_tangent * unit_tangent)).normalize() * -1

    def collision(self, other: Ball):
        if dist([self.x, self.y], [other.x, other.y]) <= self.radius + other.radius:
            vec1 = self._calculate_velocity(self, other)
            vec2 = self._calculate_velocity(other, self)
            self.velocity, other.velocity = other.velocity, self.velocity
            self.velocity_x, self.velocity_y = vec1.end_pos[0], vec1.end_pos[1]
            other.velocity_x, other.velocity_y = vec2.end_pos[0], vec2.end_pos[1]

    def update(self):
        if self.x + self.radius > self._window.get_width() or self.x - self.radius < 0:
            self.velocity_x *= -1
        if self.y + self.radius > self._window.get_height() or self.y - self.radius < 0:
            self.velocity_y *= -1
        self.x += self.velocity * self.velocity_x
        self.y += self.velocity * self.velocity_y
        pygame.draw.circle(self._window, color=self.color, center=(self.x, self.y), radius=self.radius,
                           width=self.width)

    def x_ray(self):
        pygame.draw.line(self._window, color=(100, 100, 255), start_pos=(self.x, self.y), end_pos=(
            self.x + 100 * self.velocity_x,
            self.y + 100 * self.velocity_y),
                         width=5)
        pygame.draw.line(self._window, color=(100, 255, 100), start_pos=(self.x, self.y), end_pos=(
            self.x,
            self.y + 100 * self.velocity_y),
                         width=5)
        pygame.draw.line(self._window, color=(255, 100, 100), start_pos=(self.x, self.y), end_pos=(
            self.x + 100 * self.velocity_x,
            self.y), width=5)


class Window:
    def __init__(self, title: str):
        self.window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.balls = [
            Ball(self.window, (500, 680), 50, 5, 45),
            Ball(self.window, (700, 100), 50, 3, 45),
            Ball(self.window, (100, 100), 50, 2, 0),
            Ball(self.window, (1000, 800), 50, 5, 0),
            Ball(self.window, (1500, 900), 50, 5, 15),
            Ball(self.window, (1200, 800), 50, 5, 360),
            Ball(self.window, (1300, 800), 50, 5, 75),
            Ball(self.window, (1000, 900), 50, 5, 94)
        ]

    def update(self):
        self.window.fill((0, 0, 0))
        [ball.update() for ball in self.balls]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_TAB]:
            [ball.x_ray() for ball in self.balls]
        [ball.collision(other) for ball, other in combinations(self.balls, 2)]
        pygame.display.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
            self.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Window('Balls').run()
