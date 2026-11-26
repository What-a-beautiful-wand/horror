from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Room:
    name: str
    walls: tuple
    water: int = 0

    def picture(self, occupied):
        lines = list(self.walls)
        if occupied:
            for row, figure in enumerate((" o ", "/|\\", "/ \\")):
                lines[row] = lines[row][:3] + figure + lines[row][6:]
        for row in range(len(lines) - self.water, len(lines)):
            lines[row] = "~" * len(lines[row])
        return lines


@dataclass
class Monster:
    # Путь к источнику шума: коллектор без камеры -> галерея -> насосная.
    route: tuple = ("00", "01", "02")
    step: int = 0

    @property
    def room_id(self):
        return self.route[self.step]

    def hear_pump(self):
        self.step = min(self.step + 1, len(self.route) - 1)


def make_rooms():
    return {
        "01": Room("ГАЛЕРЕЯ", ("|            |", "|   [====]   |",
                               "|   /    \\   |", "|  /      \\  |")),
        "02": Room("НАСОСНАЯ", ("        o H   ", "       /|\\H   ",
                                "       / \\H   ", "          H   "), water=1),
    }


@dataclass
class Station:
    rooms: dict = field(default_factory=make_rooms)
    monster: Monster = field(default_factory=Monster)
    seconds: int = 0
    pump_on: bool = False

    def advance(self):
        self.seconds += 10
        room = self.rooms["02"]
        room.water = max(0, min(len(room.walls), room.water + (-1 if self.pump_on else 1)))
        if self.pump_on:
            self.monster.hear_pump()

    def forecast(self):
        future = deepcopy(self)
        for _ in range(6):
            future.advance()
        return future
