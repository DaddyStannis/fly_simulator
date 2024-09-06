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
        super().__init__()

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

    class Event(Enum):
        PRESS = "PRESS"
        RELEASE = "RELEASE"

    def __init__(self, key: str):
        self.key = key
        super().__init__()

    def press(self):
        self._pressed = True
        self.notify(self.Event.PRESS)

    def release(self):
        self._pressed = False
        self.notify(self.Event.RELEASE)

    @property
    def pressed(self):
        return self._pressed


@dataclass
class Gamepad:
    id: int
    left_joystick: Joystick
    right_joystick: Joystick
    cross_btn: Button
    r1_btn: Button


class Object:
    def __init__(self, position: Point, background_color=(255, 0, 0)):
        self.position = position
        self._background_color = background_color

    def place(self, position: Point):
        self.position = position

    def fill(self, rgb: list[int, int, int]):
        self._background_color = rgb


class Figure(Object):
    def __init__(self, size: Size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size
        self._image: pygame.Surface = None

    def load_image(self, imgsrc: str):
        self._image = pygame.transform.scale(
            pygame.image.load(imgsrc), (self.size.width, self.size.height)
        )


class Text(Object):
    def __init__(self, txt: str, *args, color=(0, 0, 0), **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.write(txt)

    def write(self, txt: str):
        self.txt = txt
        font = pygame.font.SysFont("Comic Sans MS", 30)
        self._text_surface = font.render(txt, False, self.color)


class Engine:
    def __init__(self, size: Size, title: str):
        pygame.init()
        pygame.font.init()
        self.done = False
        self._objects: list[Object] = []
        self.gamepads: dict[int, Gamepad] = {}
        self._pygame_joysticks: dict[int, pygame.joystick.Joystick] = {}
        self.screen = Screen(size)
        pygame.display.set_caption(title)
        self.detect_gamepads()

    def run(self, framerate=30):

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
                    self._call_btn_method(event.joy, event.button, "press")

                elif event.type == pygame.JOYBUTTONDOWN:
                    self._call_btn_method(event.joy, event.button, "release")

            self.screen.fill((255, 255, 255))

            for joystick in self._pygame_joysticks.values():
                gamepad = self.gamepads[joystick.get_id()]
                gamepad.left_joystick.move(joystick.get_axis(0), joystick.get_axis(1))
                gamepad.right_joystick.move(joystick.get_axis(3), joystick.get_axis(4))

            for obj in self._objects:
                if isinstance(obj, Text):
                    self.screen._pygame_surface.blit(obj._text_surface, (0, 0))
                else:
                    rect = pygame.draw.rect(
                        self.screen._pygame_surface,
                        obj._background_color,
                        (
                            obj.position.x - obj.size.width / 2,
                            obj.position.y - obj.size.height / 2,
                            obj.size.width,
                            obj.size.height,
                        ),
                    )
                    if obj._image:
                        self.screen._pygame_surface.blit(obj._image, rect.topleft)

            pygame.display.flip()
            clock.tick(framerate)

    def _call_btn_method(self, gamepad_id: int, btn_code: int, method_name: str):
        btn = None
        match btn_code:
            case 0:
                btn = self.gamepads[gamepad_id].cross_btn
            case 5:
                btn = self.gamepads[gamepad_id].r1_btn
        if btn:
            getattr(btn, method_name)()

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
                id, Joystick(0, 0), Joystick(0, 0), Button("cross"), Button("r1")
            )
            self._pygame_joysticks[inst_id] = joystick

    def render(self, obj: Object):
        self._objects.append(obj)
