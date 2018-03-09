import textwrap


import libtcodpy as tcod


from map import MAX_MAP_WIDTH, MAX_MAP_HEIGHT
from messages import MessageLog


SCREEN_WIDTH = 135
SCREEN_HEIGHT = 50

console = None
popup = None


def init_ui():
    global console
    tcod.console_set_custom_font('data/terminal10x16_gs_tc.png', tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'libtcod tutorial revisited', False)
    console = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    popup = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    message_log = MessageLog(MAX_MAP_WIDTH, SCREEN_HEIGHT - MAX_MAP_HEIGHT - 1)
    return message_log, tcod.Key(), tcod.Mouse()


def render_map(con, map_knowledge, los_map):
    for x in range(map_knowledge.width):
        for y in range(map_knowledge.height):
            display = map_knowledge.display_char((x, y), los_map)
            tcod.console_set_default_foreground(con, display.color)
            tcod.console_put_char(con, x, y, display.char, tcod.BKGND_NONE)


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    old_bg = tcod.console_get_default_background(panel)
    old_fg = tcod.console_get_default_foreground(panel)

    label = '{}: {}/{} '.format(name, value, maximum)
    tcod.console_print(panel, x, y, label)
    x += len(label)
    total_width -= len(label)

    bar_width = int(value / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SET)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SET)

    tcod.console_set_default_foreground(panel, tcod.white)

    tcod.console_set_default_background(panel, old_bg)
    tcod.console_set_default_foreground(panel, old_fg)


def render_ui(con, player, message_log):
    tcod.console_set_default_foreground(con, tcod.white)
    render_bar(con, MAX_MAP_WIDTH + 1, 2, SCREEN_WIDTH - MAX_MAP_WIDTH - 2, 'HP', player.hp, player.max_hp,
               tcod.dark_green, tcod.red)
    tcod.console_hline(con, 0, MAX_MAP_HEIGHT, MAX_MAP_WIDTH)
    tcod.console_vline(con, MAX_MAP_WIDTH, 0, tcod.console_get_height(con))
    row = 0
    for message in message_log.messages:
        tcod.console_print(con, 0, MAX_MAP_HEIGHT + 1 + row, message)
        row += 1
    row = 0
    tcod.console_print(con, MAX_MAP_WIDTH + 1, 5, 'Inventory:')
    for item in player.inventory:
        tcod.console_print(con, MAX_MAP_WIDTH + 2, row + 6, chr(ord('a') + row) + ' - ' + item.kind)
        row += 1


def render_all(map_knowledge, los_map, player, message_log):
    global console
    tcod.console_clear(console)

    render_map(console, map_knowledge, los_map)
    render_ui(console, player, message_log)

    tcod.console_blit(console, 0, 0, tcod.console_get_width(console), tcod.console_get_height(console), 0, 0, 0)
    tcod.console_flush()


def show_popup(text, title):
    global popup
    lines = [string for line in text.split('\n') for string in textwrap.wrap(line, width=MAX_MAP_WIDTH-4)]
    width = max(len(string) for string in lines) + 4  # 1 space on each side, plus 1 line for the square on each side
    width = max(width, len(title))
    height = len(lines) + 4  # ditto
    x = (MAX_MAP_WIDTH - width) // 2
    y = (MAX_MAP_HEIGHT - height) // 2
    tcod.console_print_frame(popup, x, y, width, height, fmt=title)
    row = 0
    for line in lines:
        tcod.console_print(popup, x + 2, y + 2 + row, line)
        row += 1
    tcod.console_blit(popup, 0, 0, tcod.console_get_width(popup), tcod.console_get_height(popup), 0, 0, 0)
    tcod.console_flush()
    key = tcod.console_wait_for_keypress(True)

    # destroy the popup
    tcod.console_blit(console, 0, 0, tcod.console_get_width(console), tcod.console_get_height(console), 0, 0, 0)
    tcod.console_flush()
    return key
