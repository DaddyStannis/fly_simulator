import time
from engine import Engine, Gamepad, Figure, Joystick, Size, Point, Button, Text
from utils import Observable, segment_length
from enum import Enum


class Bird(Figure):
    def __init__(self, start_point: Point):
        super().__init__(Size(50, 50), start_point)

    def fly(self, delta_x: float, delta_y: float):
        self.position.x += delta_x
        self.position.y += delta_y


class Counter(Text, Observable):
    class Event(Enum):
        START = "START"
        FINISH = "FINISH"

    def __init__(self, engine: Engine, labels: list[str], *args, **kwargs):
        super().__init__(labels[0], *args, **kwargs, color=(0, 0, 255))
        Observable.__init__(self)
        self.engine = engine
        self.labels = labels
        self.count = 1
        self.start_time = time.time()

    def start(self):
        self.count = 1
        self.start_time = time.time()
        self.engine.render(self)
        self.engine.add_task(self._tick)
        self.notify(self.Event.START)

    def _tick(self):
        if time.time() >= self.start_time + self.count:
            if self.count == len(self.labels):
                self.engine.erase(self)
                self.engine.rm_task(self._tick)
                self.notify(self.Event.FINISH)
            else:
                self.write(self.labels[self.count])
                self.count += 1


class Simulator:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.gamepad = None
        self.bird = None
        self.header = None
        self._paused = False
        self.center = (
            self.engine.screen.size.width / 2,
            self.engine.screen.size.height / 2,
        )

    def start(self):
        assert self.engine.gamepads, "No gamepads found"
        self.gamepad = self.engine.gamepads[0]

        self.mark = Figure(
            Size(50, 50), Point(self.center[0], self.center[1]), (255, 255, 255)
        )
        self.mark.load_image("./src/images/cross.svg")
        self.engine.render(self.mark)

        self.bird = Bird(Point(self.center[0], self.center[1]))
        self.engine.render(self.bird)

        self.gamepad.r1_btn.attach(self._on_r1_btn_pressed, Button.Event.PRESS)

    def _restart(self):
        self.gamepad.right_joystick.attach(
            self._on_trigger_right_joystick, Joystick.Event.TRIGGER
        )
        self.gamepad.cross_btn.attach(self._on_cross_btn_pressed, Button.Event.PRESS)
        countdown = Counter(
            self.engine,
            [str(i + 1) for i in reversed(range((6)))],
            Point(self.engine.screen.size.width - 20, 20),
        )
        countdown.attach(self._stop, Counter.Event.FINISH)
        countdown.start()

    def _stop(self):
        self.gamepad.right_joystick.detach(
            self._on_trigger_right_joystick, Joystick.Event.TRIGGER
        )
        self.gamepad.cross_btn.detach(self._on_cross_btn_pressed, Button.Event.PRESS)
        self.gamepad.r1_btn.attach(self._on_r1_btn_pressed, Button.Event.PRESS)

        distance = segment_length(
            self.center[0], self.center[1], self.bird.position.x, self.bird.position.y
        )
        self.header = Text(f"Distance: {distance:.2f}", Point(120, 20), fontsize=40)
        self.engine.render(self.header)

    def _pause(self):
        self._paused = True

    def _resume(self):
        self._paused = False

    def _on_trigger_right_joystick(self):
        delta_x = self.gamepad.right_joystick.horizontal_axis
        delta_y = self.gamepad.right_joystick.vertical_axis
        self.bird.fly(delta_x, delta_y)

    def _on_cross_btn_pressed(self):
        x = self.engine.screen.size.width / 2
        y = self.engine.screen.size.height / 2
        self.bird.place(Point(x, y))

    def _on_r1_btn_pressed(self):
        labels = ("3", "2", "1", "GO")
        center_point = Point(self.center[0], self.center[1])
        countdown = Counter(self.engine, labels, center_point, fontsize=120)
        countdown.attach(self._restart, Counter.Event.FINISH)
        countdown.start()
        self.gamepad.r1_btn.detach(self._on_r1_btn_pressed, Button.Event.PRESS)
        self.engine.erase(self.header)
        self.bird.place(Point(self.center[0], self.center[1]))
