import os
import sys

from station import Station


def clear_screen():
    if sys.stdout.isatty():
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="", flush=True)


def draw_desk(station):
    clock = f"{station.seconds // 60:02}:{station.seconds % 60:02}"
    pump = "ВКЛ" if station.pump_on else "ВЫКЛ"
    screen = [
        f"ПОСТ 04                  {clock}",
        "------------------------------",
        " [1] ГАЛЕРЕЯ    [2] НАСОСНАЯ",
        "",
        f" НАСОС {pump:<4}     ВОДА {station.rooms['02'].water}/4",
    ]
    print("       __             ______________________________________")
    print("      /  \\           /  .--------------------------------.  \\")
    print("     /____\\        |   |                                |   |")
    lamp = ["       ||", "       ||", "       ||", "       ||", "     __||__"]
    for arm, line in zip(lamp, screen):
        print(f"{arm:<19}|   | {line:<30} |   |")
    print("    /______\\       |   '--------------------------------'   |")
    print("                   |    :: :: ::               [o]   ( O )  |")
    print("   ________________'---------------------------------------'__")
    print("  /      .----.                  |______|                     /|")
    print(" /       |    |)     .--------------------------------.      / |")
    print("/        '----'     / [][][][][][][][][][][][][][][] /      /  |")
    print("-------------------/__________[________]___________/-------'   |")
    print("|   |                                                  |   |")


def draw_camera(station, camera, forecast):
    view = station.forecast() if forecast else station
    room = view.rooms[camera]
    mode = "ПРОГНОЗ +60 с" if forecast else "ЭФИР"
    print(f"CAM {camera} / {room.name} / {mode} / {view.seconds // 60:02}:{view.seconds % 60:02}")
    border = "+" + "-" * len(room.walls[0]) + "+"
    print(border)
    for row in room.picture(view.monster.room_id == camera):
        print("|" + row + "|")
    print(border)
    print("Насос:", "работает" if station.pump_on else "выключен")


def main():
    station = Station()
    camera = None
    forecast = False
    while True:
        if camera is None:
            draw_desk(station)
        else:
            draw_camera(station, camera, forecast)
        print("1/2 — камеры   с — стол   ф — эфир/прогноз")
        print("н — насос      х — ход (+10 с)   в — выход")
        try:
            command = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        clear_screen()
        if command == "в":
            break
        elif command in ("1", "2"):
            camera = "0" + command
        elif command == "с":
            camera, forecast = None, False
        elif command == "ф":
            camera = camera or "02"
            forecast = not forecast
        elif command == "н":
            station.pump_on = not station.pump_on
        elif command == "х":
            station.advance()
        else:
            print("Неизвестная команда. Выбери клавишу из подсказки.")


if __name__ == "__main__":
    main()
