# index.py
# The main file from which to run the program

from manager import SimulationManager


def main():
    manager = SimulationManager()
    manager.start_sim()


if __name__ == "__main__":
    main()
