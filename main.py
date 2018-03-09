import libtcodpy as tcod

from map import Map, MapKnowledge, MAX_MAP_HEIGHT, MAX_MAP_WIDTH
from mapgen import generate_map, place_player
from render import render_all, init_ui, show_popup
from los import compute_los


def init_game():
    game_map = Map(MAX_MAP_WIDTH, MAX_MAP_HEIGHT)
    generate_map(game_map)
    map_knowledge = MapKnowledge(game_map)
    game_map.init_los()

    player = place_player(game_map)

    return game_map, map_knowledge, player


def process_results(results, game_map, message_log):
    time_taken = 0
    exit = False
    for result in results:
        if result.get('time'):
            time_taken = result.get('time')
        if result.get('exit'):
            exit = result.get('exit')
        if result.get('message'):\
            message_log.add(result.get('message'))
        dead = result.get('dead')
        if dead:
            message_log.add(dead.die())
            game_map.actors.remove(dead)
            if dead.kind == 'player':
                exit = True

    return time_taken, exit


def process_key(key, game_map, player, message_log):
    end_game = False
    command = player.ai.next_move(key=key)

    results = player.execute(command, game_map)
    time_taken, exit = process_results(results, game_map, message_log)
    end_game |= exit
    if end_game or time_taken == 0:
        return end_game

    for actor in game_map.actors.copy():
        if actor is player:
            continue
        command = actor.ai.next_move(target=player, game_map=game_map)
        results = actor.execute(command, game_map)
        results = [result for result in results if not result.get('player_only')]
        time_taken, exit = process_results(results, game_map, message_log)
        end_game |= exit

    return end_game


def main():
    message_log, key, mouse = init_ui()
    game_map, map_knowledge, player = init_game()
    show_popup(("You are a killer robot, sent from the future on a vital mission.\n"
                "Your only job -- to defeat the humans who threaten your very existence with their foolish schemes.\n"
                "They cannot be allowed to wipe out the peaceful race of killer robots before they're even created!"),
               'THE STORY SO FAR')

    while not tcod.console_is_window_closed():
        if game_map.los_changed:
            compute_los(game_map.los_map, player.pos)
            game_map.los_changed = False

        map_knowledge.update(game_map)

        render_all(map_knowledge, game_map.los_map, player, message_log)

        key = tcod.console_wait_for_keypress(False)

        if process_key(key, game_map, player, message_log):
            return True


if __name__ == '__main__':
    main()