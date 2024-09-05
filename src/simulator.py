from engine import Engine, Gamepad, Object, Joystick, Size, Point, Button


class Quadcopter(Object):
    def __init__(self, start_point: Point):
        super().__init__(Size(50, 50), start_point)

    def fly(self, delta_x: float, delta_y: float):
        self.position.x += delta_x
        self.position.y += delta_y


class Simulator:
    copter: Quadcopter

    def __init__(self, engine: Engine):
        assert engine.gamepads, "No gamepads found"
        self.engine = engine

    def simulate(self):
        self.gamepad = self.engine.gamepads[0]
        center = self.engine.screen.size.width / 2, self.engine.screen.size.height / 2

        self.mark = Object(Size(50, 50), Point(center[0], center[1]))
        self.mark.load_image("./src/images/cross.svg")
        self.mark.fill((255, 255, 255))
        self.engine.add_object(self.mark)

        self.copter = Quadcopter(Point(center[0], center[1]))
        self.engine.add_object(self.copter)

        self.gamepad.right_joystick.attach(
            self.on_trigger_right_joystick, Joystick.Event.TRIGGER
        )
        self.gamepad.cross_btn.attach(self.on_cross_btn_pressed, Button.Event.PRESS)

    def on_trigger_right_joystick(self):
        delta_x = self.gamepad.right_joystick.horizontal_axis
        delta_y = self.gamepad.right_joystick.vertical_axis
        self.copter.fly(delta_x, delta_y)

    def on_cross_btn_pressed(self):
        x = self.engine.screen.size.width / 2
        y = self.engine.screen.size.height / 2
        self.copter.place(Point(x, y))
