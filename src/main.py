from simulator import Simulator, Size
from engine import Engine


def main():
    engine = Engine(size=Size(700, 700), title="Fly Simulator")
    simulator = Simulator(engine)
    simulator.simulate()
    engine.run()


if __name__ == "__main__":
    main()
