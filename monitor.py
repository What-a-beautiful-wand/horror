"""ASCII-интерфейс. Все координаты измеряются в ячейках терминала."""
import shutil


class Canvas:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.cells = [[" "] * width for _ in range(height)]

    def put(self, x, y, text):
        if 0 <= y < self.h:
            left, right = max(0, x), min(self.w, x + len(text))
            if left < right:
                self.cells[y][left:right] = text[left - x:right - x]

    def line(self, x1, y1, x2, y2, char):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            self.put(round(x1 + (x2 - x1) * i / steps),
                     round(y1 + (y2 - y1) * i / steps), char)

    def box(self, x, y, w, h):
        edge = "+" + "-" * (w - 2) + "+"
        self.put(x, y, edge)
        for row in range(y + 1, y + h - 1):
            self.put(x, row, "|")
            self.put(x + w - 1, row, "|")
        self.put(x, y + h - 1, edge)

    def sprite(self, x, y, lines):
        for i, line in enumerate(lines):
            self.put(x, y + i, line)

    def rows(self):
        return ["".join(row) for row in self.cells]


def gallery(c):
    # Все рёбра тоннеля сходятся к двери на дальней стене.
    w, h = c.w, c.h
    vx, vy = w * 3 // 5, h // 2
    for x, y, char in [(0, 0, "\\"), (w-1, 0, "/"),
                       (0, h-1, "/"), (w-1, h-1, "\\")]:
        c.line(x, y, vx, vy, char)
    for depth in (.12, .43, .64, .79):
        left, right = int(vx * depth), int(w - (w - vx) * depth) - 1
        top, bottom = int(vy * depth), int(h - (h - vy) * depth) - 1
        c.box(left, top, right-left+1, bottom-top+1)
        c.put(left + 1, top + 1, ".")
        c.put(right - 1, bottom - 1, ".")
    door_w, door_h = max(5, w // 10), max(4, h // 4)
    dx, dy = vx - door_w//2, vy - door_h//2
    for y in range(dy, dy + door_h):
        c.put(dx, y, " " * door_w)
    c.box(dx, dy, door_w, door_h)
    c.put(dx+1, dy+1, "01")
    c.put(dx+door_w-2, dy+door_h-2, "o")
    for x in (w//4, 3*w//4):
        c.line(x, h-1, vx, dy+door_h, "/" if x < vx else "\\")
    c.put(w//2-4, 1, "[=======]")
    if h >= 15:
        x, y = max(1,w//12), h//2-2
        c.sprite(x, y, ["+------+", "|//////|", "|//////|", "+------+"])
        c.put(w*4//5, h//2, "[ -> ]")


def pump_room(c, pump_on):
    w, h = c.w, c.h
    deck = h * 3 // 4
    rail = max(2, deck - max(3, h//6))
    pipe = max(1, h//8)
    c.put(0, pipe, "=" * (w//2) + "||")
    c.put(0, pipe+1, "-" * (w//2) + "||")
    for x in range(3, w//2, max(7, w//10)):
        c.put(x, pipe, "][")
        c.put(x, pipe+1, "][")
    c.line(w//2, pipe+2, w//2, deck-1, "|")
    c.line(w//2+1, pipe+2, w//2+1, deck-1, "|")
    c.put(0, deck, "=" * w)
    for x in range(2, w, max(6, w//12)):
        c.put(x, deck, "[:]")
        c.line(x, rail, x, deck-1, "|")
    c.put(0, rail, "-" * w)
    # Рёбра охлаждения и привод занимают часть площадки при любом масштабе.
    motor_w = max(12, w//4)
    motor_h = max(3, h//6)
    mx, my = w//7, deck-motor_h
    for y in range(my, deck):
        c.put(mx, y, " " * motor_w)
    c.box(mx, my, motor_w, motor_h)
    for y in range(my+1, deck-1):
        c.put(mx+1, y, ("|:" * motor_w)[:motor_w-2])
    bearing = "( X )" if pump_on else "( O )"
    c.put(mx+motor_w//2-2, my+motor_h//2, bearing)
    c.put(mx+motor_w, my+motor_h//2, "]==")
    for foot in (mx+2, mx+motor_w-4):
        c.put(foot, deck, "[_]")
    lx = 3*w//4
    for y in range(1, h):
        c.put(lx, y, "|---|" if y % 2 == 0 else "|   |")
    c.sprite(lx-3, max(0,rail-3), [" o ", "/|\\", "/ \\"])
    if h >= 15:
        c.sprite(w//8, pipe+3, ["+-------+", "| P-02  |", "| [o] : |", "+-------+"])


def scene(station, camera, w, h):
    room = station.rooms[camera]
    c = Canvas(w, h)
    if w < 30 or h < 9:
        c.sprite((w-14)//2, max(0,(h-4)//2), room.picture(station.monster.room_id == camera))
        return c.rows()
    if camera == "01":
        gallery(c)
    else:
        pump_room(c, station.pump_on)
    if station.monster.room_id == camera:
        c.sprite(w//3, h*3//4-3, [" .-. ", " (:) ", "/| |\\", " / \\ "])
    if room.water:
        surface = h - max(1, h * room.water // 5)
        for y in range(surface, h):
            wave = "~.-~" if y == surface else "  ~.      "
            offset = (station.seconds//10 + y) % len(wave)
            c.put(0, y, (wave * (w//len(wave)+2))[offset:offset+w])
    return c.rows()


def clock(seconds):
    return f"{seconds // 60:02}:{seconds % 60:02}"


def window(screen, x, y, w, h, station, camera, title):
    screen.box(x, y, w, h)
    screen.put(x+2, y, (" " + title + " ")[:w-4])
    screen.sprite(x+1, y+1, scene(station, camera, w-2, h-2))


def draw_monitor(station, camera, forecast, message):
    cols, rows = shutil.get_terminal_size()
    # Свободные строка и колонка исключают автоперенос и прокрутку при вводе.
    w, h = max(1, cols-1), max(1, rows-1)
    screen = Canvas(w, h)
    screen.box(0, 0, w, h)
    area_h = h-9
    if w >= 40 and area_h >= 6:
        screen.put(2, 1, "ПОСТ 04  /  " + ("ВИДЕОНАБЛЮДЕНИЕ" if camera else "РАБОЧИЙ СТОЛ"))
        screen.put(w-9, 1, clock(station.seconds))
        if camera:
            view = station.forecast() if forecast else station
            mode = "ПРОГНОЗ +60 с" if forecast else "ЭФИР"
            title = f"CAM {camera} / {view.rooms[camera].name} / {mode}  {clock(view.seconds)}"
            window(screen, 2, 3, w-4, area_h, view, camera, title)
        elif w >= 78:
            pane = (w-6)//2
            for x, size, key in [(2, pane, "1"), (pane+4, w-pane-6, "2")]:
                cam = "0" + key
                window(screen, x, 3, size, area_h, station, cam,
                       f"[{key}] {station.rooms[cam].name} / ЭФИР")
        else:
            upper = area_h//2
            for y, height, key in [(3, upper, "1"), (3+upper, area_h-upper, "2")]:
                cam = "0"+key
                window(screen, 2, y, w-4, height, station, cam, f"[{key}] {station.rooms[cam].name}")
        pump = "ВКЛ" if station.pump_on else "ВЫКЛ"
        screen.put(2, h-6, f"[н] Насос {pump}    Вода {station.rooms['02'].water}/4")
        screen.put(2, h-5, "1/2 камеры   с стол   ф эфир/прогноз")
        screen.put(2, h-4, "х ход +10 с   в выход")
    else:
        screen.put(2, 1, "Увеличь окно терминала")
    screen.put(2, h-3, message[:max(0,w-4)])
    screen.put(1, h-2, " > ")
    print("\n".join(screen.rows()))
