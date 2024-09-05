import pygame
from dataclasses import dataclass
from enum import Enum
from utils import Observable


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Size:
    width: float
    height: float


class Screen:
    def __init__(self, size: Size):
        self._pygame_surface = pygame.display.set_mode((size.width, size.height))
        self.size = size
        self.fill()

    def fill(self, background=(255, 255, 255)):
        self._pygame_surface.fill(background)


class Joystick(Observable):

    class Event(Enum):
        TRIGGER = "TRIGGER"

    def __init__(self, horizontal_axis: float, vertical_axis: float):
        self._horizontal_axis = horizontal_axis
        self._vertical_axis = vertical_axis

    @property
    def horizontal_axis(self):
        return self._horizontal_axis

    @property
    def vertical_axis(self):
        return self._vertical_axis

    def move(self, horizontal_axis: float, vertical_axis: float):
        self._horizontal_axis = horizontal_axis
        self._vertical_axis = vertical_axis
        self.notify(self.Event.TRIGGER)


class Button(Observable):
    _pressed: bool = False

    def __init__(self, key: str):
        self.key = key

    class Event(Enum):
        PRESS = "PRESS"
        RELEASE = "RELEASE"

    def press(self):
        self._pressed = True
        self.notify(self.Event.PRESS)

    def release(self):
        self._pressed = False
        self.notify(self.Event.RELEASE)

    @property
    def pressed(self):
        return self._pressed


class Gamepad:
    def __init__(
        self,
        id: int,
        left_joystick: Joystick,
        right_joystick: Joystick,
        cross_btn: Button,
    ):
        self.id = id
        self.left_joystick = left_joystick
        self.right_joystick = right_joystick
        self.cross_btn = cross_btn


class Object:
    color = (255, 0, 0)

    def __init__(self, size: Size, position: Point):
        self.size = size
        self.position = position

    def place(self, position: Point):
        self.position = position


class Engine:
    done: bool
    objects: list[Object] = []
    _pygame_rects: dict[Object, pygame.Rect] = {}
    gamepads: dict[int, Gamepad] = {}
    _pygame_joysticks: dict[int, pygame.joystick.Joystick] = {}

    def __init__(self, size: Size, title: str):
        self.screen = Screen(size)
        pygame.display.set_caption(title)
        self.detect_gamepads()

    def run(self, framerate=30):
        pygame.init()
        self.done = False
        self._eventloop(framerate)
        pygame.quit()

    def _eventloop(self, framerate: int):
        clock = pygame.time.Clock()

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

                elif event.type == pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                    joystick_id = joystick.get_id()
                    self._pygame_joysticks[joystick_id] = joystick
                    print(f"Gamepad {joystick_id} connected.")

                elif event.type == pygame.JOYDEVICEREMOVED:
                    joystick_id = event.instance_id
                    if joystick_id in self._pygame_joysticks:
                        del self._pygame_joysticks[joystick_id]
                        print(f"Gamepad {joystick_id} disconnected.")

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.gamepads[event.joy].cross_btn.press()

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.gamepads[event.joy].cross_btn.release()

            self.screen.fill((255, 255, 255))

            for joystick in self._pygame_joysticks.values():
                gamepad = self.gamepads[joystick.get_id()]
                gamepad.left_joystick.move(joystick.get_axis(0), joystick.get_axis(1))
                gamepad.right_joystick.move(joystick.get_axis(3), joystick.get_axis(4))

            for obj in self.objects:
                self._pygame_rects[obj].x = obj.position.x
                self._pygame_rects[obj].y = obj.position.y
                self._draw_object(obj)

            pygame.display.flip()
            clock.tick(framerate)

    def quit(self):
        self.done = True

    def detect_gamepads(self):
        pygame.joystick.init()

        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            id = joystick.get_id()
            inst_id = joystick.get_instance_id()
            self.gamepads[id] = Gamepad(
                id, Joystick(0, 0), Joystick(0, 0), Button("cross")
            )
            self._pygame_joysticks[inst_id] = joystick

    def add_object(self, obj: Object):
        self.objects.append(obj)
        self._draw_object(obj)

    def _draw_object(self, obj: Object):
        self._pygame_rects[obj] = pygame.draw.rect(
            self.screen._pygame_surface,
            obj.color,
            (
                obj.position.x - obj.size.width / 2,
                obj.position.y - obj.size.height / 2,
                obj.size.width,
                obj.size.height,
            ),
        )
