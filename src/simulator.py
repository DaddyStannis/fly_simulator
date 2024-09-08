import time
from engine import Engine, Gamepad, Figure, Joystick, Size, Point, Button, Text
from utils import call_until


class Bird(Figure):
    def __init__(self, start_point: Point):
        super().__init__(Size(50, 50), start_point)

    def fly(self, delta_x: float, delta_y: float):
        self.position.x += delta_x
        self.position.y += delta_y


class Counter(Text):
    def __init__(self, engine: Engine, labels: list[str], *args, **kwargs):
        super().__init__(labels[0], *args, **kwargs)
        self.engine = engine
        self.labels = labels
        self.count = 1
        self.start_time = time.time()

    def start(self):
        self.count = 1
        self.start_time = time.time()
        self.engine.render(self)
        self.engine.add_task(self._tick)

    def _tick(self):
        if time.time() >= self.start_time + self.count:
            if self.count == len(self.labels):
                self.engine.erase(self)
            else:
                self.write(self.labels[self.count])
                self.count += 1


class Simulator:
    def __init__(self, engine: Engine):
        assert engine.gamepads, "No gamepads found"
        self.engine = engine
        self.bird = None

    def simulate(self):
        self.gamepad = self.engine.gamepads[0]
        self.center = (
            self.engine.screen.size.width / 2,
            self.engine.screen.size.height / 2,
        )

        self.mark = Figure(
            Size(50, 50), Point(self.center[0], self.center[1]), (255, 255, 255)
        )
        self.mark.load_image("./src/images/cross.svg")
        self.engine.render(self.mark)

        self.bird = Bird(Point(self.center[0], self.center[1]))
        self.engine.render(self.bird)

        self.header = Text("Distance:", Point(0, 0))
        self.engine.render(self.header)

        self.gamepad.right_joystick.attach(
            self.on_trigger_right_joystick, Joystick.Event.TRIGGER
        )
        self.gamepad.cross_btn.attach(self.on_cross_btn_pressed, Button.Event.PRESS)
        self.gamepad.r1_btn.attach(self.on_r1_btn_pressed, Button.Event.PRESS)

        # def pause_and_self_destruct():
        #     self.engine.pause()
        #     self.engine.rm_task(pause_and_self_destruct)

        # self.engine.add_task(pause_and_self_destruct)

    def on_trigger_right_joystick(self):
        delta_x = self.gamepad.right_joystick.horizontal_axis
        delta_y = self.gamepad.right_joystick.vertical_axis
        self.bird.fly(delta_x, delta_y)

    def on_cross_btn_pressed(self):
        x = self.engine.screen.size.width / 2
        y = self.engine.screen.size.height / 2
        self.bird.place(Point(x, y))

    def on_r1_btn_pressed(self):
        labels = ("3", "2", "1", "GO")
        center_point = Point(self.center[0], self.center[1])
        countdown = Counter(self.engine, labels, center_point, fontsize=120)
        countdown.start()
