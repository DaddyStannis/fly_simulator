from simulator import Simulator, Object, Size, Point, Joystick
from engine import Engine


def on_move():
    print("move")


def main():
    engine = Engine(size=Size(700, 700), title="Pizza Delivery Simulator")
    simulator = Simulator(engine)
    simulator.simulate()
    engine.run()


if __name__ == "__main__":
    main()
