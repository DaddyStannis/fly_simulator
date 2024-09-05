from engine import Engine, Gamepad, Object, Joystick, Size, Point, Button


class Quadcopter(Object):
    def __init__(self, start_point: Point):
        super().__init__(Size(50, 50), start_point)

    def fly(self, x_acceleration: float, y_acceleration: float):
        self.position.x += x_acceleration
        self.position.y += y_acceleration


class Simulator:
    copter: Quadcopter

    def __init__(self, engine: Engine):
        assert engine.gamepads, "No gamepads found"
        self.engine = engine

    def simulate(self):
        self.gamepad = self.engine.gamepads[0]
        self.copter = Quadcopter(
            Point(self.engine.screen.size.width / 2, self.engine.screen.size.height / 2)
        )
        self.engine.add_object(self.copter)

        self.gamepad.right_joystick.attach(
            self.on_trigger_right_joystick, Joystick.Event.TRIGGER
        )
        self.gamepad.cross_btn.attach(self.on_cross_btn_pressed, Button.Event.PRESS)

    def on_trigger_right_joystick(self):
        x_acceleration = self.gamepad.right_joystick.horizontal_axis
        y_acceleration = self.gamepad.right_joystick.vertical_axis
        self.copter.fly(x_acceleration, y_acceleration)

    def on_cross_btn_pressed(self):
        x = self.engine.screen.size.width / 2
        y = self.engine.screen.size.height / 2
        self.copter.place(Point(x, y))
