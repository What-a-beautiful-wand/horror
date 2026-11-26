import os
import sys

from station import Station
from monitor import draw_monitor


def clear_screen():
    if sys.stdout.isatty():
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="", flush=True)


def main():
    station = Station()
    camera = None
    forecast = False
    message = ""
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if interactive and os.name == "nt":
        os.system("")  # Включает ANSI-позиционирование в консоли Windows.
    clear_screen()
    while True:
        draw_monitor(station, camera, forecast, message)
        try:
            # Возвращаем курсор в поле ввода над нижней границей экрана.
            command = input("\033[2A\r\033[4C" if interactive else "").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        clear_screen()
        message = ""
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
            message = "Неизвестная команда."


if __name__ == "__main__":
    main()
