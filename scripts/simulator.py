from engine import Engine, Gamepad, Object, Joystick, Size, Point


class Hero(Object):
    def __init__(self, start_point: Point):
        super().__init__(Size(50, 50), start_point)

    def move(self, x_acceleration: float, y_acceleration: float):
        self.position.x += x_acceleration
        self.position.y += y_acceleration


class Simulator:
    hero: Hero

    def __init__(self, engine: Engine):
        assert engine.gamepads, "No gamepads found"
        self.engine = engine

    def simulate(self):
        self.gamepad = self.engine.gamepads[0]
        self.hero = Hero(
            Point(self.engine.screen.size.width / 2, self.engine.screen.size.height / 2)
        )
        self.engine.add_object(self.hero)

        self.gamepad.right_joystick.attach(
            self.on_trigger_right_joystick, Joystick.Event.TRIGGER
        )

    def on_trigger_right_joystick(self):
        self.hero.move(
            self.gamepad.right_joystick.horizontal_axis,
            self.gamepad.right_joystick.vertical_axis,
        )
