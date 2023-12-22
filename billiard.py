from __future__ import annotations
import pygame
from sys import exit
from typing import Union
from math import dist, radians, cos, sin, atan2, degrees, fabs
from itertools import combinations
from dataclasses import dataclass


class Vector:
    __slots__ = 'start_pos', 'end_pos', 'length'

    def __init__(self, end_pos: list[float, float], start_pos: list[float, float] = (.0, .0)):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.length = dist(self.end_pos, self.start_pos)

    def normalize(self) -> Vector:
        return Vector(
            end_pos=[
                (self.end_pos[0] - self.start_pos[0]) / self.length,
                (self.end_pos[1] - self.start_pos[1]) / self.length
            ]
        )

    def add(self, other: Vector) -> Vector:
        return Vector(
            end_pos=[
                self.end_pos[0] + other.end_pos[0],
                self.end_pos[1] + other.end_pos[1]
            ]
        )

    @staticmethod
    def sub(vec1: Vector, vec2: Vector) -> Vector:
        return Vector(
            end_pos=[
                vec1.end_pos[0] - vec2.end_pos[0],
                vec1.end_pos[1] - vec2.end_pos[1]
            ]
        )

    def mul(self, other: Union[Vector, float]) -> Union[Vector, float]:
        return self.end_pos[0] * other.end_pos[0] + self.end_pos[1] * other.end_pos[1] if isinstance(other, Vector) else Vector(
            end_pos=[
                self.end_pos[0] * other, self.end_pos[1] * other
            ]
        )

    def __repr__(self):
        return f'Vector({self.length=}, {self.end_pos=}, {self.start_pos=})'

    def __mul__(self, other: Union[Vector, float]) -> Union[Vector, float]:
        return self.mul(other)

    def __rmul__(self, other: Union[Vector, float]) -> Union[Vector, float]:
        return self.mul(other)

    def __sub__(self, other: Vector) -> Vector:
        return self.sub(self, other)

    def __rsub__(self, other: Vector) -> Vector:
        return self.sub(other, self)

    def __add__(self, other: Vector) -> Vector:
        return self.add(other)

    def __radd__(self, other: Vector) -> Vector:
        return self.add(other)


class Ball:
    __slots__ = 'window', 'x', 'y', 'radius', 'mass', 'color', 'width', 'vector'

    def __init__(self, window, center: tuple[Union[int, float], Union[int, float]], radius: float, velocity: float, angle: float, color: tuple = (255, 255, 255, 100), width: int = 0):
        self.window = window
        self.x = center[0]
        self.y = center[1]
        self.radius = radius
        self.mass = radius
        self.color = color
        self.width = width
        self.vector = Vector(end_pos=[velocity * cos(radians(angle)), velocity * sin(radians(angle))])

    @staticmethod
    def calculate_velocity(ball: Ball, other: Ball) -> Vector:
        unit_normal = Vector(start_pos=[ball.x, ball.y], end_pos=[other.x, other.y]).normalize()
        unit_tangent = Vector(end_pos=[-unit_normal.end_pos[1], unit_normal.end_pos[0]])
        return ((unit_normal * ball.vector * (ball.mass - other.mass) + 2 * other.mass * unit_normal * other.vector) / (ball.mass + other.mass)) * unit_normal + unit_tangent * ball.vector * unit_tangent

    def collision(self, other: Ball):
        if dist([self.x, self.y], [other.x, other.y]) < self.radius + other.radius:
            vec1 = self.calculate_velocity(self, other)
            vec2 = self.calculate_velocity(other, self)
            self.vector, other.vector = vec1, vec2

    def update(self):
        if (a := self.x + self.radius > self.window.get_width()) or self.x - self.radius < 0:
            self.vector.end_pos[0] *= -1
            self.x = fabs(a * self.window.get_width() - self.radius)
        if (b := self.y + self.radius > self.window.get_height()) or self.y - self.radius < 0:
            self.vector.end_pos[1] *= -1
            self.y = fabs(b * self.window.get_height() - self.radius)
        self.x += self.vector.end_pos[0]
        self.y += self.vector.end_pos[1]

    def draw(self):
        pygame.draw.circle(self.window, color=self.color, center=(self.x, self.y), radius=self.radius, width=self.width)


@dataclass(slots=True)
class WindowVariables:
    balls: list[Ball]
    pause: tuple[int, int] = (0, 1)
    press_pos: tuple[Union[float, int], Union[float, int]] = (0, 0)
    ball_size: int = 50
    increment: int = 1


class Window(WindowVariables):
    def __init__(self, title: str):
        self.window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        super().__init__(
            balls=[
                Ball(self.window, (500, 500), 50, 0, 0),
                Ball(self.window, (800, 530), 50, 5, 180),
                Ball(self.window, (1500, 500), 50, 0, 0),
                Ball(self.window, (1500, 800), 50, 5, -90)
            ]
        )
        pygame.init()
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def update(self):
        for ball in self.balls:
            if not list(self.pause)[0]:
                ball.update()
            ball.draw()
        [ball.collision(other) for ball, other in combinations(self.balls, 2) if not list(self.pause)[0]]
        self.window.blit(pygame.font.SysFont('arial', 50).render(f'Fps: {str(int(self.clock.get_fps()))}', True, (100, 100, 255)), (20, 20))
        self.window.blit(pygame.font.SysFont('arial', 50).render(f'Size: {str(self.ball_size)}', True, (100, 100, 255)), (20, 100))
        self.window.blit(pygame.font.SysFont('arial', 50).render(f'Parts: {str(len(self.balls))}', True, (100, 100, 255)), (20, 180))
        pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_SPACE:
                    self.pause = self.pause[::-1]
            if event.type == pygame.MOUSEWHEEL:
                self.ball_size = (a if (a := self.ball_size + self.increment) < 300 else 300) if event.y > 0 else (b if (b := self.ball_size - self.increment) > 1 else 1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.press_pos = pygame.mouse.get_pos()
                elif event.button == 3:
                    [self.balls.remove(ball) for ball in filter(lambda ball: dist((ball.x, ball.y), pygame.mouse.get_pos()) < ball.radius, self.balls) if ball in self.balls]
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.balls.append(Ball(self.window, (a := pygame.mouse.get_pos()), self.ball_size, dist([self.press_pos[0], self.press_pos[1]], [a[0], a[1]]) // 20, degrees(atan2((self.press_pos[1] - a[1]), self.press_pos[0] - a[0]))))
        keys = pygame.mouse.get_pressed()
        if keys[0]:
            pygame.draw.line(self.window, (255, 255, 255), self.press_pos, pygame.mouse.get_pos(), width=3)

    def run(self):
        while True:
            self.window.fill((0, 0, 0))
            self.event_handler()
            self.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Window('Pool Game').run()
